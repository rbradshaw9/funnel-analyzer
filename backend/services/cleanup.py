"""Maintenance helpers for pruning stale assets and housekeeping tasks."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import Analysis, AnalysisPage, User
from ..utils.config import settings
from .storage import get_storage_service

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def cleanup_ephemeral_screenshots(
    session: AsyncSession,
    *,
    retention_days: int = 7,
    dry_run: bool = True,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Remove screenshots for anonymous/free analyses older than the retention window.

    Screenshots are deleted when:
      • The owning analysis is older than ``retention_days``.
      • The user is the default anonymous user OR currently on the free plan.

    Returns stats describing how many assets were inspected/deleted.
    """

    storage = get_storage_service()
    if storage is None:
        logger.info("Storage service unavailable; skipping screenshot cleanup")
        return {
            "inspected": 0,
            "eligible": 0,
            "deleted": 0,
            "skipped": 0,
            "dry_run": dry_run,
        }

    current_time = now or _now_utc()
    cutoff = current_time - timedelta(days=retention_days)

    stmt = (
        select(AnalysisPage, Analysis, User)
        .join(Analysis, AnalysisPage.analysis_id == Analysis.id)
        .join(User, Analysis.user_id == User.id)
        .where(
            AnalysisPage.screenshot_storage_key.is_not(None),
            Analysis.created_at <= cutoff,
            or_(
                User.email == settings.DEFAULT_USER_EMAIL,
                User.plan == "free",
            ),
        )
    )

    result = await session.execute(stmt)
    rows: List[tuple[AnalysisPage, Analysis, User]] = result.all()

    stats = {
        "inspected": len(rows),
        "eligible": len(rows),
        "deleted": 0,
        "skipped": 0,
        "dry_run": dry_run,
    }

    if not rows:
        return stats

    analyses_to_update: Dict[int, Analysis] = {}
    deleted_keys: set[str] = set()

    for page, analysis, user in rows:
        key = page.screenshot_storage_key
        if not key:
            stats["skipped"] += 1
            continue

        logger.info(
            "Cleanup candidate: analysis_id=%s page_id=%s key=%s user=%s plan=%s created=%s",
            analysis.id,
            page.id,
            key,
            user.email,
            user.plan,
            analysis.created_at,
        )

        if dry_run:
            continue

        deleted = await storage.delete_object(key)
        if not deleted:
            stats["skipped"] += 1
            continue

        page.screenshot_storage_key = None
        page.screenshot_url = None
        stats["deleted"] += 1
        analyses_to_update[analysis.id] = analysis
        deleted_keys.add(key)

    if not dry_run and analyses_to_update:
        for analysis in analyses_to_update.values():
            details = analysis.detailed_feedback
            if not isinstance(details, list):
                continue
            changed = False
            for item in details:
                if not isinstance(item, dict):
                    continue
                key = item.get("screenshot_storage_key")
                if key and key in deleted_keys:
                    item["screenshot_storage_key"] = None
                    item["screenshot_url"] = None
                    changed = True
            if changed:
                analysis.detailed_feedback = details

        await session.commit()

    return stats
