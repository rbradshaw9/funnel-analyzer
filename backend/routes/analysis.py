"""Analysis route - Core funnel analysis endpoint."""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import Analysis, User
from ..models.schemas import AnalysisEmailRequest, AnalysisRequest, AnalysisResponse
from ..services.analyzer import analyze_funnel
from ..services.notifications import send_analysis_email
from ..services.plan_gating import filter_analysis_by_plan
from ..services.reports import get_report_by_id
from ..services.progress_tracker import get_progress_tracker
from ..utils.config import settings
from ..utils.rate_limiter import CompositeRateLimiter, RateLimitExceeded, SlidingWindowRateLimiter

router = APIRouter()
logger = logging.getLogger(__name__)

analysis_rate_limiter = CompositeRateLimiter()
analysis_rate_limiter.register(
    "ip",
    SlidingWindowRateLimiter(
        limit=settings.ANALYSIS_RATE_LIMIT_PER_IP,
        window_seconds=settings.ANALYSIS_RATE_LIMIT_WINDOW_SECONDS,
    ),
)
analysis_rate_limiter.register(
    "user",
    SlidingWindowRateLimiter(
        limit=settings.ANALYSIS_RATE_LIMIT_PER_USER,
        window_seconds=settings.ANALYSIS_RATE_LIMIT_WINDOW_SECONDS,
    ),
)


@router.post("/analyze", response_model=AnalysisResponse, status_code=200)
async def analyze_funnel_endpoint(
    request: AnalysisRequest,
    raw_request: Request,
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
    
    The analysis_id in the response can be used to poll for progress updates
    via GET /api/analysis/progress/{analysis_id}
    """
    try:
        client_ip = raw_request.client.host if raw_request.client else "unknown"

        try:
            await analysis_rate_limiter.check(
                {
                    "ip": f"ip:{client_ip}",
                    "user": f"user:{user_id}" if user_id is not None else None,
                }
            )
        except RateLimitExceeded as exc:  # pragma: no cover - trivial guard
            retry_after = max(int(exc.retry_after), 1)
            raise HTTPException(
                status_code=429,
                detail="Too many analysis requests. Please wait before retrying.",
                headers={"Retry-After": str(retry_after)},
            ) from exc

        logger.info(f"Received analysis request for {len(request.urls)} URLs")

        # Generate unique analysis ID for progress tracking
        analysis_id = str(uuid.uuid4())

        # Convert Pydantic URLs to strings
        url_strings = [str(url) for url in request.urls]

        result = await analyze_funnel(
            url_strings,
            session=session,
            user_id=user_id,
            recipient_email=request.email,
            analysis_id=analysis_id,
        )

        # Get user plan for filtering
        user_plan = None
        if user_id:
            user = await session.get(User, user_id)
            if user:
                user_plan = user.plan
        
        # Filter analysis based on plan
        filtered_result = filter_analysis_by_plan(result, user_plan)

        if request.email:
            asyncio.create_task(send_analysis_email(recipient_email=request.email, analysis=filtered_result))

        logger.info(f"Analysis completed with overall score: {filtered_result.overall_score}")
        return filtered_result

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


@router.get("/progress/{analysis_id}")
async def get_analysis_progress(analysis_id: str):
    """
    Poll for analysis progress updates.
    
    Returns the current progress state including:
    - stage: current processing stage
    - progress_percent: 0-100
    - message: human-readable status message
    - current_page/total_pages: for multi-page funnels
    """
    progress_tracker = get_progress_tracker()
    progress = await progress_tracker.get(analysis_id)
    
    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found or progress tracking expired"
        )
    
    return progress
