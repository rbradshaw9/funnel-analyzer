"""Transactional email helper using SendGrid."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError:  # pragma: no cover - optional dependency in some envs
    SendGridAPIClient = None  # type: ignore[assignment]
    Mail = None  # type: ignore[assignment]

from ..utils.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Lightweight wrapper around SendGrid to avoid scattering SDK calls."""

    def __init__(self, client: SendGridAPIClient, default_from: str, default_reply_to: Optional[str]) -> None:
        self._client = client
        self._default_from = default_from
        self._default_reply_to = default_reply_to

    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text_content: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        if not to_email:
            logger.error("Cannot send email without recipient")
            return False

        sender = from_email or self._default_from
        if not sender:
            logger.error("Email sender address not configured")
            return False

        message = Mail(
            from_email=sender,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        if plain_text_content:
            message.plain_text_content = plain_text_content
        elif html_content:
            message.plain_text_content = "Your email client requires HTML support to view this message."

        if self._default_reply_to:
            message.reply_to = self._default_reply_to

        try:
            response = await asyncio.to_thread(self._client.send, message)
            logger.info("SendGrid response status: %s", getattr(response, "status_code", "unknown"))
            return True
        except Exception as exc:  # noqa: BLE001 - underlying SDK raises various errors
            logger.error("Failed to send email via SendGrid: %s", exc)
            return False


_email_service: Optional[EmailService] = None


def get_email_service() -> Optional[EmailService]:
    global _email_service
    if _email_service is not None:
        return _email_service

    if SendGridAPIClient is None or Mail is None:
        logger.info("SendGrid SDK not installed. Emails disabled.")
        return None

    if not settings.SENDGRID_API_KEY:
        logger.info("SendGrid not configured. Emails disabled.")
        return None

    client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    _email_service = EmailService(
        client=client,
        default_from=settings.EMAIL_DEFAULT_FROM or "no-reply@localhost",
        default_reply_to=settings.EMAIL_DEFAULT_REPLY_TO,
    )
    logger.info("Initialized SendGrid email service")
    return _email_service


def reset_email_service() -> None:
    global _email_service
    _email_service = None
