"""API routes for funnel analysis workflows."""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import Analysis
from ..models.schemas import AnalysisEmailRequest, AnalysisRequest, AnalysisResponse
from ..services.analyzer import analyze_funnel
from ..services.notifications import send_analysis_email
from ..services.reports import get_report_by_id

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse, status_code=200)
async def analyze_funnel_endpoint(
    request: AnalysisRequest,
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

        result = await analyze_funnel(
            url_strings,
            session=session,
            user_id=user_id,
            recipient_email=request.email,
        )

        if request.email:
            asyncio.create_task(send_analysis_email(recipient_email=request.email, analysis=result))

        logger.info(f"Analysis completed with overall score: {result.overall_score}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.post("/analyze/{analysis_id}/email", status_code=202)
async def resend_analysis_email(
    analysis_id: int,
    payload: AnalysisEmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Trigger an email delivery for an existing analysis report."""

    analysis = await session.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report_payload = await get_report_by_id(analysis_id=analysis_id, session=session)
    if report_payload is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report_payload["recipient_email"] = payload.email
    analysis_response = AnalysisResponse.model_validate(report_payload)

    sent = await send_analysis_email(recipient_email=payload.email, analysis=analysis_response)
    if not sent:
        raise HTTPException(status_code=503, detail="Email service unavailable or failed to send")

    analysis.recipient_email = payload.email
    session.add(analysis)
    await session.commit()

    return {"status": "sent"}
