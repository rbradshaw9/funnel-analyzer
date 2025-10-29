"""Email testing endpoint for verifying SendGrid configuration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from ..services.email import get_email_service

router = APIRouter(prefix="/api/test", tags=["testing"])


class TestEmailRequest(BaseModel):
    """Request to send a test email."""
    to_email: EmailStr


@router.post("/send-email")
async def send_test_email(request: TestEmailRequest):
    """
    Send a test email to verify SendGrid configuration.
    
    This endpoint can be used to test that:
    - SendGrid API key is properly configured
    - Email service is initialized
    - Emails can be sent successfully
    """
    email_service = get_email_service()
    
    if not email_service:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Please set SENDGRID_API_KEY environment variable."
        )
    
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
    
    success = await email_service.send_email(
        to_email=request.to_email,
        subject=subject,
        html_content=html_content,
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check server logs for details."
        )
    
    return {
        "status": "sent",
        "message": f"Test email sent to {request.to_email}",
        "recipient": request.to_email
    }
