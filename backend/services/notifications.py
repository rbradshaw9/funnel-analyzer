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

    # Get the score color based on performance
    if analysis.overall_score >= 80:
        score_color = "#10b981"  # green
        score_status = "Excellent"
    elif analysis.overall_score >= 65:
        score_color = "#f59e0b"  # amber
        score_status = "Good"
    elif analysis.overall_score >= 50:
        score_color = "#ef4444"  # red
        score_status = "Needs Work"
    else:
        score_color = "#dc2626"  # dark red
        score_status = "Critical Issues"

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Funnel Analysis Report</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #374151;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 32px 32px 24px 32px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px 12px 0 0;">
                                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: bold;">🚀 Your Funnel Analysis Report</h1>
                                <p style="margin: 8px 0 0 0; color: #e0e7ff; font-size: 16px;">Professional conversion optimization insights</p>
                            </td>
                        </tr>
                        
                        <!-- Score Section -->
                        <tr>
                            <td style="padding: 24px 32px;">
                                <div style="text-align: center; padding: 20px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                                    <h2 style="margin: 0 0 8px 0; color: #1f2937; font-size: 18px;">Overall Funnel Score</h2>
                                    <div style="font-size: 48px; font-weight: bold; color: {score_color}; margin: 8px 0;">{analysis.overall_score}/100</div>
                                    <div style="color: {score_color}; font-weight: 600; font-size: 16px;">{score_status}</div>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Executive Summary -->
                        <tr>
                            <td style="padding: 0 32px 24px 32px;">
                                <h2 style="margin: 0 0 16px 0; color: #1f2937; font-size: 20px; border-bottom: 2px solid #6366f1; padding-bottom: 8px;">📋 Executive Summary</h2>
                                <div style="background-color: #fefefe; border-left: 4px solid #6366f1; padding: 16px; border-radius: 0 8px 8px 0;">
                                    {summary_html}
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Page Breakdown -->
                        <tr>
                            <td style="padding: 0 32px 24px 32px;">
                                <h2 style="margin: 0 0 16px 0; color: #1f2937; font-size: 20px; border-bottom: 2px solid #6366f1; padding-bottom: 8px;">🔍 Page Performance</h2>
                                <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px;">
                                    <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                                        {''.join(page_rows)}
                                    </ul>
                                    <p style="margin: 12px 0 0 0; font-size: 14px; color: #6b7280; font-style: italic;">
                                        Scores: Clarity / Value / Proof / Design / Flow
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- CTA -->
                        <tr>
                            <td style="padding: 0 32px 32px 32px; text-align: center;">
                                <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px; padding: 24px;">
                                    <h3 style="margin: 0 0 12px 0; color: white; font-size: 18px;">Ready to optimize your funnel?</h3>
                                    <p style="margin: 0 0 16px 0; color: #e0e7ff;">Get detailed recommendations, A/B testing priorities, and implementation guides in your dashboard.</p>
                                    <a href="https://funnelanalyzerpro.com/dashboard" style="display: inline-block; background-color: white; color: #6366f1; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 16px;">View Full Report →</a>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 16px 32px; text-align: center; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
                                <p style="margin: 0;">
                                    Need help? Reply to this email or visit 
                                    <a href="https://funnelanalyzerpro.com/support" style="color: #6366f1; text-decoration: none;">our support center</a>
                                </p>
                                <p style="margin: 8px 0 0 0; font-size: 12px;">
                                    © 2025 Funnel Analyzer Pro. Professional conversion optimization made simple.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    logger.info(f"📧 Sending analysis report email to {recipient_email}")
    
    try:
        sent = await email_service.send_email(
            to_email=recipient_email,
            subject=subject,
            html_content=body_html,
        )
        
        if sent:
            logger.info(f"✅ Analysis email sent successfully to {recipient_email}")
        else:
            logger.warning(f"❌ SendGrid returned failure for {recipient_email}")
            
        return sent
        
    except Exception as e:
        logger.error(f"❌ Exception sending analysis email to {recipient_email}: {str(e)}")
        return False