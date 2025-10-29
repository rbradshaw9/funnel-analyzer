"""Professional email templates for transactional emails."""

from __future__ import annotations
from typing import Dict, Any


def get_email_template_base() -> str:
    """Get the base email template with modern professional styling."""
    return """
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <title>{subject}</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        /* Reset styles */
        body, table, td, a {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
        }}
        
        /* Base styles */
        body {{
            margin: 0;
            padding: 0;
            width: 100% !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #1e293b;
            background-color: #f1f5f9;
        }}
        
        /* Container */
        .email-wrapper {{
            width: 100%;
            background-color: #f1f5f9;
            padding: 24px 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        
        /* Header with gradient */
        .header {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 48px 32px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            color: #ffffff;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            line-height: 1.2;
        }}
        .header .tagline {{
            margin: 12px 0 0 0;
            color: #dbeafe;
            font-size: 15px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }}
        
        /* Content area */
        .content {{
            padding: 48px 32px;
        }}
        .content h2 {{
            margin: 0 0 24px 0;
            color: #0f172a;
            font-size: 24px;
            font-weight: 700;
            line-height: 1.3;
        }}
        .content p {{
            margin: 0 0 20px 0;
            color: #475569;
            font-size: 16px;
            line-height: 1.7;
        }}
        .content p:last-child {{
            margin-bottom: 0;
        }}
        
        /* CTA Button */
        .button-container {{
            margin: 36px 0;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 18px 40px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 17px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4), 0 2px 4px -1px rgba(59, 130, 246, 0.2);
            transition: all 0.2s;
        }}
        
        /* Info box */
        .info-box {{
            background-color: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 20px 24px;
            margin: 28px 0;
            border-radius: 8px;
        }}
        .info-box p {{
            margin: 0;
            color: #1e40af;
            font-size: 15px;
            line-height: 1.6;
        }}
        .info-box strong {{
            color: #1e3a8a;
            font-weight: 600;
        }}
        
        /* Divider */
        .divider {{
            margin: 32px 0;
            border: 0;
            border-top: 1px solid #e2e8f0;
        }}
        
        /* Secondary text */
        .secondary-text {{
            color: #64748b;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        /* Footer */
        .footer {{
            padding: 32px;
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }}
        .footer p {{
            margin: 0 0 10px 0;
            color: #64748b;
            font-size: 14px;
            line-height: 1.6;
        }}
        .footer p:last-child {{
            margin-bottom: 0;
        }}
        .footer a {{
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
        }}
        
        /* Responsive */
        @media only screen and (max-width: 600px) {{
            .email-container {{
                border-radius: 0 !important;
            }}
            .header {{
                padding: 36px 24px !important;
            }}
            .header h1 {{
                font-size: 26px !important;
            }}
            .content {{
                padding: 36px 24px !important;
            }}
            .button {{
                padding: 16px 32px !important;
                font-size: 16px !important;
            }}
            .footer {{
                padding: 24px !important;
            }}
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            .email-wrapper {{
                background-color: #0f172a !important;
            }}
            .email-container {{
                background-color: #1e293b !important;
            }}
            .content h2 {{
                color: #f1f5f9 !important;
            }}
            .content p {{
                color: #cbd5e1 !important;
            }}
            .secondary-text {{
                color: #94a3b8 !important;
            }}
            .footer {{
                background-color: #0f172a !important;
                border-top-color: #334155 !important;
            }}
            .footer p {{
                color: #94a3b8 !important;
            }}
            .divider {{
                border-top-color: #334155 !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <table role="presentation" class="email-container" width="600" cellspacing="0" cellpadding="0" border="0" align="center">
            <tr>
                <td class="header">
                    <h1>Funnel Analyzer Pro</h1>
                    <p class="tagline">AI-Powered Funnel Optimization</p>
                </td>
            </tr>
            <tr>
                <td class="content">
                    {content}
                </td>
            </tr>
            <tr>
                <td class="footer">
                    <p>Need help? Reply to this email or visit <a href="https://funnelanalyzerpro.com/support">our support center</a></p>
                    <p>&copy; {year} Funnel Analyzer Pro. All rights reserved.</p>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""


def magic_link_email(*, magic_link_url: str, expires_minutes: int, user_email: str) -> Dict[str, Any]:
    """Generate magic link login email."""
    from datetime import datetime
    
    content = f"""
        <h2>Your Secure Login Link</h2>
        <p>Welcome back! Click the button below to securely access your Funnel Analyzer Pro account.</p>
        
        <div class="button-container">
            <a href="{magic_link_url}" class="button">Sign In to Your Account →</a>
        </div>
        
        <div class="info-box">
            <p><strong>⏱️ Expires in {expires_minutes} minutes</strong> • This link can only be used once for your security.</p>
        </div>
        
        <hr class="divider">
        
        <p class="secondary-text"><strong>Didn't request this?</strong> You can safely ignore this email. If you're concerned about your account security, please contact our support team.</p>
        
        <p class="secondary-text" style="margin-top: 20px;"><strong>Link not working?</strong> Copy and paste this URL:</p>
        <p class="secondary-text" style="word-break: break-all; font-family: monospace; font-size: 13px; color: #3b82f6;">{magic_link_url}</p>
    """
    
    html = get_email_template_base().format(
        subject="Your Secure Login Link - Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Your Secure Login Link - Funnel Analyzer Pro

Welcome back! Click the link below to securely access your Funnel Analyzer Pro account.

{magic_link_url}

⏱️ Expires in {expires_minutes} minutes • This link can only be used once for your security.

Didn't request this? You can safely ignore this email. If you're concerned about your account security, please contact our support team.

Need help? Reply to this email or visit https://funnelanalyzerpro.com/support

© {datetime.now().year} Funnel Analyzer Pro. All rights reserved.
"""
    
    return {
        "subject": "Your Secure Login Link - Funnel Analyzer Pro",
        "html": html,
        "text": plain_text
    }


