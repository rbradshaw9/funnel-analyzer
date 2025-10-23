"""Subscription management helpers for ThriveCart webhook events."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import User

logger = logging.getLogger(__name__)

_ACTIVE_EVENTS = {
    "order.success",
    "order.paid",
    "subscription_payment",
    "subscription_payment_success",
    "subscription_rebill",
    "subscription_renewed",
    "subscription_active",
}

_PAST_DUE_EVENTS = {
    "subscription_payment_failed",
    "subscription_failed",
    "subscription_payment_declined",
    "subscription_delinquent",
}

_CANCELED_EVENTS = {
    "subscription_cancelled",
    "subscription_canceled",
    "subscription_expired",
    "subscription_finished",
    "subscription_stopped",
    "subscription_paused",
    "order.refunded",
    "subscription_refunded",
}

_PLAN_KEYS = (
    "subscription[product_name]",
    "subscription.product_name",
    "subscription[product]",
    "product_name",
    "main_product_name",
    "product[label]",
    "product.label",
    "offer",
    "products[0][name]",
    "products.0.name",
)

_SUBSCRIPTION_ID_KEYS = (
    "subscription[subscription_id]",
    "subscription[id]",
    "subscription.subscription_id",
    "subscription_id",
    "order_id",
)

_CUSTOMER_ID_KEYS = (
    "customer[customer_id]",
    "customer[id]",
    "customer.customer_id",
    "customer_id",
)

_PORTAL_URL_KEYS = (
    "customer[portal_access_url]",
    "customer.portal_access_url",
    "portal_access_url",
    "portal_url",
)

_EXPIRY_KEYS = (
    "subscription[next_payment_date]",
    "subscription.next_payment_date",
    "subscription[next_payment_timestamp]",
    "subscription.next_payment_timestamp",
    "subscription[end]",
    "subscription.end",
    "subscription[expires]",
    "subscription.expires",
    "subscription[expiry_date]",
    "subscription.expiry_date",
)

_STATUS_KEYS = (
    "subscription[status]",
    "subscription.status",
    "status",
)

_EMAIL_KEYS = (
    "customer[email]",
    "customer.email",
    "customer[customer_email]",
    "customer.customer_email",
    "customer_email",
    "email",
)


def _tokenize_key(key: str) -> List[str]:
    tokens: List[str] = []
    buffer = ""
    i = 0
    length = len(key)
    while i < length:
        char = key[i]
        if char in ".[":
            if buffer:
                tokens.append(buffer)
                buffer = ""
            if char == "[":
                end = key.find("]", i)
                if end == -1:
                    break
                token = key[i + 1 : end]
                if token:
                    tokens.append(token)
                i = end + 1
            else:
                i += 1
        elif char == "]":
            if buffer:
                tokens.append(buffer)
                buffer = ""
            i += 1
        else:
            buffer += char
            i += 1
    if buffer:
        tokens.append(buffer)
    return [token for token in tokens if token]


def _get_nested_value(payload: Dict[str, Any], key: str) -> Any:
    if key in payload:
        return payload[key]

    tokens = _tokenize_key(key)
    if not tokens:
        return None

    current: Any = payload
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                return None
            current = current[token]
        elif isinstance(current, (list, tuple)):
            try:
                index = int(token)
            except (TypeError, ValueError):
                return None
            if index < 0 or index >= len(current):
                return None
            current = current[index]
        else:
            return None
    return current


def _lookup(payload: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for key in keys:
        value = _get_nested_value(payload, key)
        if value in (None, "", [], {}):
            continue
        return value
    return None


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _coerce_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value in (None, "", [], {}):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        if value <= 0:
            return None
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            numeric = float(text)
            if numeric > 0:
                return datetime.fromtimestamp(numeric, tz=timezone.utc)
        except ValueError:
            pass
        canonical = text.replace("Z", "+00:00")
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(canonical, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                return dt
            except ValueError:
                continue
        try:
            dt = datetime.fromisoformat(canonical)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except ValueError:
            return None
    return None


def _normalize_status(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_")
    if normalized in {"active", "trial", "trialing", "paid"}:
        return "active"
    if normalized in {"past_due", "pastdue"}:
        return "past_due"
    if normalized in {"canceled", "cancelled", "expired", "ended", "stopped", "inactive"}:
        return "canceled"
    return None


def _status_from_event(event_type: Optional[str]) -> Optional[str]:
    if not event_type:
        return None
    normalized = event_type.strip().lower()
    if normalized in _ACTIVE_EVENTS:
        return "active"
    if normalized in _PAST_DUE_EVENTS:
        return "past_due"
    if normalized in _CANCELED_EVENTS:
        return "canceled"
    return None


def _derive_status_and_reason(event_type: Optional[str], explicit_status: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    status_from_payload = _normalize_status(explicit_status)
    if status_from_payload:
        reason = f"ThriveCart reported status {explicit_status}"
        if event_type:
            reason += f" via {event_type}"
        return status_from_payload, reason

    status_from_event = _status_from_event(event_type)
    if status_from_event:
        reason = f"ThriveCart event: {event_type}"
        return status_from_event, reason

    return None, None


def _extract_datetime(payload: Dict[str, Any], keys: Iterable[str]) -> Optional[datetime]:
    raw_value = _lookup(payload, keys)
    if raw_value is None:
        return None
    return _parse_timestamp(raw_value)


async def apply_thrivecart_membership_update(
    session: AsyncSession,
    payload: Dict[str, Any],
) -> Optional[User]:
    """Update or create a user record based on a ThriveCart webhook payload."""

    if not isinstance(payload, dict):
        logger.warning("ThriveCart payload must be a dictionary")
        return None

    email_value = _lookup(payload, _EMAIL_KEYS)
    email_str = _coerce_str(email_value)
    if not email_str:
        logger.warning("Skipping ThriveCart membership sync because no email was provided")
        return None

    email = _normalize_email(email_str)

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    created = False
    if user is None:
        user = User(email=email)
        session.add(user)
        await session.flush()
        created = True
        logger.info("Created user %s from ThriveCart webhook", email)

    updated = created
    now = datetime.now(timezone.utc)

    event_type = _coerce_str(_lookup(payload, ("event", "type")))
    explicit_status = _coerce_str(_lookup(payload, _STATUS_KEYS))
    status, status_reason = _derive_status_and_reason(event_type, explicit_status)

    status_changed = False
    if status and status != user.status:
        user.status = status
        user.status_last_updated = now
        user.is_active = 1 if status == "active" else 0
        updated = True
        status_changed = True

    if status_reason and status_reason != (user.status_reason or None):
        user.status_reason = status_reason
        if status_changed or not user.status_last_updated:
            user.status_last_updated = now
        updated = True
    elif status_changed and not status_reason and user.status_reason:
        user.status_reason = None
        updated = True

    plan_value = _coerce_str(_lookup(payload, _PLAN_KEYS))
    if not plan_value and status == "active" and user.plan == "free":
        plan_value = "member"
    if plan_value and plan_value != user.plan:
        user.plan = plan_value
        updated = True

    subscription_id = _coerce_str(_lookup(payload, _SUBSCRIPTION_ID_KEYS))
    if subscription_id and subscription_id != (user.subscription_id or None):
        user.subscription_id = subscription_id
        updated = True

    customer_id = _coerce_str(_lookup(payload, _CUSTOMER_ID_KEYS))
    if customer_id and customer_id != (user.thrivecart_customer_id or None):
        user.thrivecart_customer_id = customer_id
        updated = True

    portal_url = _coerce_str(_lookup(payload, _PORTAL_URL_KEYS))
    if portal_url and portal_url != (user.portal_update_url or None):
        user.portal_update_url = portal_url
        updated = True

    expiry_dt = _extract_datetime(payload, _EXPIRY_KEYS)
    if status in {"past_due", "canceled"} and expiry_dt is None:
        expiry_dt = now
    if status == "active" and expiry_dt is None and user.access_expires_at and user.access_expires_at <= now:
        expiry_dt = None
    if expiry_dt is not None or (status == "active" and user.access_expires_at and user.access_expires_at <= now):
        if expiry_dt != user.access_expires_at:
            user.access_expires_at = expiry_dt
            updated = True

    if updated:
        await session.commit()
        await session.refresh(user)
        logger.info(
            "Applied ThriveCart membership update for %s (status=%s, event=%s)",
            email,
            user.status,
            event_type,
        )

    return user
