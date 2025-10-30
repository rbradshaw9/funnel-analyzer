"""Funnel analyzer service for processing and analyzing marketing funnels."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any, List, Optional

import httpx

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import Analysis, AnalysisPage, User
from ..models.schemas import AnalysisResponse
from ..services.screenshot import get_screenshot_service
from ..services.llm_provider import get_llm_provider
from ..services.storage import get_storage_service
from ..services.scraper import scrape_funnel
from ..services.progress_tracker import get_progress_tracker
from ..services.performance_analyzer import get_performance_analyzer
from ..services.source_analyzer import get_source_analyzer
from ..utils.config import settings

logger = logging.getLogger(__name__)

_VALIDATION_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FunnelAnalyzer/1.0; +https://funnelanalyzer.pro)",
}
_VALIDATION_TIMEOUT = httpx.Timeout(8.0, connect=5.0)


async def _validate_single_url(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Check that a URL is reachable before attempting screenshots or AI analysis."""

    head_error: Optional[str] = None
    try:
        response = await client.head(url, headers=_VALIDATION_HEADERS)
    except Exception as exc:  # noqa: BLE001 - network failures vary widely
        head_error = str(exc).strip() or None
        response = None

    if response and 200 <= response.status_code < 400:
        return None

    if response and response.status_code not in {405, 501}:
        head_error = f"HTTP {response.status_code}"

    try:
        response = await client.get(url, headers=_VALIDATION_HEADERS)
    except Exception as exc:  # noqa: BLE001 - capture networking errors
        message = head_error or (str(exc).strip() or "request failed")
        return message

    if 200 <= response.status_code < 400:
        return None

    return f"HTTP {response.status_code}"


async def _validate_urls_or_raise(urls: List[str]) -> None:
    """Ensure all URLs respond successfully before running the heavy analysis pipeline."""

    if not urls:
        raise ValueError("At least one URL is required")

    async with httpx.AsyncClient(follow_redirects=True, timeout=_VALIDATION_TIMEOUT) as client:
        results = await asyncio.gather(*(_validate_single_url(client, url) for url in urls))

    failures = []
    for url, failure in zip(urls, results):
        if failure:
            logger.warning("URL validation failed for %s: %s", url, failure)
            failures.append(f"{url} ({failure})")

    if failures:
        details = "; ".join(failures)
        raise ValueError(f"Some URLs could not be reached: {details}")