def welcome_email(*, user_name: str, magic_link_url: str, plan: str = "free") -> Dict[str, Any]:
    """Generate welcome email for new users."""
    from datetime import datetime
    
    plan_benefits = {
        "free": "Free plan features including funnel analysis and basic insights",
        "basic": "Basic plan features including advanced analytics and priority support",
        "pro": "Pro plan features including unlimited analyses, team collaboration, and premium support"
    }
    
    content = f"""
        <h2>Welcome to Funnel Analyzer Pro! 🎉</h2>
        <p>Hi{' ' + user_name if user_name else ''},</p>
        <p>Thank you for joining Funnel Analyzer Pro! We're excited to help you optimize your marketing funnels and drive better conversions.</p>
        
        <div class="info-box">
            <p><strong>Your Plan:</strong> {plan.title()} Plan • {plan_benefits.get(plan, 'Premium features')}</p>
        </div>
        
        <div class="button-container">
            <a href="{magic_link_url}" class="button">Access Your Dashboard →</a>
        </div>
        
        <hr class="divider">
        
        <h2>Getting Started in 3 Steps</h2>
        
        <p><strong>1️⃣ Analyze Your First Funnel</strong><br>
        Enter your funnel URLs and let our AI analyze every aspect of your conversion flow.</p>
        
        <p><strong>2️⃣ Review Your Insights</strong><br>
        Get detailed scores across clarity, value proposition, social proof, design, and conversion flow.</p>
        
        <p><strong>3️⃣ Implement Improvements</strong><br>
        Follow our actionable recommendations to boost your funnel performance immediately.</p>
        
        <hr class="divider">
        
        <p class="secondary-text">Questions? Just reply to this email. We're here to help you succeed!</p>
        
        <p style="margin-top: 28px;">Best regards,<br>
        <strong>Ryan</strong><br>
        <span style="color: #64748b;">Funnel Analyzer Pro</span></p>
    """
    
    html = get_email_template_base().format(
        subject="Welcome to Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Welcome to Funnel Analyzer Pro!

Hi{' ' + user_name if user_name else ''},

Thank you for joining Funnel Analyzer Pro! We're excited to help you optimize your marketing funnels and drive better conversions.

Your Plan: {plan.title()} Plan • {plan_benefits.get(plan, 'Premium features')}

Click the link below to access your dashboard:

{magic_link_url}

Getting Started in 3 Steps:

1️⃣ Analyze Your First Funnel
   Enter your funnel URLs and let our AI analyze every aspect of your conversion flow.

2️⃣ Review Your Insights
   Get detailed scores across clarity, value proposition, social proof, design, and conversion flow.

3️⃣ Implement Improvements
   Follow our actionable recommendations to boost your funnel performance immediately.

Questions? Just reply to this email. We're here to help you succeed!

Best regards,
Ryan
Funnel Analyzer Pro

© {datetime.now().year} Funnel Analyzer Pro. All rights reserved.
"""
    
    return {
        "subject": "Welcome to Funnel Analyzer Pro 🎉",
        "html": html,
        "text": plain_text
    }


def analysis_complete_email(*, user_name: str, analysis_url: str, overall_score: int, top_issue: str) -> Dict[str, Any]:
    """Generate email when analysis is complete."""
    from datetime import datetime
    
    score_emoji = "🎉" if overall_score >= 80 else "👍" if overall_score >= 60 else "📊"
    score_label = "Excellent" if overall_score >= 80 else "Good" if overall_score >= 60 else "Needs Work"
    
    content = f"""
        <h2>Your Funnel Analysis is Ready {score_emoji}</h2>
        <p>Hi{' ' + user_name if user_name else ''},</p>
        <p>Great news! We've finished analyzing your funnel and identified key opportunities for improvement.</p>
        
        <div class="info-box">
            <p><strong>Overall Score: {overall_score}/100</strong> • {score_label}</p>
            <p style="margin-top: 8px;"><strong>Top Priority:</strong> {top_issue}</p>
        </div>
        
        <div class="button-container">
            <a href="{analysis_url}" class="button">View Full Analysis →</a>
        </div>
        
        <h2>What's Inside Your Report</h2>
        <p>✅ <strong>5 Key Dimensions</strong> • Detailed scoring across clarity, value prop, social proof, design, and flow</p>
        <p>✅ <strong>Page-by-Page Breakdown</strong> • Individual feedback for every step of your funnel</p>
        <p>✅ <strong>Actionable Recommendations</strong> • Specific improvements you can implement today</p>
        <p>✅ <strong>Visual Screenshots</strong> • Annotated images showing exactly what to fix</p>
        
        <hr class="divider">
        
        <p class="secondary-text">Have questions about your results? Reply to this email and we'll help you understand the recommendations!</p>
    """
    
    html = get_email_template_base().format(
        subject=f"Your Funnel Analysis is Ready - Score: {overall_score}/100",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Your Funnel Analysis is Ready {score_emoji}

Hi{' ' + user_name if user_name else ''},

Great news! We've finished analyzing your funnel and identified key opportunities for improvement.

Overall Score: {overall_score}/100 • {score_label}
Top Priority: {top_issue}

View your complete analysis:
{analysis_url}

What's Inside Your Report:
✅ 5 Key Dimensions • Detailed scoring across clarity, value prop, social proof, design, and flow
✅ Page-by-Page Breakdown • Individual feedback for every step of your funnel
✅ Actionable Recommendations • Specific improvements you can implement today
✅ Visual Screenshots • Annotated images showing exactly what to fix

Have questions about your results? Reply to this email and we'll help you understand the recommendations!

© {datetime.now().year} Funnel Analyzer Pro. All rights reserved.
"""
    
    return {
        "subject": f"Your Funnel Analysis is Ready - Score: {overall_score}/100",
        "html": html,
        "text": plain_text
    }


def password_reset_email(*, reset_url: str, user_email: str) -> Dict[str, Any]:
    """Generate password reset email."""
    from datetime import datetime
    
    content = f"""
        <h2>Reset Your Password 🔐</h2>
        <p>We received a request to reset the password for your Funnel Analyzer Pro account.</p>
        
        <div class="button-container">
            <a href="{reset_url}" class="button">Reset Your Password →</a>
        </div>
        
        <div class="info-box">
            <p><strong>⏱️ Expires in 30 minutes</strong> • This secure link will only work once.</p>
        </div>
        
        <hr class="divider">
        
        <p class="secondary-text"><strong>Didn't request this?</strong> You can safely ignore this email. Your password will remain unchanged and your account is secure.</p>
        
        <p class="secondary-text" style="margin-top: 20px;"><strong>Link not working?</strong> Copy and paste this URL:</p>
        <p class="secondary-text" style="word-break: break-all; font-family: monospace; font-size: 13px; color: #3b82f6;">{reset_url}</p>
    """
    
    html = get_email_template_base().format(
        subject="Reset Your Password - Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Reset Your Password 🔐

We received a request to reset the password for your Funnel Analyzer Pro account.

Click here to reset your password:
{reset_url}

⏱️ Expires in 30 minutes • This secure link will only work once.

Didn't request this? You can safely ignore this email. Your password will remain unchanged and your account is secure.

© {datetime.now().year} Funnel Analyzer Pro. All rights reserved.
"""
    
    return {
        "subject": "Reset Your Password - Funnel Analyzer Pro",
        "html": html,
        "text": plain_text
    }

