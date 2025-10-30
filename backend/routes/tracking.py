"""API routes for conversion tracking and attribution."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import Analysis, FunnelSession, Conversion
from ..models.schemas import (
    SessionCreateRequest,
    SessionEventRequest,
    ConversionWebhookRequest,
    ConversionResponse,
    FunnelSessionResponse,
    ConversionStatsResponse,
)
from ..services.attribution import AttributionService
from ..utils.fingerprint import generate_fingerprint
from ..utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP from request headers (Railway/Cloudflare compatible)."""
    # Try common proxy headers first
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list; first IP is the client
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to direct connection IP
    if request.client:
        return request.client.host
    
    return None


@router.post("/track/{analysis_id}/session", response_model=FunnelSessionResponse)
async def track_session(
    analysis_id: int,
    session_data: SessionCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create or update a funnel session for tracking.
    
    This endpoint is called by the client-side tracking script to
    register a new session or update an existing one with new data
    (e.g., when email is captured at opt-in).
    """
    # Verify analysis exists
    analysis_query = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(analysis_query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get client IP and user agent if not provided
    ip_address = session_data.ip_address or get_client_ip(request)
    user_agent = session_data.user_agent or request.headers.get("user-agent")
    
    # Generate fingerprint if not provided
    fingerprint = session_data.fingerprint or generate_fingerprint(
        ip_address=ip_address,
        user_agent=user_agent,
        screen_resolution=session_data.screen_resolution,
        timezone=session_data.timezone,
        language=session_data.language,
    )
    
    # Check if session already exists
    session_query = select(FunnelSession).where(
        FunnelSession.session_id == session_data.session_id
    )
    result = await db.execute(session_query)
    existing_session = result.scalar_one_or_none()
    
    if existing_session:
        # Update existing session
        if session_data.email:
            existing_session.email = session_data.email.lower().strip()
        if session_data.user_id:
            existing_session.user_id = session_data.user_id
        if session_data.order_id:
            existing_session.order_id = session_data.order_id
        
        # Update last_seen_at
        existing_session.last_seen_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(existing_session)
        
        logger.info(f"Updated session {session_data.session_id} for analysis {analysis_id}")
        
        return FunnelSessionResponse(
            session_id=existing_session.session_id,
            fingerprint=existing_session.fingerprint,
            analysis_id=existing_session.analysis_id,
            created=False,
            message="Session updated"
        )
    
    # Create new session
    new_session = FunnelSession(
        analysis_id=analysis_id,
        session_id=session_data.session_id,
        fingerprint=fingerprint,
        email=session_data.email.lower().strip() if session_data.email else None,
        user_id=session_data.user_id,
        order_id=session_data.order_id,
        landing_page=session_data.landing_page,
        referrer=session_data.referrer,
        utm_source=session_data.utm_source,
        utm_medium=session_data.utm_medium,
        utm_campaign=session_data.utm_campaign,
        utm_content=session_data.utm_content,
        utm_term=session_data.utm_term,
        ip_address=ip_address,
        user_agent=user_agent,
        screen_resolution=session_data.screen_resolution,
        timezone=session_data.timezone,
        language=session_data.language,
        page_views=0,
        events=[],
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    logger.info(f"Created session {session_data.session_id} for analysis {analysis_id}")
    
    return FunnelSessionResponse(
        session_id=new_session.session_id,
        fingerprint=new_session.fingerprint,
        analysis_id=new_session.analysis_id,
        created=True,
        message="Session created"
    )


@router.post("/track/{analysis_id}/event")
async def track_event(
    analysis_id: int,
    event_data: SessionEventRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Track an event within a session (page view, click, form submit, etc.).
    
    This builds the session journey for better attribution and analysis.
    """
    # Find the session
    session_query = select(FunnelSession).where(
        FunnelSession.session_id == event_data.session_id
    )
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session with event
    event_record = {
        "type": event_data.event_type,
        "page_url": event_data.page_url,
        "target": event_data.target,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": event_data.metadata or {},
    }
    
    # Append to events array
    current_events = session.events or []
    current_events.append(event_record)
    session.events = current_events
    
    # Update counters
    if event_data.event_type == "pageview":
        session.page_views += 1
        session.last_page_url = event_data.page_url
    
    session.last_seen_at = datetime.utcnow()
    
    await db.commit()
    
    logger.debug(f"Tracked {event_data.event_type} event for session {event_data.session_id}")
    
    return {"success": True, "message": "Event tracked"}


@router.post("/webhooks/convert/{analysis_id}", response_model=ConversionResponse)
async def receive_conversion_webhook(
    analysis_id: int,
    conversion_data: ConversionWebhookRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Receive conversion webhook and attribute to session.
    
    This endpoint accepts webhooks from payment processors (Stripe, Infusionsoft, etc.)
    or manual conversions. It uses the attribution service to match the conversion
    to a funnel session.
    
    Authentication:
    - Bearer token in Authorization header (recommended)
    - API key in X-API-Key header (alternative)
    - For now, we'll allow unauthenticated for testing (TODO: add auth)
    """
    # Verify analysis exists
    analysis_query = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(analysis_query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Check if conversion already exists (prevent duplicates)
    existing_conversion_query = select(Conversion).where(
        Conversion.conversion_id == conversion_data.conversion_id
    )
    result = await db.execute(existing_conversion_query)
    existing_conversion = result.scalar_one_or_none()
    
    if existing_conversion:
        logger.warning(f"Duplicate conversion webhook: {conversion_data.conversion_id}")
        return ConversionResponse(
            conversion_id=conversion_data.conversion_id,
            attributed=existing_conversion.session_id is not None,
            attribution_method=existing_conversion.attribution_method,
            attribution_confidence=existing_conversion.attribution_confidence,
            session_id=existing_conversion.session.session_id if existing_conversion.session else None,
            message="Conversion already recorded (duplicate webhook)"
        )
    
    # Get client IP if not provided (for probabilistic matching)
    ip_address = conversion_data.ip_address or get_client_ip(request)
    user_agent = conversion_data.user_agent or request.headers.get("user-agent")
    converted_at = conversion_data.converted_at or datetime.utcnow()
    
    # Attempt attribution
    attribution_service = AttributionService(db)
    attribution_result = await attribution_service.attribute_conversion(
        analysis_id=analysis_id,
        email=conversion_data.email,
        order_id=conversion_data.order_id or conversion_data.conversion_id,
        user_id=conversion_data.user_id,
        session_fingerprint=conversion_data.session_id,  # Client may send session UUID
        ip_address=ip_address,
        user_agent=user_agent,
        conversion_time=converted_at,
    )
    
    # Convert revenue to cents for storage
    revenue_cents = int(conversion_data.revenue * 100) if conversion_data.revenue else None
    
    # Create conversion record
    conversion = Conversion(
        analysis_id=analysis_id,
        session_id=attribution_result.session.id if attribution_result.session else None,
        conversion_id=conversion_data.conversion_id,
        email=conversion_data.email.lower().strip() if conversion_data.email else None,
        customer_name=conversion_data.customer_name,
        revenue=revenue_cents,
        currency=conversion_data.currency,
        product_name=conversion_data.product_name,
        attribution_method=attribution_result.method,
        attribution_confidence=attribution_result.confidence,
        attribution_metadata=attribution_result.metadata,
        webhook_source=conversion_data.webhook_source,
        webhook_payload=conversion_data.dict(),
        converted_at=converted_at,
        attributed_at=datetime.utcnow() if attribution_result.session else None,
    )
    
    db.add(conversion)
    await db.commit()
    await db.refresh(conversion)
    
    logger.info(
        f"Conversion {conversion_data.conversion_id} recorded - "
        f"Method: {attribution_result.method}, Confidence: {attribution_result.confidence}%"
    )
    
    return ConversionResponse(
        conversion_id=conversion.conversion_id,
        attributed=attribution_result.session is not None,
        attribution_method=attribution_result.method,
        attribution_confidence=attribution_result.confidence,
        session_id=attribution_result.session.session_id if attribution_result.session else None,
        message="Conversion recorded and attributed" if attribution_result.session else "Conversion recorded (not attributed)"
    )


@router.get("/reports/{analysis_id}/conversions", response_model=ConversionStatsResponse)
async def get_conversion_stats(
    analysis_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get conversion statistics for an analysis.
    
    Returns total conversions, attribution rates, revenue, and breakdown by method.
    """
    # Verify analysis exists
    analysis_query = select(Analysis).where(Analysis.id == analysis_id)
    result = await db.execute(analysis_query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get conversion counts
    conversions_query = select(Conversion).where(Conversion.analysis_id == analysis_id)
    result = await db.execute(conversions_query)
    conversions = result.scalars().all()
    
    total_conversions = len(conversions)
    attributed_conversions = sum(1 for c in conversions if c.session_id is not None)
    
    # Calculate attribution rate
    attribution_rate = (attributed_conversions / total_conversions * 100) if total_conversions > 0 else 0.0
    
    # Calculate total revenue
    total_revenue = sum((c.revenue or 0) for c in conversions) / 100.0  # Convert cents to dollars
    
    # Attribution method breakdown
    attribution_methods = {}
    total_confidence = 0
    confidence_count = 0
    
    for conversion in conversions:
        method = conversion.attribution_method or "none"
        attribution_methods[method] = attribution_methods.get(method, 0) + 1
        
        if conversion.attribution_confidence is not None:
            total_confidence += conversion.attribution_confidence
            confidence_count += 1
    
    avg_confidence = (total_confidence / confidence_count) if confidence_count > 0 else None
    
    # Get session count
    sessions_query = select(func.count(FunnelSession.id)).where(
        FunnelSession.analysis_id == analysis_id
    )
    result = await db.execute(sessions_query)
    total_sessions = result.scalar() or 0
    
    # Calculate conversion rate
    conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0.0
    
    return ConversionStatsResponse(
        total_conversions=total_conversions,
        attributed_conversions=attributed_conversions,
        attribution_rate=attribution_rate,
        total_revenue=total_revenue,
        attribution_methods=attribution_methods,
        avg_confidence=avg_confidence,
        total_sessions=total_sessions,
        conversion_rate=conversion_rate,
    )
