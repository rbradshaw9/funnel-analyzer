"""Debug endpoints for testing system functionality."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from ..services.notifications import send_analysis_email
from ..models.schemas import AnalysisResponse, ScoreBreakdown, PageAnalysis
from ..utils.config import settings
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class TestEmailRequest(BaseModel):
    email: EmailStr


@router.post("/test-email")
async def test_email_delivery(request: TestEmailRequest):
    """Test email delivery with a sample analysis report."""
    
    # Create a mock analysis result for testing
    mock_analysis = AnalysisResponse(
        analysis_id=12345,
        overall_score=85,
        scores=ScoreBreakdown(
            clarity=90,
            value=85,
            proof=80,
            design=88,
            flow=82
        ),
        summary="""
        **Overall Assessment**: Your funnel demonstrates strong performance with clear messaging and professional design. The value proposition is well-communicated and trust elements are effectively placed.
        
        **Key Strengths**: Excellent visual hierarchy, compelling headlines, and smooth user flow. The CTA placement is strategic and the design maintains consistency throughout.
        
        **Primary Opportunity**: Enhance social proof elements on the landing page to increase credibility and conversion rates. Adding customer testimonials with photos could boost conversions by 15-20%.
        
        **Quick Wins**: Optimize CTA button copy for urgency, add testimonials above the fold, and implement exit-intent popup for cart abandonment recovery.
        
        **Strategic Recommendation**: Consider A/B testing different headline variations to maximize impact and implement progressive profiling in your lead capture process.
        """,
        pages=[
            PageAnalysis(
                url="https://example.com/landing",
                title="Landing Page - Product Launch",
                page_type="landing_page",
                scores=ScoreBreakdown(
                    clarity=90,
                    value=85,
                    proof=80,
                    design=88,
                    flow=82
                ),
                feedback="Strong landing page with clear value proposition and effective visual hierarchy."
            ),
            PageAnalysis(
                url="https://example.com/checkout",
                title="Checkout Page",
                page_type="order_form", 
                scores=ScoreBreakdown(
                    clarity=85,
                    value=88,
                    proof=85,
                    design=90,
                    flow=87
                ),
                feedback="Clean checkout process with minimal friction and clear pricing."
            )
        ],
        created_at=datetime.now(),
        analysis_duration_seconds=45
    )
    
    logger.info(f"🧪 Testing email delivery to: {request.email}")
    
    try:
        # Test email service configuration
        from ..services.email import get_email_service
        email_service = get_email_service()
        
        if not email_service:
            return {
                "status": "error",
                "message": "Email service not configured",
                "details": {
                    "sendgrid_api_key": "Not configured" if not settings.SENDGRID_API_KEY else f"Configured ({len(settings.SENDGRID_API_KEY)} characters)",
                    "default_from": settings.EMAIL_DEFAULT_FROM,
                    "default_reply_to": settings.EMAIL_DEFAULT_REPLY_TO
                }
            }
        
        # Attempt to send test email
        sent = await send_analysis_email(
            recipient_email=request.email,
            analysis=mock_analysis
        )
        
        if sent:
            return {
                "status": "success",
                "message": f"Test email sent successfully to {request.email}",
                "details": {
                    "sendgrid_configured": True,
                    "email_service_available": True,
                    "from_email": settings.EMAIL_DEFAULT_FROM,
                    "api_key_length": len(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else 0
                }
            }
        else:
            return {
                "status": "error", 
                "message": "Email sending failed - check logs for details",
                "details": {
                    "sendgrid_configured": bool(settings.SENDGRID_API_KEY),
                    "email_service_available": True,
                    "possible_issues": [
                        "Invalid SendGrid API key",
                        "Sender email not authenticated",
                        "Domain not verified",
                        "Rate limiting"
                    ]
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Test email failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Email test failed with exception: {str(e)}",
            "details": {
                "exception_type": type(e).__name__,
                "sendgrid_configured": bool(settings.SENDGRID_API_KEY),
                "from_email": settings.EMAIL_DEFAULT_FROM
            }
        }


@router.get("/email-config")
async def get_email_config():
    """Get current email configuration status (without exposing sensitive data)."""
    
    from ..services.email import get_email_service
    email_service = get_email_service()
    
    return {
        "email_service_available": email_service is not None,
        "sendgrid_api_key_configured": bool(settings.SENDGRID_API_KEY),
        "api_key_length": len(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else 0,
        "api_key_prefix": settings.SENDGRID_API_KEY[:10] + "..." if settings.SENDGRID_API_KEY else None,
        "default_from_email": settings.EMAIL_DEFAULT_FROM,
        "default_reply_to": settings.EMAIL_DEFAULT_REPLY_TO,
        "has_sendgrid_dependency": True  # We checked this in requirements.txt
    }