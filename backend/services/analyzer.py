"""Funnel analyzer service for processing and analyzing marketing funnels."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import Analysis, AnalysisPage, User
from ..models.schemas import AnalysisResponse
from ..services.screenshot import get_screenshot_service
from ..services.llm_provider import get_llm_provider
from ..services.storage import get_storage_service
from ..services.scraper import scrape_funnel
from ..utils.config import settings

logger = logging.getLogger(__name__)


async def analyze_funnel(
    urls: List[str],
    session: AsyncSession,
    user_id: Optional[int] = None,
    recipient_email: Optional[str] = None,
) -> AnalysisResponse:
    """Generate analysis results, persist them, and return a response payload."""
    
    start_time = time.time()
    perf_start = time.perf_counter()
    
    # Step 1: Scrape all pages
    logger.info(f"Starting analysis for {len(urls)} URLs")
    scrape_start = time.perf_counter()
    page_contents = await scrape_funnel(urls)
    scrape_duration = time.perf_counter() - scrape_start
    
    # Step 2: Capture screenshots (best effort) and analyze each page with OpenAI
    llm_provider = get_llm_provider()
    page_analyses = []
    screenshot_service = None
    storage_service = get_storage_service()

    try:
        screenshot_service = await get_screenshot_service()
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
        screenshot_base64 = None
        screenshot_timeout_seconds = 8
        screenshot_task: asyncio.Task[str | None] | None = None
        screenshot_captured = False
        screenshot_uploaded = False
        screenshot_asset = None

        if screenshot_service:
            screenshot_metrics["attempted"] += 1
            capture_timer_start = time.perf_counter()
            screenshot_task = asyncio.create_task(
                screenshot_service.capture_screenshot(
                    page_content.url,
                    viewport_width=1440,
                    viewport_height=900,
                    full_page=False,
                )
            )

            try:
                screenshot_base64 = await asyncio.wait_for(
                    asyncio.shield(screenshot_task),
                    timeout=screenshot_timeout_seconds,
                )
                screenshot_captured = bool(screenshot_base64)
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
                screenshot_task = None
            finally:
                screenshot_time_total += time.perf_counter() - capture_timer_start
                if screenshot_task and screenshot_task.done():
                    try:
                        screenshot_base64 = screenshot_task.result()
                        screenshot_captured = screenshot_captured or bool(screenshot_base64)
                    except Exception as capture_error:  # noqa: BLE001
                        logger.warning(
                            "Screenshot task error for %s: %s",
                            page_content.url,
                            capture_error,
                        )
                        screenshot_task = None

        llm_timer_start = time.perf_counter()
        analysis_result = await llm_provider.analyze_page(
            page_content,
            page_number=i + 1,
            total_pages=len(urls),
            screenshot_base64=screenshot_base64,
        )
        llm_duration_total += time.perf_counter() - llm_timer_start

        screenshot_url = None
        if screenshot_base64 and storage_service:
            try:
                screenshot_asset = await storage_service.upload_base64_image(
                    base64_data=screenshot_base64,
                    content_type="image/png",
                )
                if screenshot_asset:
                    screenshot_url = screenshot_asset.url
                    screenshot_uploaded = True
            except Exception as upload_error:  # noqa: BLE001 - log and continue
                logger.warning(
                    "Failed to upload screenshot for %s: %s",
                    page_content.url,
                    upload_error,
                )
        elif screenshot_task and storage_service:
            deferred_capture_start = time.perf_counter()
            try:
                captured = await screenshot_task
                if captured:
                    screenshot_captured = True
                    screenshot_asset = await storage_service.upload_base64_image(
                        base64_data=captured,
                        content_type="image/png",
                    )
                    if screenshot_asset:
                        screenshot_url = screenshot_asset.url
                        screenshot_uploaded = True
            except asyncio.CancelledError:
                pass
            except Exception as late_capture_error:  # noqa: BLE001
                logger.warning(
                    "Deferred screenshot handling failed for %s: %s",
                    page_content.url,
                    late_capture_error,
                )
            finally:
                screenshot_time_total += time.perf_counter() - deferred_capture_start

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
        })
    
    # Step 3: Calculate overall scores
    all_scores = {"clarity": [], "value": [], "proof": [], "design": [], "flow": []}
    for page_analysis in page_analyses:
        for key in all_scores:
            all_scores[key].append(page_analysis["scores"][key])
    
    avg_scores = {key: sum(values) // len(values) for key, values in all_scores.items()}
    overall_score = sum(avg_scores.values()) // len(avg_scores)
    
    # Step 4: Generate executive summary
    summary = await llm_provider.analyze_funnel_summary(page_analyses, overall_score)
    
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
