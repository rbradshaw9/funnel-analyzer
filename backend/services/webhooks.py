"""Webhook processing helpers for external automation integrations."""

from __future__ import annotations

import hmac
import json
import logging
from hashlib import sha256
from typing import Any, Dict, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import WebhookEvent
from ..utils.config import settings

logger = logging.getLogger(__name__)


def _validate_signature(secret: str, payload: bytes, provided_signature: str | None) -> None:
    """Validate HMAC SHA-256 signature for webhook payloads."""
    if not provided_signature:
        raise HTTPException(status_code=401, detail="Missing webhook signature header")

    expected = hmac.new(secret.encode("utf-8"), payload, sha256).hexdigest()
    if not hmac.compare_digest(expected, provided_signature.strip()):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


async def store_webhook_event(
    *,
    session: AsyncSession,
    source: str,
    payload: Dict[str, Any],
    raw_payload: str | None,
) -> WebhookEvent:
    """Persist the webhook event for audit and replay."""
    event_type = payload.get("event") or payload.get("type")

    record = WebhookEvent(
        source=source,
        event_type=str(event_type) if event_type else None,
        payload=payload,
        raw_payload=raw_payload,
    )

    session.add(record)
    await session.flush()
    logger.info("Stored webhook event %s from %s", record.id, source)
    return record


async def handle_thrivecart_webhook(
    *,
    session: AsyncSession,
    body: bytes,
    signature: str | None,
) -> Tuple[str, int]:
    """Process ThriveCart webhook payloads and persist them."""
    secret = settings.THRIVECART_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(status_code=503, detail="ThriveCart integration not configured")

    if not signature:
        logger.warning("ThriveCart webhook missing signature; treating as validation ping")
        return ("handshake", 200)

    _validate_signature(secret, body, signature)

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        # ThriveCart can post form-encoded payloads; attempt best-effort conversion
        payload = {"raw": body.decode("utf-8", errors="ignore")}

    await store_webhook_event(
        session=session,
        source="thrivecart",
        payload=payload,
        raw_payload=body.decode("utf-8", errors="ignore"),
    )

    await session.commit()
    return ("ok", 200)
