"""Progress tracking for long-running analysis operations."""

from typing import Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class ProgressUpdate:
    """Represents a progress update for an analysis."""
    analysis_id: str
    stage: str  # 'scraping', 'screenshot', 'analysis', 'summary', 'complete'
    progress_percent: int  # 0-100
    message: str
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class ProgressTracker:
    """
    In-memory progress tracker for analysis operations.
    
    Stores progress updates that can be polled by the frontend.
    Updates expire after 10 minutes to prevent memory bloat.
    """
    
    def __init__(self):
        self._progress: Dict[str, ProgressUpdate] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    async def update(
        self,
        analysis_id: str,
        stage: str,
        progress_percent: int,
        message: str,
        current_page: Optional[int] = None,
        total_pages: Optional[int] = None,
    ):
        """Update progress for an analysis."""
        if analysis_id not in self._locks:
            self._locks[analysis_id] = asyncio.Lock()
        
        async with self._locks[analysis_id]:
            self._progress[analysis_id] = ProgressUpdate(
                analysis_id=analysis_id,
                stage=stage,
                progress_percent=min(100, max(0, progress_percent)),
                message=message,
                current_page=current_page,
                total_pages=total_pages,
            )
    
    async def get(self, analysis_id: str) -> Optional[Dict]:
        """Get current progress for an analysis."""
        if analysis_id not in self._progress:
            return None
        
        if analysis_id in self._locks:
            async with self._locks[analysis_id]:
                progress = self._progress.get(analysis_id)
                return asdict(progress) if progress else None
        
        progress = self._progress.get(analysis_id)
        return asdict(progress) if progress else None
    
    async def remove(self, analysis_id: str):
        """Remove progress tracking for an analysis."""
        if analysis_id in self._progress:
            del self._progress[analysis_id]
        if analysis_id in self._locks:
            del self._locks[analysis_id]
    
    async def cleanup_old_entries(self, max_age_minutes: int = 10):
        """Remove entries older than max_age_minutes."""
        from datetime import timedelta
        
        now = datetime.now(timezone.utc)
        to_remove = []
        
        for analysis_id, progress in self._progress.items():
            if progress.timestamp:
                try:
                    timestamp = datetime.fromisoformat(progress.timestamp)
                    age = now - timestamp
                    if age > timedelta(minutes=max_age_minutes):
                        to_remove.append(analysis_id)
                except Exception:
                    pass
        
        for analysis_id in to_remove:
            await self.remove(analysis_id)


# Global singleton instance
_progress_tracker: Optional[ProgressTracker] = None


def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker
