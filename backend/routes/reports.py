"""
Reports route - Retrieve past analysis reports.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import User
from ..models.schemas import AnalysisResponse, ReportDeleteResponse, ReportListResponse
from ..services.plan_gating import filter_analysis_by_plan
from ..services.reports import delete_report, get_report_by_id, get_user_reports
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/detail/{analysis_id}", response_model=AnalysisResponse)
async def get_report_detail(
    analysis_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Get detailed analysis report by ID.
    
    Returns complete analysis with all pages, scores, and feedback.
    Results are filtered based on user's plan level.
    """
    try:
        logger.info(f"Fetching detailed report for analysis {analysis_id}")
        
        result = await get_report_by_id(session, analysis_id, user_id=user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Get user plan for filtering
        user_plan = None
        if user_id:
            user = await session.get(User, user_id)
            if user:
                user_plan = user.plan
        
        # Filter analysis based on plan
        filtered_result = filter_analysis_by_plan(result, user_plan)
        
        return filtered_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch report detail: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve report")


@router.delete("/detail/{analysis_id}", response_model=ReportDeleteResponse)
async def remove_report_detail(
    analysis_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """Delete an analysis and purge any persisted screenshots."""

    try:
        result = await delete_report(session=session, analysis_id=analysis_id, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to delete report %s: %s", analysis_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete report") from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"status": "deleted", **result}


@router.get("/{user_id}", response_model=ReportListResponse)
async def get_reports(
    user_id: int,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get list of past analysis reports for a user.
    
    Returns paginated list of analyses with summary information.
    """
    try:
        logger.info(f"Fetching reports for user {user_id}, limit={limit}, offset={offset}")
        
        result = await get_user_reports(session, user_id=user_id, limit=limit, offset=offset)

        return result

    except Exception as e:
        logger.error(f"Failed to fetch reports: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")
