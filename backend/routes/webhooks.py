"""Webhook endpoints for third-party automation providers."""

from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..services.webhooks import handle_thrivecart_webhook
from ..utils.config import settings
from ..models.database import WebhookEvent

router = APIRouter()


@router.get("/thrivecart")
async def thrivecart_webhook_ping():
    """Allow ThriveCart to verify the webhook endpoint responds successfully."""
    return {"status": "ready"}


@router.head("/thrivecart")
async def thrivecart_webhook_head() -> Response:
    """Respond to ThriveCart HEAD pings with a 200 status."""
    return Response(status_code=200)


@router.post("/thrivecart")
async def thrivecart_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    x_webhook_signature: str | None = Header(default=None, convert_underscores=False),
    x_thrivecart_signature: str | None = Header(default=None, convert_underscores=False),
    sign: str | None = Query(default=None),
):
    """Receive ThriveCart webhook payloads, verify signature, and persist for processing."""
    body = await request.body()

    try:
        message, status = await handle_thrivecart_webhook(
            session=session,
            body=body,
            signature=x_webhook_signature or x_thrivecart_signature or sign,
        )
    except HTTPException:
        raise

    return JSONResponse({"status": message}, status_code=status)


@router.get("/thrivecart/events")
async def list_thrivecart_events(
    secret: str = Query(..., description="ThriveCart webhook secret for authorization"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent ThriveCart webhook events for debugging and verification."""
    configured_secret = settings.THRIVECART_WEBHOOK_SECRET or ""
    if not configured_secret:
        raise HTTPException(status_code=503, detail="ThriveCart integration not configured")
    if not hmac.compare_digest(secret, configured_secret):
        raise HTTPException(status_code=401, detail="Invalid secret")

    result = await session.execute(
        select(WebhookEvent)
        .where(WebhookEvent.source == "thrivecart")
        .order_by(desc(WebhookEvent.created_at))
        .limit(limit)
    )
    events = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "payload": event.payload,
        }
        for event in result.scalars().all()
    ]

    return {"events": events}
