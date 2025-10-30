"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


IndustryType = Literal[
    "ecommerce", 
    "saas", 
    "coaching", 
    "consulting", 
    "lead_generation", 
    "affiliate_marketing",
    "course_creation",
    "agency",
    "other"
]

class AnalysisRequest(BaseModel):
    """Request body for funnel analysis."""
    
    urls: List[HttpUrl] = Field(..., min_length=1, max_length=10, description="List of funnel URLs to analyze")
    email: Optional[EmailStr] = Field(default=None, description="Optional email to receive the report")
    industry: Optional[IndustryType] = Field(default="other", description="Industry type for tailored recommendations")
    name: Optional[str] = Field(default=None, max_length=255, description="Optional name for this analysis")
    parent_analysis_id: Optional[int] = Field(default=None, description="ID of original analysis if this is a re-run")
    
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


class PipelineStageTimings(BaseModel):
    scrape_seconds: Optional[float] = Field(default=None, ge=0, description="Time spent scraping URLs")
    analysis_seconds: Optional[float] = Field(default=None, ge=0, description="Time spent in LLM analysis")
    screenshot_seconds: Optional[float] = Field(default=None, ge=0, description="Time spent awaiting screenshots")
    total_seconds: Optional[float] = Field(default=None, ge=0, description="Total pipeline duration")


class ScreenshotPipelineMetrics(BaseModel):
    attempted: int = Field(default=0, ge=0)
    succeeded: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    uploaded: int = Field(default=0, ge=0)
    timeouts: int = Field(default=0, ge=0)


class PipelineTelemetry(BaseModel):
    stage_timings: Optional[PipelineStageTimings] = None
    screenshot: Optional[ScreenshotPipelineMetrics] = None
    llm_provider: Optional[str] = None
    notes: Optional[List[str]] = None


class PerformanceData(BaseModel):
    """Core Web Vitals and performance metrics."""
    
    lcp: Optional[float] = None  # Largest Contentful Paint
    fid: Optional[float] = None  # First Input Delay (or TBT)
    cls: Optional[float] = None  # Cumulative Layout Shift
    fcp: Optional[float] = None  # First Contentful Paint
    speed_index: Optional[float] = None
    performance_score: Optional[int] = Field(default=None, ge=0, le=100)
    accessibility_score: Optional[int] = Field(default=None, ge=0, le=100)
    best_practices_score: Optional[int] = Field(default=None, ge=0, le=100)
    seo_score: Optional[int] = Field(default=None, ge=0, le=100)
    opportunities: Optional[List[str]] = None
    opportunity_details: Optional[List[Dict[str, Any]]] = None
    core_web_vitals: Optional[Dict[str, Dict[str, Any]]] = None
    analysis_timestamp: Optional[str] = None
    url: Optional[str] = None
    

class SourceAnalysis(BaseModel):
    """Technical SEO and tracking analysis."""
    
    tracking_pixels: Optional[List[str]] = None
    structured_data: Optional[List[str]] = None
    technical_score: Optional[int] = Field(default=None, ge=0, le=100)
    seo_issues: Optional[List[str]] = None
    conversion_tracking: Optional[List[str]] = None


class PageAnalysis(BaseModel):
    """Analysis results for a single page."""
    
    url: str
    page_type: Optional[str] = None
    title: Optional[str] = None
    scores: ScoreBreakdown
    feedback: str
    screenshot_url: Optional[str] = None
    screenshot_storage_key: Optional[str] = None
    headline_recommendation: Optional[str] = None
    headline_alternatives: Optional[List[str]] = None  # 3-5 alternative headline options
    cta_recommendations: Optional[List[CTARecommendation]] = None
    design_improvements: Optional[List[DesignImprovement]] = None
    copy_improvements: Optional[List[dict]] = None  # Before/after copy examples
    trust_elements_missing: Optional[List[TrustElementRecommendation]] = None
    ab_test_priority: Optional[ABTestPlan] = None
    priority_alerts: Optional[List[PriorityAlert]] = None
    funnel_flow_gaps: Optional[List[FunnelFlowGap]] = None
    copy_diagnostics: Optional[CopyDiagnostics] = None
    visual_diagnostics: Optional[VisualDiagnostics] = None
    video_recommendations: Optional[List[VideoRecommendation]] = None
    email_capture_recommendations: Optional[List[str]] = None
    performance_data: Optional[PerformanceData] = None
    source_analysis: Optional[SourceAnalysis] = None


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
    pipeline_metrics: Optional[PipelineTelemetry] = None
    is_limited: Optional[bool] = None  # Whether content is limited by plan
    upgrade_message: Optional[str] = None  # Upgrade prompt message
    name: Optional[str] = None  # Optional user-provided name
    parent_analysis_id: Optional[int] = None  # For tracking re-runs
    urls: Optional[List[str]] = None  # Store URLs for re-run functionality
    

