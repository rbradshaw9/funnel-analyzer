"""Notification helpers for analysis events."""

from __future__ import annotations

import html
import logging

from ..models.schemas import AnalysisResponse
from .email import get_email_service

logger = logging.getLogger(__name__)


def _get_merge_data(recipient_email: str, analysis: AnalysisResponse) -> dict:
    """Get merge data for email templates."""
    # Extract user name from email or use fallback
    user_name = "valued customer"
    if recipient_email:
        # Try to extract name from email (e.g., john.doe@example.com -> John Doe)
        local_part = recipient_email.split('@')[0]
        if '.' in local_part:
            parts = local_part.split('.')
            user_name = ' '.join(part.capitalize() for part in parts)
        else:
            user_name = local_part.capitalize()
    
    return {
        'user_name': user_name,
        'user_email': recipient_email,
        'overall_score': analysis.overall_score,
        'total_pages': len(analysis.pages),
        'analysis_date': analysis.created_at.strftime('%B %d, %Y') if analysis.created_at else 'Today',
        'first_page_url': analysis.pages[0].url if analysis.pages else '',
        'company_name': 'Funnel Analyzer Pro',
        'support_email': 'ryan@funnelanalyzerpro.com',
        'dashboard_url': 'https://funnelanalyzerpro.com/dashboard',
        'report_url': f'https://funnelanalyzerpro.com/reports/{analysis.analysis_id}' if hasattr(analysis, 'analysis_id') else 'https://funnelanalyzerpro.com/dashboard'
    }


def _apply_merge_codes(template: str, merge_data: dict) -> str:
    """Apply merge codes to email template."""
    for key, value in merge_data.items():
        placeholder = f"{{{{{key}}}}}"
        template = template.replace(placeholder, str(value))
    return template


async def send_analysis_email(*, recipient_email: str, analysis: AnalysisResponse) -> bool:
    """Send a concise analysis recap to the recipient, if email is configured."""
    email_service = get_email_service()
    if not email_service:
        logger.info("Email service unavailable; skipping analysis notification")
        return False

    # Get merge data
    merge_data = _get_merge_data(recipient_email, analysis)
    
    subject = f"{{{{user_name}}}}, Your Funnel Analysis Report (Score: {{{{overall_score}}}}/100)"
    subject = _apply_merge_codes(subject, merge_data)

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

    # Add plural 's' if more than one page
    page_plural = "s" if len(analysis.pages) > 1 else ""
    merge_data['page_plural'] = page_plural
    
    # Create email template with merge codes
    body_template = f"""
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
                                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: bold;">🚀 Hi {{{{user_name}}}}, Your Funnel Analysis is Ready!</h1>
                                <p style="margin: 8px 0 0 0; color: #e0e7ff; font-size: 16px;">Professional insights for {{{{total_pages}}}} page{page_plural} analyzed on {{{{analysis_date}}}}</p>
                            </td>
                        </tr>
                        
                        <!-- Score Section -->
                        <tr>
                            <td style="padding: 24px 32px;">
                                <div style="text-align: center; padding: 20px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                                    <h2 style="margin: 0 0 8px 0; color: #1f2937; font-size: 18px;">Overall Funnel Score</h2>
                                    <div style="font-size: 48px; font-weight: bold; color: {score_color}; margin: 8px 0;">{{{{overall_score}}}}/100</div>
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
                                    <h3 style="margin: 0 0 12px 0; color: white; font-size: 18px;">Ready to optimize your funnel, {{{{user_name}}}}?</h3>
                                    <p style="margin: 0 0 16px 0; color: #e0e7ff;">Get detailed recommendations, A/B testing priorities, and implementation guides in your dashboard.</p>
                                    <a href="{{{{dashboard_url}}}}" style="display: inline-block; background-color: white; color: #6366f1; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 16px;">View Full Report →</a>
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
                                    © 2025 {{{{company_name}}}}. Professional conversion optimization made simple.
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
    
    # Apply merge codes to create final HTML
    body_html = _apply_merge_codes(body_template, merge_data)

    logger.info(f"📧 Attempting to send analysis report email to {recipient_email}")
    logger.info(f"📧 Email subject: {subject}")
    logger.info(f"📧 User name extracted: {merge_data.get('user_name')}")
    
    # Debug: Check if SendGrid is configured  
    if not email_service:
        logger.error(f"❌ Email service not available - check SENDGRID_API_KEY environment variable")
        return False
    
    # Enhanced debugging - check SendGrid configuration
    from ..utils.config import settings
    logger.info(f"📧 SendGrid API Key configured: {'Yes' if settings.SENDGRID_API_KEY else 'No'}")
    logger.info(f"📧 SendGrid API Key length: {len(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else 0}")
    logger.info(f"📧 From email: {settings.EMAIL_DEFAULT_FROM}")
    logger.info(f"📧 Reply-to email: {settings.EMAIL_DEFAULT_REPLY_TO}")
    
    # Validate email address format
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, recipient_email):
        logger.error(f"❌ Invalid email address format: {recipient_email}")
        return False
    
    logger.info(f"📧 Email validation passed for: {recipient_email}")
    
    try:
        sent = await email_service.send_email(
            to_email=recipient_email,
            subject=subject,
            html_content=body_html,
        )
        
        if sent:
            logger.info(f"✅ Analysis email sent successfully to {recipient_email}")
            logger.info(f"✅ Email content length: {len(body_html)} characters")
            logger.info(f"✅ SendGrid API call completed successfully")
        else:
            logger.warning(f"❌ SendGrid returned failure for {recipient_email}")
            logger.warning(f"❌ Check SendGrid API key validation and sender authentication")
            logger.warning(f"❌ Verify domain authentication in SendGrid dashboard")
            
        return sent
        
    except Exception as e:
        logger.error(f"❌ Exception sending analysis email to {recipient_email}: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Full error details: {repr(e)}")
        
        # Check for specific SendGrid errors
        if "authentication" in str(e).lower():
            logger.error(f"❌ Authentication error - check SendGrid API key validity")
        elif "sender" in str(e).lower():
            logger.error(f"❌ Sender error - verify sender email authentication in SendGrid")
        elif "400" in str(e):
            logger.error(f"❌ Bad request - check email content or recipient format")
        elif "403" in str(e):
            logger.error(f"❌ Forbidden - check SendGrid API key permissions")
        elif "429" in str(e):
            logger.error(f"❌ Rate limit exceeded - too many emails sent")
            
        return False