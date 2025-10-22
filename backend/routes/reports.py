"""
Reports route - Retrieve past analysis reports.
"""

from fastapi import APIRouter, HTTPException, Query
from ..models.schemas import ReportListResponse, AnalysisResponse
from ..services.reports import get_user_reports_mock, get_report_by_id_mock
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/detail/{analysis_id}", response_model=AnalysisResponse)
async def get_report_detail(analysis_id: int):
    """
    Get detailed analysis report by ID.
    
    Returns complete analysis with all pages, scores, and feedback.
    **Note**: Currently returns mock data for development.
    """
    try:
        logger.info(f"Fetching detailed report for analysis {analysis_id}")
        
        # TODO: Replace with real database query
        result = await get_report_by_id_mock(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch report detail: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve report")


@router.get("/{user_id}", response_model=ReportListResponse)
async def get_reports(
    user_id: int,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get list of past analysis reports for a user.
    
    Returns paginated list of analyses with summary information.
    **Note**: Currently returns mock data for development.
    """
    try:
        logger.info(f"Fetching reports for user {user_id}, limit={limit}, offset={offset}")
        
        # TODO: Replace with real database query
        result = await get_user_reports_mock(user_id, limit, offset)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch reports: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")