class AnalysisEmailRequest(BaseModel):
    """Payload for requesting an email delivery of an analysis."""

    email: EmailStr


class MagicLinkRequest(BaseModel):
    """Payload to request a magic-link email."""

    email: EmailStr = Field(..., description="Email address to receive the magic link")


class MagicLinkResponse(BaseModel):
    """Response after attempting to send a magic-link email."""

    status: Literal["sent", "skipped"]
    message: Optional[str] = None


class AuthValidateRequest(BaseModel):
    """JWT validation request."""
    
    token: str = Field(..., description="JWT token from WordPress or manual login")


class AuthValidateResponse(BaseModel):
    """JWT validation response."""
    
    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    message: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    access_granted: bool = False
    access_expires_at: Optional[datetime] = None
    portal_update_url: Optional[str] = None
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    has_password: Optional[bool] = None  # Whether user has set a password


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


class ReportDeleteResponse(BaseModel):
    """Deletion outcome when removing a stored analysis."""

    status: Literal["deleted"]
    analysis_id: int
    assets_total: int
    assets_deleted: int
    assets_failed: int
    assets_skipped: int
    storage_available: bool


class MemberRegistrationRequest(BaseModel):
    """Payload for creating a password-based member account."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=255)


class MemberLoginRequest(BaseModel):
    """Credentials used for authenticating an existing member."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class SessionResponse(BaseModel):
    """Standard bearer token envelope returned after authentication."""

    access_token: str
    refresh_token: str = Field(..., description="Refresh token for obtaining new access tokens")
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., ge=0, description="Token lifetime in seconds")
    user_id: int
    email: EmailStr
    plan: str = Field(..., description="Member plan identifier")


class MemberRegistrationResponse(SessionResponse):
    """Registration response containing the initial session token."""

    status: Literal["registered"] = "registered"


class MemberLoginResponse(SessionResponse):
    """Login response containing a refreshed session token."""

    status: Literal["authenticated"] = "authenticated"


class AdminLoginRequest(BaseModel):
    """Payload for admin credential login."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AdminLoginResponse(BaseModel):
    """Bearer token issued after successful admin login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., ge=0, description="Token lifetime in seconds")


class RefreshTokenRequest(BaseModel):
    """Payload for refresh token request."""

    refresh_token: str = Field(..., description="The refresh token to exchange for a new access token")


class RefreshTokenResponse(BaseModel):
    """Response containing new access token and optionally new refresh token."""

    access_token: str
    refresh_token: str = Field(..., description="New refresh token (tokens are rotated on use)")
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., ge=0, description="Access token lifetime in seconds")


class SetPasswordRequest(BaseModel):
    """Payload for setting a password on an account that doesn't have one."""

    password: str = Field(..., min_length=8, max_length=128, description="New password to set")


