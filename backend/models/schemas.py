"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request body for funnel analysis."""
    
    urls: List[HttpUrl] = Field(..., min_length=1, max_length=10, description="List of funnel URLs to analyze")
    
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


class PageAnalysis(BaseModel):
    """Analysis results for a single page."""
    
    url: str
    page_type: Optional[str] = None
    title: Optional[str] = None
    scores: ScoreBreakdown
    feedback: str
    screenshot_url: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response body for completed analysis."""
    
    analysis_id: int
    overall_score: int = Field(..., ge=0, le=100)
    scores: ScoreBreakdown
    summary: str
    pages: List[PageAnalysis]
    created_at: datetime
    analysis_duration_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True


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
    
    analysis_id: int
    overall_score: int
    urls: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """List of user's past analyses."""
    
    reports: List[ReportListItem]
    total: int
