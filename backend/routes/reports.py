"""
Reports route - Retrieve past analysis reports.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json

from ..db.session import get_db_session
from ..models.database import User, Analysis
from ..models.schemas import AnalysisResponse, ReportDeleteResponse, ReportListResponse
from ..services.plan_gating import filter_analysis_by_plan
from ..services.reports import delete_report, get_report_by_id, get_user_reports
from sqlalchemy import select
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class RenameAnalysisRequest(BaseModel):
    """Request body for renaming an analysis."""
    name: str


class AnalysisVersionsResponse(BaseModel):
    """Response for analysis version history."""
    versions: list[dict]
    count: int


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


@router.patch("/detail/{analysis_id}/rename")
async def rename_analysis(
    analysis_id: int,
    request: RenameAnalysisRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Rename an analysis.
    
    Updates the custom name for an analysis. Max 255 characters.
    """
    try:
        # Get the analysis
        query = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        result = await session.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Update the name
        analysis.name = request.name[:255]  # Truncate to max length
        await session.commit()
        
        logger.info(f"Renamed analysis {analysis_id} to '{request.name}'")
        
        return {"status": "success", "analysis_id": analysis_id, "name": analysis.name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rename analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to rename analysis")


@router.get("/detail/{analysis_id}/versions", response_model=AnalysisVersionsResponse)
async def get_analysis_versions(
    analysis_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Get all versions of an analysis (original + re-runs).
    
    Returns chronological list of all related analyses for tracking progress.
    """
    try:
        # Get the original analysis
        query = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        result = await session.execute(query)
        original = result.scalar_one_or_none()
        
        if not original:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Find root analysis (in case current one is a re-run)
        root_id = original.parent_analysis_id or analysis_id
        
        # Get all versions (root + all children)
        versions_query = select(Analysis).where(
            (Analysis.id == root_id) | (Analysis.parent_analysis_id == root_id)
        ).order_by(Analysis.created_at.asc())
        
        if user_id:
            versions_query = versions_query.where(Analysis.user_id == user_id)
        
        versions_result = await session.execute(versions_query)
        analyses = versions_result.scalars().all()
        
        # Build version list
        versions = []
        for idx, analysis in enumerate(analyses, 1):
            versions.append({
                "analysis_id": analysis.id,
                "version": idx,
                "name": analysis.name,
                "overall_score": analysis.overall_score,
                "created_at": analysis.created_at.isoformat(),
                "is_current": analysis.id == analysis_id,
                "parent_analysis_id": analysis.parent_analysis_id,
            })
        
        return {"versions": versions, "count": len(versions)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch analysis versions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve versions")


@router.post("/detail/{analysis_id}/rerun", response_model=dict)
async def rerun_analysis(
    analysis_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Initiate a re-run of an existing analysis.
    
    Creates a new analysis with the same URLs as the original, 
    linking them via parent_analysis_id for version tracking.
    Returns the new analysis ID that can be polled for progress.
    """
    try:
        # Get the original analysis
        query = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        result = await session.execute(query)
        original = result.scalar_one_or_none()
        
        if not original:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Extract URLs from original analysis
        if not original.urls:
            raise HTTPException(status_code=400, detail="Original analysis has no URLs to re-run")
        
        logger.info(f"Re-running analysis {analysis_id} with {len(original.urls)} URLs")
        
        # Return instruction to call /api/analyze endpoint with parent_analysis_id
        # The actual re-run is handled by the frontend calling the analyze endpoint
        return {
            "status": "ready",
            "message": "Use the analyze endpoint to create a re-run",
            "original_analysis_id": analysis_id,
            "urls": original.urls,
            "parent_analysis_id": analysis_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate re-run: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate re-run")


class UpdateRecommendationCompletionRequest(BaseModel):
    """Request body for updating recommendation completion status."""
    recommendation_id: str
    completed: bool


@router.patch("/detail/{analysis_id}/recommendations")
async def update_recommendation_completion(
    analysis_id: int,
    request: UpdateRecommendationCompletionRequest,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Update the completion status of a specific recommendation.
    
    Stores completion state in recommendation_completions JSONB column.
    Format: {"rec_id_1": true, "rec_id_2": false, ...}
    """
    try:
        # Get the analysis
        query = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        result = await session.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get current completions (handle both None and existing JSONB)
        current_completions = {}
        if analysis.recommendation_completions:
            if isinstance(analysis.recommendation_completions, str):
                current_completions = json.loads(analysis.recommendation_completions)
            elif isinstance(analysis.recommendation_completions, dict):
                current_completions = analysis.recommendation_completions
        
        # Update completion status
        current_completions[request.recommendation_id] = request.completed
        
        # Save back to database
        analysis.recommendation_completions = json.dumps(current_completions)
        await session.commit()
        
        # Calculate completion percentage
        total_count = len(current_completions)
        completed_count = sum(1 for v in current_completions.values() if v)
        completion_percentage = int((completed_count / total_count * 100)) if total_count > 0 else 0
        
        logger.info(
            f"Updated recommendation {request.recommendation_id} completion to {request.completed} "
            f"for analysis {analysis_id} ({completed_count}/{total_count} = {completion_percentage}%)"
        )
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "recommendation_id": request.recommendation_id,
            "completed": request.completed,
            "completions": current_completions,
            "completion_percentage": completion_percentage,
            "completed_count": completed_count,
            "total_count": total_count,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update recommendation completion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update recommendation completion")


@router.get("/detail/{analysis_id}/recommendations/completions")
async def get_recommendation_completions(
    analysis_id: int,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, ge=1, description="Optional user ownership check"),
):
    """
    Get all recommendation completion statuses for an analysis.
    
    Returns the current completion state and statistics.
    """
    try:
        # Get the analysis
        query = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            query = query.where(Analysis.user_id == user_id)
        
        result = await session.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get current completions
        current_completions = {}
        if analysis.recommendation_completions:
            if isinstance(analysis.recommendation_completions, str):
                current_completions = json.loads(analysis.recommendation_completions)
            elif isinstance(analysis.recommendation_completions, dict):
                current_completions = analysis.recommendation_completions
        
        # Calculate stats
        total_count = len(current_completions)
        completed_count = sum(1 for v in current_completions.values() if v)
        completion_percentage = int((completed_count / total_count * 100)) if total_count > 0 else 0
        
        return {
            "analysis_id": analysis_id,
            "completions": current_completions,
            "completion_percentage": completion_percentage,
            "completed_count": completed_count,
            "total_count": total_count,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recommendation completions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendation completions")
