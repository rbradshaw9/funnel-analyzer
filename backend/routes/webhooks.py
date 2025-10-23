"""Webhook endpoints for third-party automation providers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..services.webhooks import handle_thrivecart_webhook

router = APIRouter()


@router.get("/thrivecart")
async def thrivecart_webhook_ping():
    """Allow ThriveCart to verify the webhook endpoint responds successfully."""
    return {"status": "ready"}


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
