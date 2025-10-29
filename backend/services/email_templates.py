"""Professional email templates for transactional emails."""

from __future__ import annotations
from typing import Dict, Any


def get_email_template_base() -> str:
    """Get the base email template with professional styling."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1e293b;
            background-color: #f8fafc;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        .header {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            color: #ffffff;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header .tagline {{
            margin: 8px 0 0 0;
            color: #e0f2fe;
            font-size: 14px;
            font-weight: 400;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .content h2 {{
            margin: 0 0 20px 0;
            color: #0f172a;
            font-size: 22px;
            font-weight: 600;
        }}
        .content p {{
            margin: 0 0 16px 0;
            color: #475569;
            font-size: 16px;
            line-height: 1.7;
        }}
        .button-container {{
            margin: 32px 0;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
            transition: all 0.2s;
        }}
        .button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
        }}
        .footer {{
            padding: 30px;
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }}
        .footer p {{
            margin: 0 0 8px 0;
            color: #64748b;
            font-size: 14px;
        }}
        .footer a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .divider {{
            margin: 24px 0;
            border: 0;
            border-top: 1px solid #e2e8f0;
        }}
        .secondary-text {{
            color: #64748b;
            font-size: 14px;
        }}
        .highlight-box {{
            background-color: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 16px 20px;
            margin: 24px 0;
            border-radius: 4px;
        }}
        .highlight-box p {{
            margin: 0;
            color: #1e40af;
            font-size: 15px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Funnel Analyzer Pro</h1>
            <p class="tagline">AI-Powered Funnel Optimization</p>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>Need help? Reply to this email or visit <a href="https://funnelanalyzerpro.com/support">our support center</a></p>
            <p>&copy; {year} Funnel Analyzer Pro. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def magic_link_email(*, magic_link_url: str, expires_minutes: int, user_email: str) -> Dict[str, Any]:
    """Generate magic link login email."""
    from datetime import datetime
    
    content = f"""
        <h2>Your Secure Login Link</h2>
        <p>Hi there,</p>
        <p>Click the button below to securely sign in to your Funnel Analyzer Pro account. This link will expire in <strong>{expires_minutes} minutes</strong> for your security.</p>
        
        <div class="button-container">
            <a href="{magic_link_url}" class="button">Sign In to Your Dashboard</a>
        </div>
        
        <div class="highlight-box">
            <p><strong>Security tip:</strong> If you didn't request this email, you can safely ignore it. This link will only work once and expires automatically.</p>
        </div>
        
        <hr class="divider">
        
        <p class="secondary-text">Or copy and paste this URL into your browser:</p>
        <p class="secondary-text" style="word-break: break-all;">{magic_link_url}</p>
    """
    
    html = get_email_template_base().format(
        subject="Your Secure Login Link - Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Your Secure Login Link - Funnel Analyzer Pro

Hi there,

Click the link below to securely sign in to your Funnel Analyzer Pro account. This link will expire in {expires_minutes} minutes for your security.

{magic_link_url}

Security tip: If you didn't request this email, you can safely ignore it. This link will only work once and expires automatically.

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
        
        <div class="highlight-box">
            <p><strong>Your Plan:</strong> {plan.title()} - {plan_benefits.get(plan, 'Premium features')}</p>
        </div>
        
        <p>Click the button below to access your dashboard and start analyzing your funnels:</p>
        
        <div class="button-container">
            <a href="{magic_link_url}" class="button">Access Your Dashboard</a>
        </div>
        
        <h2 style="margin-top: 40px;">Getting Started</h2>
        <p><strong>1. Analyze Your First Funnel</strong><br>
        Paste your funnel URLs and let our AI analyze every aspect of your conversion flow.</p>
        
        <p><strong>2. Review Your Insights</strong><br>
        Get detailed scores across clarity, value proposition, social proof, design, and conversion flow.</p>
        
        <p><strong>3. Implement Improvements</strong><br>
        Follow our actionable recommendations to boost your funnel performance.</p>
        
        <hr class="divider">
        
        <p>If you have any questions, just reply to this email. We're here to help!</p>
        
        <p>Best regards,<br>
        <strong>Ryan</strong><br>
        Funnel Analyzer Pro</p>
    """
    
    html = get_email_template_base().format(
        subject="Welcome to Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Welcome to Funnel Analyzer Pro!

Hi{' ' + user_name if user_name else ''},

Thank you for joining Funnel Analyzer Pro! We're excited to help you optimize your marketing funnels and drive better conversions.

Your Plan: {plan.title()} - {plan_benefits.get(plan, 'Premium features')}

Click the link below to access your dashboard and start analyzing your funnels:

{magic_link_url}

Getting Started:

1. Analyze Your First Funnel
   Paste your funnel URLs and let our AI analyze every aspect of your conversion flow.

2. Review Your Insights
   Get detailed scores across clarity, value proposition, social proof, design, and conversion flow.

3. Implement Improvements
   Follow our actionable recommendations to boost your funnel performance.

If you have any questions, just reply to this email. We're here to help!

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
    
    content = f"""
        <h2>Your Funnel Analysis is Ready {score_emoji}</h2>
        <p>Hi{' ' + user_name if user_name else ''},</p>
        <p>Great news! We've finished analyzing your funnel. Here's a quick overview:</p>
        
        <div class="highlight-box">
            <p><strong>Overall Score: {overall_score}/100</strong></p>
            <p style="margin-top: 8px;">Top Priority: {top_issue}</p>
        </div>
        
        <p>Click below to view your complete analysis with detailed recommendations:</p>
        
        <div class="button-container">
            <a href="{analysis_url}" class="button">View Full Analysis</a>
        </div>
        
        <p>Your analysis includes:</p>
        <p>✓ Detailed scoring across 5 key dimensions<br>
        ✓ Page-by-page breakdown and feedback<br>
        ✓ Actionable recommendations for improvement<br>
        ✓ Visual screenshots with annotations</p>
        
        <hr class="divider">
        
        <p>Questions about your results? Just reply to this email!</p>
        
        <p>Best regards,<br>
        <strong>Ryan</strong><br>
        Funnel Analyzer Pro</p>
    """
    
    html = get_email_template_base().format(
        subject=f"Your Funnel Analysis is Ready - Score: {overall_score}/100",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Your Funnel Analysis is Ready {score_emoji}

Hi{' ' + user_name if user_name else ''},

Great news! We've finished analyzing your funnel. Here's a quick overview:

Overall Score: {overall_score}/100
Top Priority: {top_issue}

View your complete analysis:
{analysis_url}

Your analysis includes:
✓ Detailed scoring across 5 key dimensions
✓ Page-by-page breakdown and feedback
✓ Actionable recommendations for improvement
✓ Visual screenshots with annotations

Questions about your results? Just reply to this email!

Best regards,
Ryan
Funnel Analyzer Pro

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
        <h2>Reset Your Password</h2>
        <p>Hi there,</p>
        <p>We received a request to reset the password for your Funnel Analyzer Pro account.</p>
        
        <div class="button-container">
            <a href="{reset_url}" class="button">Reset Password</a>
        </div>
        
        <div class="highlight-box">
            <p><strong>Security reminder:</strong> This link expires in 30 minutes. If you didn't request this reset, please ignore this email and your password will remain unchanged.</p>
        </div>
        
        <hr class="divider">
        
        <p class="secondary-text">Or copy and paste this URL into your browser:</p>
        <p class="secondary-text" style="word-break: break-all;">{reset_url}</p>
    """
    
    html = get_email_template_base().format(
        subject="Reset Your Password - Funnel Analyzer Pro",
        content=content,
        year=datetime.now().year
    )
    
    plain_text = f"""Reset Your Password - Funnel Analyzer Pro

Hi there,

We received a request to reset the password for your Funnel Analyzer Pro account.

Click here to reset your password:
{reset_url}

Security reminder: This link expires in 30 minutes. If you didn't request this reset, please ignore this email and your password will remain unchanged.

© {datetime.now().year} Funnel Analyzer Pro. All rights reserved.
"""
    
    return {
        "subject": "Reset Your Password - Funnel Analyzer Pro",
        "html": html,
        "text": plain_text
    }
