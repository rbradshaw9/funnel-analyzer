"""
Analysis route - Main endpoint for funnel analysis.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.schemas import AnalysisRequest, AnalysisResponse
from ..services.analyzer import analyze_funnel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse, status_code=200)
async def analyze_funnel_endpoint(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    user_id: int | None = Query(default=None, description="Identifier for the authenticated user"),
):
    """
    Analyze a marketing funnel by URLs.
    
    This endpoint:
    1. Validates input URLs
    2. Scrapes content and takes screenshots
    3. Analyzes with GPT-4o
    4. Returns structured scores and feedback
    """
    try:
        logger.info(f"Received analysis request for {len(request.urls)} URLs")

        # Convert Pydantic URLs to strings
        url_strings = [str(url) for url in request.urls]

        result = await analyze_funnel(url_strings, session=session, user_id=user_id)

        logger.info(f"Analysis completed with overall score: {result.overall_score}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
