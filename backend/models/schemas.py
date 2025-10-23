"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator, EmailStr, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request body for funnel analysis."""
    
    urls: List[HttpUrl] = Field(..., min_length=1, max_length=10, description="List of funnel URLs to analyze")
    email: Optional[EmailStr] = Field(default=None, description="Optional email to receive the report")
    
    @field_validator('urls')
    @classmethod
    def validate_urls(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 URLs allowed per analysis")
        return v


class ScoreBreakdown(BaseModel):
    """Individual scores for funnel aspects."""
    
    clarity: int = Field(..., ge=0, le=100, description="Clarity score (0-100)")
    value: int = Field(..., ge=0, le=100, description="Value proposition score (0-100)")
    proof: int = Field(..., ge=0, le=100, description="Social proof score (0-100)")
    design: int = Field(..., ge=0, le=100, description="Design quality score (0-100)")
    flow: int = Field(..., ge=0, le=100, description="Flow and continuity score (0-100)")


class CTARecommendation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cta_copy: str = Field(..., alias="copy", serialization_alias="copy")
    location: Optional[str] = None
    reason: Optional[str] = None


class DesignImprovement(BaseModel):
    area: Optional[str] = None
    recommendation: str
    impact: Optional[str] = None


class TrustElementRecommendation(BaseModel):
    element: str
    why: Optional[str] = None


class ABTestPlan(BaseModel):
    element: Optional[str] = None
    control: Optional[str] = None
    variant: Optional[str] = None
    expected_lift: Optional[str] = None
    reasoning: Optional[str] = None


class PriorityAlert(BaseModel):
    severity: Optional[str] = None
    issue: str
    impact: Optional[str] = None
    fix: Optional[str] = None


class FunnelFlowGap(BaseModel):
    step: Optional[str] = None
    issue: str
    fix: Optional[str] = None


class CopyDiagnostics(BaseModel):
    hook: Optional[str] = None
    offer: Optional[str] = None
    urgency: Optional[str] = None
    objections: Optional[str] = None
    audience_fit: Optional[str] = None


class VisualDiagnostics(BaseModel):
    hero: Optional[str] = None
    layout: Optional[str] = None
    contrast: Optional[str] = None
    mobile: Optional[str] = None
    credibility: Optional[str] = None


class VideoRecommendation(BaseModel):
    context: Optional[str] = None
    recommendation: str


class PageAnalysis(BaseModel):
    """Analysis results for a single page."""
    
    url: str
    page_type: Optional[str] = None
    title: Optional[str] = None
    scores: ScoreBreakdown
    feedback: str
    screenshot_url: Optional[str] = None
    headline_recommendation: Optional[str] = None
    cta_recommendations: Optional[List[CTARecommendation]] = None
    design_improvements: Optional[List[DesignImprovement]] = None
    trust_elements_missing: Optional[List[TrustElementRecommendation]] = None
    ab_test_priority: Optional[ABTestPlan] = None
    priority_alerts: Optional[List[PriorityAlert]] = None
    funnel_flow_gaps: Optional[List[FunnelFlowGap]] = None
    copy_diagnostics: Optional[CopyDiagnostics] = None
    visual_diagnostics: Optional[VisualDiagnostics] = None
    video_recommendations: Optional[List[VideoRecommendation]] = None
    email_capture_recommendations: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    """Response body for completed analysis."""
    
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    overall_score: int = Field(..., ge=0, le=100)
    scores: ScoreBreakdown
    summary: str
    pages: List[PageAnalysis]
    created_at: datetime
    analysis_duration_seconds: Optional[int] = None
    recipient_email: Optional[EmailStr] = None
    

class AnalysisEmailRequest(BaseModel):
    """Payload for requesting an email delivery of an analysis."""

    email: EmailStr


class AuthValidateRequest(BaseModel):
    """JWT validation request."""
    
    token: str = Field(..., description="JWT token from WordPress or manual login")


class AuthValidateResponse(BaseModel):
    """JWT validation response."""
    
    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    message: Optional[str] = None


class ReportListItem(BaseModel):
    """Summary of a single analysis report."""
    
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    overall_score: int
    urls: List[str]
    created_at: datetime


class ReportListResponse(BaseModel):
    """List of user's past analyses."""
    
    reports: List[ReportListItem]
    total: int
