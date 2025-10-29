"""
Screenshot Cleanup Service

Automatically deletes screenshots from S3 when:
1. Analysis is deleted
2. User account is deleted (cascades to all analyses)
3. Free trial expires without conversion
4. Analysis older than retention period for inactive users
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.database import User, FunnelAnalysis, PageAnalysis
from .storage import StorageService

logger = logging.getLogger(__name__)


class ScreenshotCleanupService:
    """Manages screenshot lifecycle and cleanup from S3"""
    
    def __init__(self, storage_service: Optional[StorageService] = None):
        self.storage = storage_service
        
    async def cleanup_analysis_screenshots(
        self, 
        db: Session, 
        analysis_id: int
    ) -> int:
        """
        Delete all screenshots associated with an analysis
        
        Args:
            db: Database session
            analysis_id: ID of analysis to clean up
            
        Returns:
            Number of screenshots deleted
        """
        if not self.storage:
            logger.warning("No storage service configured - cannot delete screenshots")
            return 0
            
        # Get all page analyses for this funnel analysis
        page_analyses = db.query(PageAnalysis).filter(
            PageAnalysis.funnel_analysis_id == analysis_id,
            PageAnalysis.screenshot_storage_key.isnot(None)
        ).all()
        
        deleted_count = 0
        for page in page_analyses:
            try:
                # Delete from S3
                success = await self.storage.delete_object(page.screenshot_storage_key)
                if success:
                    deleted_count += 1
                    logger.info(f"Deleted screenshot: {page.screenshot_storage_key}")
                    
                # Clear database references
                page.screenshot_url = None
                page.screenshot_storage_key = None
                
            except Exception as e:
                logger.error(f"Failed to delete screenshot {page.screenshot_storage_key}: {e}")
                
        db.commit()
        return deleted_count
        
    async def cleanup_user_screenshots(
        self, 
        db: Session, 
        user_id: int
    ) -> int:
        """
        Delete all screenshots for a user (all their analyses)
        
        Args:
            db: Database session
            user_id: ID of user whose screenshots to delete
            
        Returns:
            Total number of screenshots deleted
        """
        # Get all analyses for this user
        analyses = db.query(FunnelAnalysis).filter(
            FunnelAnalysis.user_id == user_id
        ).all()
        
        total_deleted = 0
        for analysis in analyses:
            deleted = await self.cleanup_analysis_screenshots(db, analysis.id)
            total_deleted += deleted
            
        logger.info(f"Deleted {total_deleted} screenshots for user {user_id}")
        return total_deleted
        
    async def cleanup_expired_free_trials(
        self, 
        db: Session,
        trial_days: int = 14
    ) -> int:
        """
        Delete screenshots from free trials that expired without converting
        
        Args:
            db: Database session
            trial_days: Number of days before considering trial expired
            
        Returns:
            Number of screenshots deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=trial_days)
        
        # Find free users with old analyses who never upgraded
        expired_analyses = db.query(FunnelAnalysis).join(User).filter(
            User.plan == "free",
            FunnelAnalysis.created_at < cutoff_date
        ).all()
        
        total_deleted = 0
        for analysis in expired_analyses:
            deleted = await self.cleanup_analysis_screenshots(db, analysis.id)
            total_deleted += deleted
            
        logger.info(f"Cleaned up {total_deleted} screenshots from {len(expired_analyses)} expired free trials")
        return total_deleted
        
    async def cleanup_inactive_user_screenshots(
        self, 
        db: Session,
        inactive_days: int = 90,
        keep_recent_days: int = 30
    ) -> int:
        """
        Delete old screenshots for inactive users
        Keep recent screenshots, delete older ones
        
        Args:
            db: Database session
            inactive_days: Days since last login to consider inactive
            keep_recent_days: Keep screenshots from last N days even for inactive users
            
        Returns:
            Number of screenshots deleted
        """
        inactive_cutoff = datetime.utcnow() - timedelta(days=inactive_days)
        screenshot_cutoff = datetime.utcnow() - timedelta(days=keep_recent_days)
        
        # Find inactive users
        inactive_users = db.query(User).filter(
            User.last_login_at < inactive_cutoff
        ).all()
        
        total_deleted = 0
        for user in inactive_users:
            # Get old analyses for this inactive user
            old_analyses = db.query(FunnelAnalysis).filter(
                FunnelAnalysis.user_id == user.id,
                FunnelAnalysis.created_at < screenshot_cutoff
            ).all()
            
            for analysis in old_analyses:
                deleted = await self.cleanup_analysis_screenshots(db, analysis.id)
                total_deleted += deleted
                
        logger.info(
            f"Cleaned up {total_deleted} old screenshots from {len(inactive_users)} inactive users"
        )
        return total_deleted
        
    async def get_storage_stats(self, db: Session) -> dict:
        """Get statistics about screenshot storage usage"""
        
        total_screenshots = db.query(PageAnalysis).filter(
            PageAnalysis.screenshot_storage_key.isnot(None)
        ).count()
        
        # Screenshots by plan
        from sqlalchemy import func
        by_plan = db.query(
            User.plan,
            func.count(PageAnalysis.id).label('count')
        ).join(FunnelAnalysis).join(User).filter(
            PageAnalysis.screenshot_storage_key.isnot(None)
        ).group_by(User.plan).all()
        
        # Old screenshots (>90 days)
        old_cutoff = datetime.utcnow() - timedelta(days=90)
        old_screenshots = db.query(PageAnalysis).join(FunnelAnalysis).filter(
            PageAnalysis.screenshot_storage_key.isnot(None),
            FunnelAnalysis.created_at < old_cutoff
        ).count()
        
        return {
            "total_screenshots": total_screenshots,
            "by_plan": {plan: count for plan, count in by_plan},
            "old_screenshots_90_days": old_screenshots,
            "estimated_storage_mb": total_screenshots * 0.5  # Rough estimate: 500KB per screenshot
        }