class SetPasswordResponse(BaseModel):
    """Response after successfully setting a password."""

    status: Literal["password_set"] = "password_set"
    message: str = "Password has been set successfully"


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password reset flow."""

    email: EmailStr = Field(..., description="Email address for password reset")


class ForgotPasswordResponse(BaseModel):
    """Response after password reset email sent."""

    status: Literal["email_sent"] = "email_sent"
    message: str = "If an account exists with this email, a password reset link has been sent"


class ResetPasswordRequest(BaseModel):
    """Request to reset password with token."""

    token: str = Field(..., min_length=1, description="Password reset token from email")
    password: str = Field(..., min_length=8, max_length=128, description="New password")


class ResetPasswordResponse(BaseModel):
    """Response after successful password reset."""

    status: Literal["password_reset"] = "password_reset"
    message: str = "Password has been reset successfully"


class PublicStatsResponse(BaseModel):
    """Aggregate statistics suitable for public surfaces."""

    analyses_run: int = Field(default=0, ge=0)
    pages_analyzed: int = Field(default=0, ge=0)


# ============================================================================
# Conversion Tracking Schemas
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request to create or update a funnel session."""
    
    session_id: str = Field(..., min_length=1, max_length=255, description="Client-generated session UUID")
    fingerprint: Optional[str] = Field(default=None, description="Device fingerprint hash")
    
    # Optional visitor information
    email: Optional[EmailStr] = Field(default=None, description="Email captured at opt-in")
    user_id: Optional[str] = Field(default=None, max_length=255, description="External user ID if authenticated")
    order_id: Optional[str] = Field(default=None, max_length=255, description="Order ID if tracked through funnel")
    
    # Session metadata
    landing_page: Optional[str] = Field(default=None, max_length=2048, description="First page URL")
    referrer: Optional[str] = Field(default=None, max_length=2048, description="HTTP referrer")
    utm_source: Optional[str] = Field(default=None, max_length=255)
    utm_medium: Optional[str] = Field(default=None, max_length=255)
    utm_campaign: Optional[str] = Field(default=None, max_length=255)
    utm_content: Optional[str] = Field(default=None, max_length=255)
    utm_term: Optional[str] = Field(default=None, max_length=255)
    
    # Device/browser info
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=1024)
    screen_resolution: Optional[str] = Field(default=None, max_length=50)
    timezone: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=50)


class SessionEventRequest(BaseModel):
    """Request to track an event within a session."""
    
    session_id: str = Field(..., min_length=1, max_length=255, description="Session UUID")
    event_type: str = Field(..., max_length=100, description="Event type (pageview, click, submit, etc.)")
    page_url: Optional[str] = Field(default=None, max_length=2048, description="Current page URL")
    target: Optional[str] = Field(default=None, max_length=500, description="Event target (button ID, form name, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event data")


class ConversionWebhookRequest(BaseModel):
    """Webhook payload for conversion tracking."""
    
    # Required fields
    conversion_id: str = Field(..., min_length=1, max_length=255, description="Unique order/conversion ID")
    
    # Attribution data (at least one recommended)
    email: Optional[EmailStr] = Field(default=None, description="Customer email")
    session_id: Optional[str] = Field(default=None, max_length=255, description="Client session UUID if tracked")
    order_id: Optional[str] = Field(default=None, max_length=255, description="Order ID if different from conversion_id")
    user_id: Optional[str] = Field(default=None, max_length=255, description="User ID if authenticated")
    
    # Conversion details
    revenue: Optional[float] = Field(default=None, ge=0, description="Revenue amount in dollars")
    currency: str = Field(default="USD", max_length=10, description="Currency code")
    customer_name: Optional[str] = Field(default=None, max_length=255, description="Customer full name")
    product_name: Optional[str] = Field(default=None, max_length=500, description="Product/service name")
    
    # Source tracking
    webhook_source: Optional[str] = Field(default="manual", max_length=100, description="stripe, infusionsoft, etc.")
    
    # Optional device info for probabilistic matching
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=1024)
    
    # Timestamp
    converted_at: Optional[datetime] = Field(default=None, description="Conversion timestamp (UTC)")


class ConversionResponse(BaseModel):
    """Response after processing a conversion webhook."""
    
    conversion_id: str
    attributed: bool = Field(..., description="Whether we successfully matched to a session")
    attribution_method: Optional[str] = Field(default=None, description="How we matched the conversion")
    attribution_confidence: Optional[int] = Field(default=None, ge=0, le=100, description="Confidence score 0-100")
    session_id: Optional[str] = Field(default=None, description="Matched session ID if found")
    message: str = Field(default="Conversion recorded")


class FunnelSessionResponse(BaseModel):
    """Response after creating/updating a funnel tracking session."""
    
    session_id: str
    fingerprint: str
    analysis_id: int
    created: bool = Field(..., description="True if new session, False if updated")
    message: str = Field(default="Session tracked")


class ConversionStatsResponse(BaseModel):
    """Statistics about conversions for an analysis."""
    
    total_conversions: int = Field(default=0, ge=0)
    attributed_conversions: int = Field(default=0, ge=0)
    attribution_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage attributed")
    total_revenue: float = Field(default=0.0, ge=0.0, description="Total revenue in dollars")
    
    # Attribution breakdown
    attribution_methods: Dict[str, int] = Field(default_factory=dict, description="Count by method")
    avg_confidence: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Average confidence score")
    
    # Session stats
    total_sessions: int = Field(default=0, ge=0)
    conversion_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Conversions / Sessions %")