async def analyze_funnel(
    urls: List[str],
    session: AsyncSession,
    user_id: Optional[int] = None,
    recipient_email: Optional[str] = None,
    analysis_id: Optional[str] = None,
    industry: Optional[str] = None,
    name: Optional[str] = None,
    parent_analysis_id: Optional[int] = None,
) -> AnalysisResponse:
    """Generate analysis results, persist them, and return a response payload."""
    
    # Generate or use provided analysis ID for progress tracking
    if not analysis_id:
        analysis_id = str(uuid.uuid4())
    
    progress = get_progress_tracker()
    total_pages = len(urls)
    
    start_time = time.time()
    perf_start = time.perf_counter()
    
    await _validate_urls_or_raise(urls)
    
    # Report: Starting
    await progress.update(
        analysis_id=analysis_id,
        stage="validation",
        progress_percent=5,
        message="Validating URLs and checking accessibility…",
        total_pages=total_pages,
    )

    # Step 1: Scrape all pages
    logger.info(f"Starting analysis for {len(urls)} URLs (ID: {analysis_id})")
    await progress.update(
        analysis_id=analysis_id,
        stage="scraping",
        progress_percent=10,
        message=f"Extracting content from {total_pages} page{'s' if total_pages > 1 else ''}…",
        total_pages=total_pages,
    )
    
    scrape_start = time.perf_counter()
    page_contents = await scrape_funnel(urls)
    scrape_duration = time.perf_counter() - scrape_start
    
    await progress.update(
        analysis_id=analysis_id,
        stage="screenshots",
        progress_percent=20,
        message="Capturing screenshots and analyzing visual elements…",
        total_pages=total_pages,
    )
    
    # Step 2: Initialize analysis services
    llm_provider = get_llm_provider()
    performance_analyzer = get_performance_analyzer(api_key=settings.GOOGLE_PAGESPEED_API_KEY)
    source_analyzer = get_source_analyzer()
    page_analyses = []
    screenshot_service = None
    storage_service = get_storage_service()
    
    if not storage_service:
        logger.warning(
            "⚠️  S3 storage not configured - screenshots will NOT be saved or displayed. "
            "Set AWS_S3_BUCKET, AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY in Railway."
        )
    else:
        logger.info("✓ S3 storage configured - screenshots will be uploaded")

    try:
        screenshot_service = await get_screenshot_service()
        logger.info("✓ Screenshot service (Playwright) initialized successfully")
    except Exception as screenshot_error:
        logger.warning(f"Screenshot service unavailable, continuing without visuals: {screenshot_error}")
    
    screenshot_metrics = {
        "attempted": 0,
        "succeeded": 0,
        "failed": 0,
        "uploaded": 0,
        "timeouts": 0,
    }
    screenshot_time_total = 0.0
    llm_duration_total = 0.0
    telemetry_notes: list[str] = []
    if not screenshot_service:
        telemetry_notes.append("screenshot_service_unavailable")
    if not (settings.OPENAI_API_KEY or "").strip():
        telemetry_notes.append("llm_placeholder_mode")
    if not storage_service:
        telemetry_notes.append("storage_service_unconfigured")

    def _ensure_list(value: Any) -> list:
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _ensure_dict(value: Any) -> Optional[dict]:
        return value if isinstance(value, dict) else None

    def _dict_list(value: Any) -> list:
        items = _ensure_list(value)
        return [item for item in items if isinstance(item, dict)]

    def _string_list(value: Any) -> list[str]:
        items = _ensure_list(value)
        return [str(item) for item in items if isinstance(item, (str, int, float))]

    for i, page_content in enumerate(page_contents):
        current_page = i + 1
        
        # Update progress for each page
        # Screenshots: 20-40%, Analysis: 40-85%
        screenshot_progress = 20 + (current_page - 1) * (20 / total_pages)
        
        # Get page URL for display
        page_url = page_content.url
        # Shorten URL for display (remove protocol and www, truncate if needed)
        display_url = page_url.replace('https://', '').replace('http://', '').replace('www.', '')
        if len(display_url) > 50:
            display_url = display_url[:47] + '...'
        
        await progress.update(
            analysis_id=analysis_id,
            stage="screenshots",
            progress_percent=int(screenshot_progress),
            message=f"Page {current_page}/{total_pages}: Capturing screenshot from {display_url}",
            current_page=current_page,
            total_pages=total_pages,
        )
        
        screenshot_base64 = None
        visual_elements = None  # Will store extracted CTAs, images, etc.
        screenshot_timeout_seconds = 15  # Increased from 8s to accommodate Framer Motion animations
        screenshot_task: asyncio.Task[str | None] | None = None
        screenshot_captured = False
        screenshot_uploaded = False
        screenshot_asset = None

        if screenshot_service:
            screenshot_metrics["attempted"] += 1
            capture_timer_start = time.perf_counter()
            
            # Use analyze_above_fold to get both screenshot AND visual element data
            try:
                above_fold_task = asyncio.create_task(
                    screenshot_service.analyze_above_fold(page_content.url)
                )
                above_fold_data = await asyncio.wait_for(
                    asyncio.shield(above_fold_task),
                    timeout=screenshot_timeout_seconds,
                )
                
                if above_fold_data:
                    screenshot_base64 = above_fold_data.get("screenshot")
                    visual_elements = above_fold_data.get("visual_elements")
                    screenshot_captured = bool(screenshot_base64)
                    
                    if visual_elements:
                        logger.info(
                            f"Extracted {len(visual_elements.get('buttons', []))} CTAs from {page_content.url}"
                        )
                        
            except asyncio.TimeoutError:
                logger.info(
                    "Screenshot exceeded %ss for %s; continuing without blocking analysis",
                    screenshot_timeout_seconds,
                    page_content.url,
                )
                screenshot_metrics["timeouts"] += 1
            except Exception as screenshot_error:  # noqa: BLE001
                logger.warning(
                    "Failed to capture screenshot for %s: %s",
                    page_content.url,
                    screenshot_error,
                )
            finally:
                screenshot_time_total += time.perf_counter() - capture_timer_start

        # Step: Performance analysis (if API key available)
        performance_data = None
        if performance_analyzer and settings.GOOGLE_PAGESPEED_API_KEY:
            try:
                perf_progress = 35 + (current_page - 1) * (10 / total_pages)
                await progress.update(
                    analysis_id=analysis_id,
                    stage="performance_analysis",
                    progress_percent=int(perf_progress),
                    message=f"Page {current_page}/{total_pages}: Analyzing page speed for {display_url}",
                    current_page=current_page,
                    total_pages=total_pages,
                )
                performance_data = await performance_analyzer.analyze_performance(page_content.url)
                logger.info(f"Performance analysis complete for {page_content.url}")
            except Exception as perf_error:
                logger.warning(f"Performance analysis failed for {page_content.url}: {perf_error}")
        
        # Step: Source code analysis
        source_data = None
        if source_analyzer and page_content.raw_html:
            try:
                source_progress = 38 + (current_page - 1) * (7 / total_pages)
                await progress.update(
                    analysis_id=analysis_id,
                    stage="source_analysis",
                    progress_percent=int(source_progress),
                    message=f"Page {current_page}/{total_pages}: Analyzing technical SEO for {display_url}",
                    current_page=current_page,
                    total_pages=total_pages,
                )
                source_data = await source_analyzer.analyze_source(
                    page_content.raw_html, 
                    page_content.url
                )
                logger.info(f"Source code analysis complete for {page_content.url}")
            except Exception as source_error:
                logger.warning(f"Source analysis failed for {page_content.url}: {source_error}")

        # Update progress for AI analysis
        ai_progress = 45 + (current_page - 1) * (35 / total_pages)
        await progress.update(
            analysis_id=analysis_id,
            stage="ai_analysis",
            progress_percent=int(ai_progress),
            message=f"Page {current_page}/{total_pages}: AI analyzing {display_url} for insights…",
            current_page=current_page,
            total_pages=total_pages,
        )

        llm_timer_start = time.perf_counter()
        analysis_result = await llm_provider.analyze_page(
            page_content,
            page_number=i + 1,
            total_pages=len(urls),
            screenshot_base64=screenshot_base64,
            visual_elements=visual_elements,  # Pass extracted visual data to LLM
            industry=industry,  # Pass industry for tailored recommendations
        )
        llm_duration_total += time.perf_counter() - llm_timer_start

        screenshot_url = None
        screenshot_asset = None
        if screenshot_base64 and storage_service:
            try:
                screenshot_asset = await storage_service.upload_base64_image(
                    base64_data=screenshot_base64,
                    content_type="image/png",
                )
                if screenshot_asset:
                    screenshot_url = screenshot_asset.url
                    screenshot_uploaded = True
                    logger.info(
                        f"✓ Screenshot uploaded for {page_content.url}: {screenshot_url}"
                    )
                    # Also log the first few characters to verify it's a valid URL
                    logger.info(f"Screenshot URL preview: {screenshot_url[:100]}...")
            except Exception as upload_error:  # noqa: BLE001 - log and continue
                logger.warning(
                    "Failed to upload screenshot for %s: %s",
                    page_content.url,
                    upload_error,
                )
        elif not storage_service:
            logger.warning(f"No storage service available for screenshot upload: {page_content.url}")
        elif not screenshot_base64:
            logger.warning(f"No screenshot data captured for: {page_content.url}")

        if screenshot_service:
            if screenshot_captured:
                screenshot_metrics["succeeded"] += 1
            else:
                screenshot_metrics["failed"] += 1
            if screenshot_uploaded:
                screenshot_metrics["uploaded"] += 1

        page_analyses.append({
            "url": page_content.url,
            "title": page_content.title,
            "page_type": analysis_result.get("page_type", "unknown"),
            "scores": analysis_result["scores"],
            "feedback": analysis_result["feedback"],
            # Enhanced recommendations
            "headline_recommendation": analysis_result.get("headline_recommendation"),
            "cta_recommendations": _dict_list(analysis_result.get("cta_recommendations")),
            "design_improvements": _dict_list(analysis_result.get("design_improvements")),
            "trust_elements_missing": _dict_list(analysis_result.get("trust_elements_missing")),
            "ab_test_priority": _ensure_dict(analysis_result.get("ab_test_priority")),
            "priority_alerts": _dict_list(analysis_result.get("priority_alerts")),
            "funnel_flow_gaps": _dict_list(analysis_result.get("funnel_flow_gaps")),
            "copy_diagnostics": _ensure_dict(analysis_result.get("copy_diagnostics")),
            "visual_diagnostics": _ensure_dict(analysis_result.get("visual_diagnostics")),
            "video_recommendations": _dict_list(analysis_result.get("video_recommendations")),
            "email_capture_recommendations": _string_list(analysis_result.get("email_capture_recommendations")),
            "screenshot_url": screenshot_url,
            "screenshot_storage_key": getattr(screenshot_asset, "key", None),
            # New technical analysis data
            "performance_data": performance_data,
            "source_analysis": source_data,
        })
    
    # Step 3: Calculate overall scores
    await progress.update(
        analysis_id=analysis_id,
        stage="scoring",
        progress_percent=85,
        message="Calculating conversion scores and performance metrics…",
        total_pages=total_pages,
    )
    
    all_scores = {"clarity": [], "value": [], "proof": [], "design": [], "flow": []}
    for page_analysis in page_analyses:
        for key in all_scores:
            all_scores[key].append(page_analysis["scores"][key])
    
    avg_scores = {key: sum(values) // len(values) for key, values in all_scores.items()}
    overall_score = sum(avg_scores.values()) // len(avg_scores)
    
    # Step 4: Generate executive summary
    await progress.update(
        analysis_id=analysis_id,
        stage="executive_summary",
        progress_percent=90,
        message="Creating executive summary with strategic recommendations…",
        total_pages=total_pages,
    )
    
    summary = await llm_provider.analyze_funnel_summary(page_analyses, overall_score, industry)
    
    # Update progress after summary completes
    await progress.update(
        analysis_id=analysis_id,
        stage="saving",
        progress_percent=93,
        message="Saving analysis results to database…",
        total_pages=total_pages,
    )
    
    duration = int(time.time() - start_time)
    total_perf_duration = time.perf_counter() - perf_start

    pipeline_metrics = {
        "stage_timings": {
            "scrape_seconds": round(scrape_duration, 3),
            "analysis_seconds": round(llm_duration_total, 3),
            "screenshot_seconds": round(screenshot_time_total, 3) if screenshot_service else None,
            "total_seconds": round(total_perf_duration, 3),
        },
        "screenshot": screenshot_metrics if screenshot_service else None,
        "llm_provider": settings.LLM_PROVIDER,
        "notes": telemetry_notes or None,
    }

    logger.info(
        "Analysis completed in %ss with overall score %s", duration, overall_score
    )
    logger.debug("Analysis telemetry: %s", pipeline_metrics)
    
    # Step 5: Persist to database
    resolved_user_id = await _resolve_user_id(session, user_id)
    
    analysis_result = {
        "urls": urls,
        "scores": avg_scores,
        "overall_score": overall_score,
        "summary": summary,
        "pages": page_analyses,
        "analysis_duration_seconds": duration,
        "recipient_email": recipient_email,
        "pipeline_metrics": pipeline_metrics,
    }

    analysis = Analysis(
        user_id=resolved_user_id,
        urls=analysis_result["urls"],
        scores=analysis_result["scores"],
        overall_score=analysis_result["overall_score"],
        summary=analysis_result["summary"],
        detailed_feedback=analysis_result["pages"],
        pipeline_metrics=pipeline_metrics,
        analysis_duration_seconds=analysis_result.get("analysis_duration_seconds"),
        recipient_email=recipient_email,
        name=name,
        parent_analysis_id=parent_analysis_id,
    )

    analysis.pages = [
        AnalysisPage(
            url=page["url"],
            page_type=page.get("page_type"),
            title=page.get("title"),
            screenshot_url=page.get("screenshot_url"),
            screenshot_storage_key=page.get("screenshot_storage_key"),
            page_scores=page["scores"],
            page_feedback=page["feedback"],
        )
        for page in analysis_result["pages"]
    ]

    session.add(analysis)
    await session.flush()
    await session.commit()
    await session.refresh(analysis, attribute_names=["pages"])
    
    # Step 5: Finalize and save results
    await progress.update(
        analysis_id=analysis_id,
        stage="finalizing",
        progress_percent=95,
        message="Saving analysis results and preparing report…",
        total_pages=total_pages,
    )

    # Mark as complete
    await progress.update(
        analysis_id=analysis_id,
        stage="complete",
        progress_percent=100,
        message="Professional funnel analysis complete - ready to view!",
        total_pages=total_pages,
    )

    response_payload = {
        "analysis_id": analysis.id,
        "overall_score": analysis.overall_score,
        "scores": analysis.scores,
        "summary": analysis.summary,
        "pages": analysis_result["pages"],
        "created_at": analysis.created_at,
        "analysis_duration_seconds": analysis.analysis_duration_seconds,
        "recipient_email": recipient_email,
        "pipeline_metrics": pipeline_metrics,
    }

    return AnalysisResponse.model_validate(response_payload)


async def _resolve_user_id(session: AsyncSession, provided_user_id: Optional[int]) -> int:
    """Return the user ID to use for the analysis, creating the default user if necessary."""

    if provided_user_id is not None:
        return provided_user_id

    query = select(User).where(User.email == settings.DEFAULT_USER_EMAIL)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=settings.DEFAULT_USER_EMAIL,
            full_name=settings.DEFAULT_USER_NAME,
            is_active=1,
        )
        session.add(user)
        await session.flush()

    return user.id
