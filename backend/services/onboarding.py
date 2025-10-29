"""Onboarding helpers for newly activated members."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import User
from ..services.auth import create_magic_link_token
from ..services.email import get_email_service
from ..services.email_templates import welcome_email
from ..utils.config import settings

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_plan(plan: Optional[str]) -> str:
    if not plan:
        return "member"
    normalized = plan.strip().lower()
    if normalized in {"basic", "pro", "member", "free"}:
        return normalized
    if "pro" in normalized or "growth" in normalized:
        return "pro"
    if "basic" in normalized:
        return "basic"
    return "member"


async def send_magic_link_onboarding(
    session: AsyncSession,
    user: User,
    *,
    plan: Optional[str] = None,
    force: bool = False,
) -> bool:
    """Send a magic-link onboarding email when a membership becomes active."""

    email_service = get_email_service()
    if not email_service:
        logger.info("Skipping onboarding email; email service unavailable")
        return False

    now = _now_utc()
    if not force and user.last_magic_link_sent_at is not None:
        last_sent = user.last_magic_link_sent_at
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=timezone.utc)
        cooldown = timedelta(minutes=max(5, settings.MAGIC_LINK_EXPIRATION_MINUTES))
        if now - last_sent < cooldown:
            logger.info("Magic link already sent recently to %s; skipping onboarding", user.email)
            return False

    token = await create_magic_link_token(user.id, user.email)
    dashboard_url = f"{settings.FRONTEND_URL.rstrip('/')}/dashboard?token={token}"

    plan_slug = _normalize_plan(plan or user.plan)

    # Use professional welcome email template
    email_data = welcome_email(
        user_name=user.full_name or "",
        magic_link_url=dashboard_url,
        plan=plan_slug
    )

    sent = await email_service.send_email(
        to_email=user.email,
        subject=email_data["subject"],
        html_content=email_data["html"],
        plain_text_content=email_data["text"],
    )

    if sent:
        user.last_magic_link_sent_at = now
        session.add(user)
        await session.commit()
        logger.info("Sent onboarding magic link to %s", user.email)
        return True

    logger.error("Failed to send onboarding magic link to %s", user.email)
    return False
