#!/usr/bin/env python3
"""Test SendGrid email functionality."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.services.email import get_email_service
from backend.utils.config import settings


async def send_test_email():
    """Send a test email to verify SendGrid configuration."""
    
    print("=" * 60)
    print("SendGrid Email Test")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    print(f"   SENDGRID_API_KEY: {'✅ Set' if settings.SENDGRID_API_KEY else '❌ Not set'}")
    print(f"   EMAIL_DEFAULT_FROM: {settings.EMAIL_DEFAULT_FROM}")
    print(f"   EMAIL_DEFAULT_REPLY_TO: {settings.EMAIL_DEFAULT_REPLY_TO}")
    
    if not settings.SENDGRID_API_KEY:
        print("\n❌ ERROR: SENDGRID_API_KEY not set in environment variables")
        print("   Please set it in your .env file or Railway dashboard")
        return False
    
    # Initialize email service
    print("\n🔧 Initializing email service...")
    email_service = get_email_service()
    
    if not email_service:
        print("❌ Failed to initialize email service")
        return False
    
    print("✅ Email service initialized")
    
    # Send test email
    print("\n📧 Sending test email to ryan@tactiqal.com...")
    
    subject = "Funnel Analyzer Pro - SendGrid Test Email"
    
    html_content = """
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #6366f1; border-bottom: 3px solid #6366f1; padding-bottom: 12px;">
            🎉 SendGrid is Working!
        </h1>
        
        <p style="font-size: 16px; line-height: 1.6; color: #1f2937;">
            Hey Ryan,
        </p>
        
        <p style="font-size: 16px; line-height: 1.6; color: #1f2937;">
            Great news - your SendGrid integration is properly configured and working! 
            This test email confirms that:
        </p>
        
        <ul style="font-size: 16px; line-height: 1.8; color: #1f2937;">
            <li>✅ SendGrid API key is valid</li>
            <li>✅ Email service is initialized correctly</li>
            <li>✅ Emails can be sent from your backend</li>
            <li>✅ Sender address is properly configured</li>
        </ul>
        
        <div style="background: #f3f4f6; border-left: 4px solid #6366f1; padding: 16px; margin: 24px 0;">
            <p style="margin: 0; font-size: 14px; color: #4b5563;">
                <strong>Next steps:</strong><br>
                Your Funnel Analyzer Pro application can now send analysis results via email.
                When users enter their email address during funnel analysis, they'll receive
                a beautifully formatted report with their scores and recommendations.
            </p>
        </div>
        
        <p style="font-size: 16px; line-height: 1.6; color: #1f2937;">
            Keep crushing it! 🚀
        </p>
        
        <p style="font-size: 14px; color: #6b7280; margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
            Sent from Funnel Analyzer Pro<br>
            This is an automated test email
        </p>
    </div>
    """
    
    try:
        success = await email_service.send_email(
            to_email="ryan@tactiqal.com",
            subject=subject,
            html_content=html_content,
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("\n📬 Check your inbox at ryan@tactiqal.com")
            print("   (Check spam folder if you don't see it)")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(send_test_email())
    sys.exit(0 if success else 1)
