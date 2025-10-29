"""Admin endpoints for screenshot cleanup and maintenance."""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..db.session import get_db_session
from ..models.database import User
from ..services.auth import validate_jwt_token
from ..services.screenshot_cleanup import ScreenshotCleanupService
from ..services.storage import get_storage_service

router = APIRouter()
logger = logging.getLogger(__name__)


class CleanupStats(BaseModel):
    screenshots_deleted: int
    message: str


class StorageStats(BaseModel):
    total_screenshots: int
    by_plan: dict[str, int]
    old_screenshots_90_days: int
    estimated_storage_mb: float


async def require_admin(
    authorization: str = Depends(lambda authorization: authorization),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Dependency to require admin authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    payload = validate_jwt_token(token)
    
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await session.get(User, payload["user_id"])
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user


@router.post("/cleanup/expired-trials", response_model=CleanupStats)
async def cleanup_expired_trials(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """
    Clean up screenshots from free trials that expired without converting.
    Default: 14 days
    """
    storage_service = get_storage_service()
    if not storage_service:
        raise HTTPException(status_code=503, detail="Storage service not configured")
    
    cleanup_service = ScreenshotCleanupService(storage_service)
    deleted_count = await cleanup_service.cleanup_expired_free_trials(session, trial_days=14)
    
    logger.info(f"Admin {admin.email} triggered expired trial cleanup: {deleted_count} screenshots deleted")
    
    return CleanupStats(
        screenshots_deleted=deleted_count,
        message=f"Cleaned up {deleted_count} screenshots from expired free trials"
    )


@router.post("/cleanup/inactive-users", response_model=CleanupStats)
async def cleanup_inactive_users(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """
    Clean up old screenshots from inactive users.
    - Inactive: No login for 90+ days
    - Keeps screenshots from last 30 days
    """
    storage_service = get_storage_service()
    if not storage_service:
        raise HTTPException(status_code=503, detail="Storage service not configured")
    
    cleanup_service = ScreenshotCleanupService(storage_service)
    deleted_count = await cleanup_service.cleanup_inactive_user_screenshots(
        session,
        inactive_days=90,
        keep_recent_days=30
    )
    
    logger.info(f"Admin {admin.email} triggered inactive user cleanup: {deleted_count} screenshots deleted")
    
    return CleanupStats(
        screenshots_deleted=deleted_count,
        message=f"Cleaned up {deleted_count} old screenshots from inactive users"
    )


@router.get("/storage/stats", response_model=StorageStats)
async def get_storage_stats(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Get statistics about screenshot storage usage."""
    storage_service = get_storage_service()
    if not storage_service:
        raise HTTPException(status_code=503, detail="Storage service not configured")
    
    cleanup_service = ScreenshotCleanupService(storage_service)
    stats = await cleanup_service.get_storage_stats(session)
    
    return StorageStats(**stats)
