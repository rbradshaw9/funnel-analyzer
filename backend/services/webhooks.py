"""Webhook processing helpers for external automation integrations."""

from __future__ import annotations

import hmac
import json
import logging
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Dict, Optional

from urllib.parse import parse_qs

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import WebhookEvent
from ..utils.config import settings

logger = logging.getLogger(__name__)


@dataclass
class StoredWebhookEvent:
    """Lightweight representation of a persisted webhook event."""

    id: int
    payload: Dict[str, Any]
    raw_payload: Optional[str]
    event_type: Optional[str]


@dataclass
class WebhookResult:
    """Details of a processed webhook call."""

    message: str
    status: int
    event: Optional[StoredWebhookEvent] = None


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


def _deserialize_thrivecart_payload(raw_body: bytes) -> Dict[str, Any]:
    """Convert ThriveCart payload into a dictionary from JSON or form-encoded body."""
    text_body = raw_body.decode("utf-8", errors="ignore")
    if not text_body.strip():
        return {}

    try:
        return json.loads(text_body)
    except json.JSONDecodeError:
        form_data = parse_qs(text_body)
        normalized: Dict[str, Any] = {}
        for key, values in form_data.items():
            if not values:
                continue
            normalized[key] = values[0] if len(values) == 1 else values
        if normalized:
            return normalized
        # Fallback: store original body if parsing fails completely
        return {"raw": text_body}


async def handle_thrivecart_webhook(
    *,
    session: AsyncSession,
    body: bytes,
    signature: str | None,
) -> WebhookResult:
    """Process ThriveCart webhook payloads and persist them."""
    secret = settings.THRIVECART_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(status_code=503, detail="ThriveCart integration not configured")

    if not signature:
        logger.warning("ThriveCart webhook missing signature; treating as validation ping")
        return WebhookResult(message="handshake", status=200, event=None)

    _validate_signature(secret, body, signature)

    payload = _deserialize_thrivecart_payload(body)
    raw_payload = body.decode("utf-8", errors="ignore") or None

    event_record = await store_webhook_event(
        session=session,
        source="thrivecart",
        payload=payload,
        raw_payload=raw_payload,
    )
    stored_event = StoredWebhookEvent(
        id=event_record.id,
        payload=payload,
        raw_payload=raw_payload,
        event_type=event_record.event_type,
    )
    await session.commit()
    return WebhookResult(message="ok", status=200, event=stored_event)
