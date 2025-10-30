"""
Service for gating features and content based on user plan level.
Implements freemium model with Basic and Pro tiers.
"""

from datetime import datetime
from typing import Optional
from ..models.schemas import AnalysisResponse, PageAnalysis, ScoreBreakdown


PLAN_HIERARCHY = {
    "free": 0,
    "basic": 1,
    "pro": 2,
    "growth": 2,  # Alias for pro
}


def get_plan_level(plan: Optional[str]) -> int:
    """Convert plan string to numeric level for comparison."""
    if not plan:
        return 0
    return PLAN_HIERARCHY.get(plan.lower(), 0)


def filter_analysis_by_plan(analysis: AnalysisResponse, user_plan: Optional[str] = None) -> AnalysisResponse:
    """
    Filter analysis response based on user's plan level.
    
    Free users get:
    - Overall score
    - Basic score breakdown (clarity, value, proof, design, flow)
    - Short summary (first 200 characters)
    - Limited feedback (first 300 characters per page)
    
    Basic users get:
    - Everything free users get
    - Full summary
    - Full feedback
    - Screenshots
    - Headline recommendations
    - CTA recommendations
    - Basic design improvements
    
    Pro users get:
    - Everything (no filtering)
    """
    
    plan_level = get_plan_level(user_plan)
    
    # Pro users get everything
    if plan_level >= PLAN_HIERARCHY["pro"]:
        return analysis
    
    # Handle both dict and object analysis formats
    pages = analysis.get("pages", []) if isinstance(analysis, dict) else getattr(analysis, "pages", [])
    
    # Filter pages based on plan
    filtered_pages = []
    for page in pages:
        # Handle both dict and object page formats
        def get_field(obj, field, default=None):
            if isinstance(obj, dict):
                return obj.get(field, default)
            return getattr(obj, field, default)
        
        if plan_level >= PLAN_HIERARCHY["basic"]:
            # Basic users: Keep most fields but hide advanced recommendations
            filtered_pages.append(
                PageAnalysis(
                    url=get_field(page, "url") or "",
                    page_type=get_field(page, "page_type"),
                    title=get_field(page, "title"),
                    scores=get_field(page, "scores") or {},  # type: ignore
                    feedback=get_field(page, "feedback") or "",
                    screenshot_url=get_field(page, "screenshot_url"),
                    screenshot_storage_key=get_field(page, "screenshot_storage_key"),
                    headline_recommendation=get_field(page, "headline_recommendation"),
                    cta_recommendations=get_field(page, "cta_recommendations"),
                    design_improvements=get_field(page, "design_improvements"),
                    # Hide pro-only features
                    trust_elements_missing=None,
                    ab_test_priority=None,
                    priority_alerts=None,
                    funnel_flow_gaps=None,
                    copy_diagnostics=None,
                    visual_diagnostics=None,
                    video_recommendations=None,
                    email_capture_recommendations=None,
                )
            )
        else:
            # Free users: Only basic info
            # Truncate feedback to 300 characters
            feedback = get_field(page, "feedback") or ""
            truncated_feedback = feedback[:300] + "..." if len(feedback) > 300 else feedback
            
            filtered_pages.append(
                PageAnalysis(
                    url=get_field(page, "url") or "",
                    page_type=get_field(page, "page_type"),
                    title=get_field(page, "title"),
                    scores=get_field(page, "scores") or {},  # type: ignore
                    feedback=truncated_feedback,
                    # Hide all premium features
                    screenshot_url=None,
                    screenshot_storage_key=None,
                    headline_recommendation=None,
                    cta_recommendations=None,
                    design_improvements=None,
                    trust_elements_missing=None,
                    ab_test_priority=None,
                    priority_alerts=None,
                    funnel_flow_gaps=None,
                    copy_diagnostics=None,
                    visual_diagnostics=None,
                    video_recommendations=None,
                    email_capture_recommendations=None,
                )
            )
    
    # Filter summary for free users
    def get_analysis_field(field, default=None):
        if isinstance(analysis, dict):
            return analysis.get(field, default)
        return getattr(analysis, field, default)
    
    summary = get_analysis_field("summary", "")
    if plan_level < PLAN_HIERARCHY["basic"]:
        summary = summary[:200] + "..." if len(summary) > 200 else summary
    
    # Create filtered response
    is_limited = plan_level < PLAN_HIERARCHY["pro"]
    upgrade_message = get_upgrade_message(user_plan) if is_limited else None
    
    return AnalysisResponse(
        analysis_id=get_analysis_field("analysis_id") or 0,
        overall_score=get_analysis_field("overall_score") or 0,
        scores=get_analysis_field("scores") or {},  # type: ignore
        summary=summary,
        pages=filtered_pages,
        created_at=get_analysis_field("created_at") or datetime.now(),
        analysis_duration_seconds=get_analysis_field("analysis_duration_seconds"),
        recipient_email=get_analysis_field("recipient_email"),
        pipeline_metrics=get_analysis_field("pipeline_metrics"),
        is_limited=is_limited,
        upgrade_message=upgrade_message,
    )


def should_show_upgrade_prompt(user_plan: Optional[str]) -> bool:
    """Determine if user should see upgrade prompts."""
    plan_level = get_plan_level(user_plan)
    return plan_level < PLAN_HIERARCHY["pro"]


def get_upgrade_message(user_plan: Optional[str]) -> str:
    """Get appropriate upgrade message based on current plan."""
    plan_level = get_plan_level(user_plan)
    
    if plan_level < PLAN_HIERARCHY["basic"]:
        return "Upgrade to Basic or Pro to unlock full reports with screenshots, detailed recommendations, and A/B testing suggestions."
    elif plan_level < PLAN_HIERARCHY["pro"]:
        return "Upgrade to Pro for advanced diagnostics, video recommendations, and priority support."
    
    return ""
