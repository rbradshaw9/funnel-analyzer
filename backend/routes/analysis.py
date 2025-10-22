"""
Analysis route - Main endpoint for funnel analysis.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import AnalysisRequest, AnalysisResponse
from ..services.analyzer import analyze_funnel_mock
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse, status_code=200)
async def analyze_funnel(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze a marketing funnel by URLs.
    
    This endpoint:
    1. Validates input URLs
    2. Scrapes content and takes screenshots
    3. Analyzes with GPT-4o
    4. Returns structured scores and feedback
    
    **Note**: Currently returns mock data for development.
    """
    try:
        logger.info(f"Received analysis request for {len(request.urls)} URLs")
        
        # Convert Pydantic URLs to strings
        url_strings = [str(url) for url in request.urls]
        
        # TODO: Replace with real analysis service
        # For now, use mock data
        result = await analyze_funnel_mock(url_strings)
        
        logger.info(f"Analysis completed with overall score: {result['overall_score']}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
