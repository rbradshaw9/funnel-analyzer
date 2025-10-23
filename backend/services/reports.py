"""Reports service for retrieving persisted analyses."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.database import Analysis
from ..services.storage import get_storage_service


logger = logging.getLogger(__name__)


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
                if "screenshot_storage_key" not in page_data:
                    try:
                        page_data["screenshot_storage_key"] = analysis.pages[idx].screenshot_storage_key
                    except IndexError:
                        page_data["screenshot_storage_key"] = None
    else:
        stored_pages = [
            {
                "url": page.url,
                "page_type": page.page_type,
                "title": page.title,
                "scores": page.page_scores,
                "feedback": page.page_feedback,
                "screenshot_url": page.screenshot_url,
                "screenshot_storage_key": page.screenshot_storage_key,
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
        "pipeline_metrics": analysis.pipeline_metrics,
    }


async def delete_report(
    session: AsyncSession,
    analysis_id: int,
    *,
    user_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Delete an analysis and remove any stored assets.

    Returns a dictionary with cleanup statistics when the analysis exists,
    otherwise ``None`` if the record could not be found (or does not belong
    to the requesting user).
    """

    stmt = select(Analysis).options(selectinload(Analysis.pages)).where(Analysis.id == analysis_id)
    if user_id is not None:
        stmt = stmt.where(Analysis.user_id == user_id)

    result = await session.execute(stmt)
    analysis = result.scalar_one_or_none()

    if analysis is None:
        return None

    keys: list[str] = []
    for page in analysis.pages:
        if page.screenshot_storage_key:
            keys.append(page.screenshot_storage_key)

    detailed = analysis.detailed_feedback
    if isinstance(detailed, list):
        for item in detailed:
            if isinstance(item, dict):
                key = item.get("screenshot_storage_key")
                if key:
                    keys.append(key)

    # Preserve insertion order while removing duplicates
    seen: dict[str, None] = {}
    for key in keys:
        seen.setdefault(key, None)
    unique_keys = list(seen.keys())

    storage = get_storage_service()
    stats: Dict[str, Any] = {
        "analysis_id": analysis.id,
        "assets_total": len(unique_keys),
        "assets_deleted": 0,
        "assets_failed": 0,
        "assets_skipped": 0,
        "storage_available": storage is not None,
    }

    if storage is None:
        stats["assets_skipped"] = len(unique_keys)
    else:
        for key in unique_keys:
            try:
                deleted = await storage.delete_object(key)
            except Exception as exc:  # noqa: BLE001
                stats["assets_failed"] += 1
                logger.error("Failed to delete asset %s during report cleanup: %s", key, exc)
                continue

            if deleted:
                stats["assets_deleted"] += 1
            else:
                stats["assets_failed"] += 1

    await session.delete(analysis)
    await session.commit()

    return stats
