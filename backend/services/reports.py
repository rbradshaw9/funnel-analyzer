"""Reports service for retrieving persisted analyses."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.database import Analysis


async def get_user_reports(
    session: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """Return paginated analyses for a given user."""

    total_stmt = select(func.count()).select_from(Analysis).where(Analysis.user_id == user_id)
    total = await session.scalar(total_stmt) or 0

    if total == 0:
        return {"reports": [], "total": 0}

    stmt = (
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    analyses = result.scalars().all()

    reports = [
        {
            "analysis_id": analysis.id,
            "overall_score": analysis.overall_score,
            "urls": analysis.urls,
            "created_at": analysis.created_at,
        }
        for analysis in analyses
    ]

    return {"reports": reports, "total": total}


async def get_report_by_id(
    session: AsyncSession,
    analysis_id: int,
    user_id: Optional[int] = None,
) -> Optional[dict]:
    """Retrieve a single analysis with its detail pages."""

    stmt = select(Analysis).options(selectinload(Analysis.pages)).where(Analysis.id == analysis_id)

    if user_id is not None:
        stmt = stmt.where(Analysis.user_id == user_id)

    result = await session.execute(stmt)
    analysis = result.scalar_one_or_none()

    if analysis is None:
        return None

    stored_pages = analysis.detailed_feedback or []

    if stored_pages:
        # Ensure screenshot URLs from relational table are merged in if missing
        for idx, page_data in enumerate(stored_pages):
            if isinstance(page_data, dict):
                if "screenshot_url" not in page_data:
                    try:
                        page_data["screenshot_url"] = analysis.pages[idx].screenshot_url
                    except IndexError:
                        page_data["screenshot_url"] = None
    else:
        stored_pages = [
            {
                "url": page.url,
                "page_type": page.page_type,
                "title": page.title,
                "scores": page.page_scores,
                "feedback": page.page_feedback,
                "screenshot_url": page.screenshot_url,
            }
            for page in analysis.pages
        ]

    return {
        "analysis_id": analysis.id,
        "overall_score": analysis.overall_score,
        "scores": analysis.scores,
        "summary": analysis.summary,
        "pages": stored_pages,
        "created_at": analysis.created_at,
        "analysis_duration_seconds": analysis.analysis_duration_seconds,
        "recipient_email": analysis.recipient_email,
    }
