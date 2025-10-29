"""
Service for gating features and content based on user plan level.
Implements freemium model with Basic and Pro tiers.
"""

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
    
    # Filter pages based on plan
    filtered_pages = []
    for page in analysis.pages:
        if plan_level >= PLAN_HIERARCHY["basic"]:
            # Basic users: Keep most fields but hide advanced recommendations
            filtered_pages.append(
                PageAnalysis(
                    url=page.url,
                    page_type=page.page_type,
                    title=page.title,
                    scores=page.scores,
                    feedback=page.feedback,
                    screenshot_url=page.screenshot_url,
                    screenshot_storage_key=page.screenshot_storage_key,
                    headline_recommendation=page.headline_recommendation,
                    cta_recommendations=page.cta_recommendations,
                    design_improvements=page.design_improvements,
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
            truncated_feedback = page.feedback[:300] + "..." if len(page.feedback) > 300 else page.feedback
            
            filtered_pages.append(
                PageAnalysis(
                    url=page.url,
                    page_type=page.page_type,
                    title=page.title,
                    scores=page.scores,
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
    summary = analysis.summary
    if plan_level < PLAN_HIERARCHY["basic"]:
        summary = analysis.summary[:200] + "..." if len(analysis.summary) > 200 else analysis.summary
    
    # Create filtered response
    is_limited = plan_level < PLAN_HIERARCHY["pro"]
    upgrade_message = get_upgrade_message(user_plan) if is_limited else None
    
    return AnalysisResponse(
        analysis_id=analysis.analysis_id,
        overall_score=analysis.overall_score,
        scores=analysis.scores,
        summary=summary,
        pages=filtered_pages,
        created_at=analysis.created_at,
        analysis_duration_seconds=analysis.analysis_duration_seconds,
        recipient_email=analysis.recipient_email,
        pipeline_metrics=analysis.pipeline_metrics,
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
