"""Notification helpers for analysis events."""

from __future__ import annotations

import html
import logging

from ..models.schemas import AnalysisResponse
from .email import get_email_service

logger = logging.getLogger(__name__)


async def send_analysis_email(*, recipient_email: str, analysis: AnalysisResponse) -> bool:
    """Send a concise analysis recap to the recipient, if email is configured."""
    email_service = get_email_service()
    if not email_service:
        logger.info("Email service unavailable; skipping analysis notification")
        return False

    subject = f"Your Funnel Analyzer Pro Report (Score: {analysis.overall_score}/100)"

    summary_html = html.escape(analysis.summary).replace("\n", "<br />")
    page_rows = []
    for page in analysis.pages:
        title = html.escape(page.title or page.url)
        scores = page.scores
        page_rows.append(
            f"<li><strong>{title}</strong>: {scores.clarity}/{scores.value}/{scores.proof}/{scores.design}/{scores.flow}</li>"
        )

    body_html = f"""
    <p>Hi there,</p>
    <p>Your funnel analysis is ready. Here's the executive summary:</p>
    <blockquote style="border-left:4px solid #6366f1;padding-left:12px;margin:16px 0;color:#1f2937;">
        {summary_html}
    </blockquote>
    <p>Overall score: <strong>{analysis.overall_score}/100</strong></p>
    <p>Page breakdown:</p>
    <ul>
        {''.join(page_rows)}
    </ul>
    <p>Log in to your dashboard for the full playbook and recommendations.</p>
    <p>— Funnel Analyzer Pro</p>
    """

    return await email_service.send_email(
        to_email=recipient_email,
        subject=subject,
        html_content=body_html,
    )