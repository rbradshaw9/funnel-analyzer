"""Funnel analyzer service for processing and analyzing marketing funnels."""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import Analysis, AnalysisPage, User
from ..models.schemas import AnalysisResponse
from ..services.openai_service import get_openai_service
from ..services.scraper import scrape_funnel
from ..utils.config import settings

logger = logging.getLogger(__name__)


async def analyze_funnel(urls: List[str], session: AsyncSession, user_id: Optional[int] = None) -> AnalysisResponse:
    """Generate analysis results, persist them, and return a response payload."""
    
    start_time = time.time()
    
    # Step 1: Scrape all pages
    logger.info(f"Starting analysis for {len(urls)} URLs")
    page_contents = await scrape_funnel(urls)
    
    # Step 2: Analyze each page with OpenAI
    openai_service = get_openai_service()
    page_analyses = []
    
    for i, page_content in enumerate(page_contents):
        analysis_result = await openai_service.analyze_page(
            page_content, page_number=i + 1, total_pages=len(urls)
        )
        page_analyses.append({
            "url": page_content.url,
            "title": page_content.title,
            "page_type": analysis_result.get("page_type", "unknown"),
            "scores": analysis_result["scores"],
            "feedback": analysis_result["feedback"],
        })
    
    # Step 3: Calculate overall scores
    all_scores = {"clarity": [], "value": [], "proof": [], "design": [], "flow": []}
    for page_analysis in page_analyses:
        for key in all_scores:
            all_scores[key].append(page_analysis["scores"][key])
    
    avg_scores = {key: sum(values) // len(values) for key, values in all_scores.items()}
    overall_score = sum(avg_scores.values()) // len(avg_scores)
    
    # Step 4: Generate executive summary
    summary = await openai_service.analyze_funnel_summary(page_analyses, overall_score)
    
    duration = int(time.time() - start_time)
    logger.info(f"Analysis completed in {duration}s with overall score: {overall_score}")
    
    # Step 5: Persist to database
    resolved_user_id = await _resolve_user_id(session, user_id)
    
    analysis_result = {
        "urls": urls,
        "scores": avg_scores,
        "overall_score": overall_score,
        "summary": summary,
        "pages": page_analyses,
        "analysis_duration_seconds": duration,
    }

    analysis = Analysis(
        user_id=resolved_user_id,
        urls=analysis_result["urls"],
        scores=analysis_result["scores"],
        overall_score=analysis_result["overall_score"],
        summary=analysis_result["summary"],
        detailed_feedback=analysis_result["pages"],
        analysis_duration_seconds=analysis_result.get("analysis_duration_seconds"),
    )

    analysis.pages = [
        AnalysisPage(
            url=page["url"],
            page_type=page.get("page_type"),
            title=page.get("title"),
            screenshot_url=page.get("screenshot_url"),
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
        "pages": [
            {
                "url": page.url,
                "page_type": page.page_type,
                "title": page.title,
                "scores": page.page_scores,
                "feedback": page.page_feedback,
                "screenshot_url": page.screenshot_url,
            }
            for page in analysis.pages
        ],
        "created_at": analysis.created_at,
        "analysis_duration_seconds": analysis.analysis_duration_seconds,
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
