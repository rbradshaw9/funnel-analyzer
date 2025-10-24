"""Onboarding helpers for newly activated members."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import User
from ..services.auth import create_magic_link_token
from ..services.email import get_email_service
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
    success_path = f"/success?plan={plan_slug}" if plan_slug in {"basic", "pro"} else "/success"
    success_url = f"{settings.FRONTEND_URL.rstrip('/')}{success_path}"

    subject = "Welcome to Funnel Analyzer Pro"
    plan_label = plan_slug.title() if plan_slug not in {"member", "free"} else "Member"

    html_content = f"""
    <p>Hi there,</p>
    <p>Welcome to the <strong>{plan_label}</strong> plan. Your workspace is active and ready to use.</p>
    <p>Use the button below to access your dashboard instantly. This secure link expires in {max(5, settings.MAGIC_LINK_EXPIRATION_MINUTES)} minutes.</p>
    <p>
      <a href="{dashboard_url}" style="display:inline-block;padding:12px 18px;background:#4f46e5;color:#ffffff;border-radius:8px;text-decoration:none;font-weight:600">
        Open your dashboard
      </a>
    </p>
    <p>If you need onboarding tips, jump back to <a href="{success_url}">{success_url}</a>.</p>
    <p>Questions? Reply to this email or contact <a href="mailto:support@funnelanalyzerpro.com">support@funnelanalyzerpro.com</a>.</p>
    <p>— The Funnel Analyzer Pro team</p>
    """

    plain_text_content = (
        "Welcome to Funnel Analyzer Pro! Your workspace is ready. "
        "Use the link below to open your dashboard (expires in "
        f"{max(5, settings.MAGIC_LINK_EXPIRATION_MINUTES)} minutes).\n\n"
        f"{dashboard_url}\n\n"
        f"Need help? Visit {success_url} or email support@funnelanalyzerpro.com"
    )

    sent = await email_service.send_email(
        to_email=user.email,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_text_content,
    )

    if sent:
        user.last_magic_link_sent_at = now
        session.add(user)
        await session.commit()
        logger.info("Sent onboarding magic link to %s", user.email)
        return True

    logger.error("Failed to send onboarding magic link to %s", user.email)
    return False
