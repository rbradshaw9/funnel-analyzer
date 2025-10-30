"""Admin routes for user management."""

from __future__ import annotations

import logging
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from ..db.session import get_db_session
from ..models.database import User, Analysis, EmailTemplate
from ..services.auth import validate_jwt_token
from ..services.passwords import hash_password
# from ..services.screenshot_cleanup import ScreenshotCleanupService
from ..services.storage import get_storage_service

router = APIRouter()
logger = logging.getLogger(__name__)


class UserListItem(BaseModel):
    """User list item for admin view."""
    id: int
    email: str
    full_name: Optional[str] = None
    plan: str
    status: str
    role: str
    created_at: datetime
    last_magic_link_sent_at: Optional[datetime] = None
    analysis_count: int = 0
    oauth_provider: Optional[str] = None


class UserDetail(BaseModel):
    """Detailed user information for admin."""
    id: int
    email: str
    full_name: Optional[str] = None
    plan: str
    status: str
    role: str
    status_reason: Optional[str] = None
    subscription_id: Optional[str] = None
    thrivecart_customer_id: Optional[str] = None
    access_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_magic_link_sent_at: Optional[datetime] = None
    oauth_provider: Optional[str] = None
    oauth_provider_id: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    avatar_url: Optional[str] = None
    onboarding_completed: bool = False
    analysis_count: int = 0


class UserUpdate(BaseModel):
    """User update payload."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    plan: Optional[str] = Field(None, pattern="^(free|basic|pro)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended|canceled|past_due)$")
    role: Optional[str] = Field(None, pattern="^(member|admin)$")
    status_reason: Optional[str] = None
    access_expires_at: Optional[datetime] = None


class UserStats(BaseModel):
    """Platform statistics."""
    total_users: int
    active_users: int
    free_users: int
    basic_users: int
    pro_users: int
    total_analyses: int
    analyses_today: int


def _user_to_list_item(user: User, analysis_count: int = 0) -> UserListItem:
    """Convert User ORM object to UserListItem response model."""
    return UserListItem(
        id=int(user.id),  # type: ignore[arg-type]
        email=str(user.email),  # type: ignore[arg-type]
        full_name=str(user.full_name) if user.full_name else None,  # type: ignore[arg-type]
        plan=str(user.plan),  # type: ignore[arg-type]
        status=str(user.status),  # type: ignore[arg-type]
        role=str(user.role),  # type: ignore[arg-type]
        created_at=user.created_at,  # type: ignore[arg-type]
        last_magic_link_sent_at=user.last_magic_link_sent_at,  # type: ignore[arg-type]
        analysis_count=analysis_count,
        oauth_provider=str(user.oauth_provider) if user.oauth_provider else None,  # type: ignore[arg-type]
    )


def _user_to_detail(user: User, analysis_count: int = 0) -> UserDetail:
    """Convert User ORM object to UserDetail response model."""
    return UserDetail(
        id=int(user.id),  # type: ignore[arg-type]
        email=str(user.email),  # type: ignore[arg-type]
        full_name=str(user.full_name) if user.full_name else None,  # type: ignore[arg-type]
        plan=str(user.plan),  # type: ignore[arg-type]
        status=str(user.status),  # type: ignore[arg-type]
        role=str(user.role),  # type: ignore[arg-type]
        status_reason=str(user.status_reason) if user.status_reason else None,  # type: ignore[arg-type]
        subscription_id=str(user.subscription_id) if user.subscription_id else None,  # type: ignore[arg-type]
        thrivecart_customer_id=str(user.thrivecart_customer_id) if user.thrivecart_customer_id else None,  # type: ignore[arg-type]
        access_expires_at=user.access_expires_at,  # type: ignore[arg-type]
        created_at=user.created_at,  # type: ignore[arg-type]
        updated_at=user.updated_at,  # type: ignore[arg-type]
        last_magic_link_sent_at=user.last_magic_link_sent_at,  # type: ignore[arg-type]
        oauth_provider=str(user.oauth_provider) if user.oauth_provider else None,  # type: ignore[arg-type]
        oauth_provider_id=str(user.oauth_provider_id) if user.oauth_provider_id else None,  # type: ignore[arg-type]
        company=str(user.company) if user.company else None,  # type: ignore[arg-type]
        job_title=str(user.job_title) if user.job_title else None,  # type: ignore[arg-type]
        avatar_url=str(user.avatar_url) if user.avatar_url else None,  # type: ignore[arg-type]
        onboarding_completed=bool(user.onboarding_completed),  # type: ignore[arg-type]
        analysis_count=analysis_count,
    )


def _template_to_schema(template: EmailTemplate) -> "EmailTemplateSchema":
    """Convert EmailTemplate ORM object to EmailTemplateSchema response model."""
    return EmailTemplateSchema(
        id=int(template.id),  # type: ignore[arg-type]
        name=str(template.name),  # type: ignore[arg-type]
        subject=str(template.subject),  # type: ignore[arg-type]
        html_content=str(template.html_content),  # type: ignore[arg-type]
        text_content=str(template.text_content),  # type: ignore[arg-type]
        description=str(template.description) if template.description else None,  # type: ignore[arg-type]
        is_custom=bool(template.is_custom),  # type: ignore[arg-type]
        created_at=template.created_at,  # type: ignore[arg-type]
        updated_at=template.updated_at,  # type: ignore[arg-type]
    )


async def require_admin(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Dependency to require admin role."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    token = authorization.replace("Bearer ", "")
    result = await validate_jwt_token(token)
    
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = result.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Type ignore needed for SQLAlchemy Column comparison
    if str(user.role) != "admin":  # type: ignore[arg-type]
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user


@router.get("/stats", response_model=UserStats)
async def get_platform_stats(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Get platform statistics."""
    
    # Total users
    total_result = await session.execute(select(func.count(User.id)))
    total_users = total_result.scalar() or 0
    
    # Active users
    active_result = await session.execute(
        select(func.count(User.id)).where(User.status == "active")
    )
    active_users = active_result.scalar() or 0
    
    # Users by plan
    free_result = await session.execute(
        select(func.count(User.id)).where(User.plan == "free")
    )
    free_users = free_result.scalar() or 0
    
    basic_result = await session.execute(
        select(func.count(User.id)).where(User.plan == "basic")
    )
    basic_users = basic_result.scalar() or 0
    
    pro_result = await session.execute(
        select(func.count(User.id)).where(User.plan == "pro")
    )
    pro_users = pro_result.scalar() or 0
    
    # Total analyses
    total_analyses_result = await session.execute(select(func.count(Analysis.id)))
    total_analyses = total_analyses_result.scalar() or 0
    
    # Analyses today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(func.count(Analysis.id)).where(Analysis.created_at >= today_start)
    )
    analyses_today = today_result.scalar() or 0
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        free_users=free_users,
        basic_users=basic_users,
        pro_users=pro_users,
        total_analyses=total_analyses,
        analyses_today=analyses_today,
    )


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    plan: Optional[str] = Query(None, pattern="^(free|basic|pro)$"),
    status: Optional[str] = Query(None, pattern="^(active|inactive|suspended|canceled|past_due)$"),
    role: Optional[str] = Query(None, pattern="^(member|admin)$"),
    search: Optional[str] = None,
):
    """List all users with optional filtering."""
    
    query = select(User)
    
    # Apply filters
    if plan:
        query = query.where(User.plan == plan)
    if status:
        query = query.where(User.status == status)
    if role:
        query = query.where(User.role == role)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )
    
    # Order by most recent first
    query = query.order_by(User.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    # Get analysis counts for each user
    user_items = []
    for user in users:
        count_result = await session.execute(
            select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
        )
        analysis_count = count_result.scalar() or 0
        
        user_items.append(_user_to_list_item(user, analysis_count))
    
    return user_items


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Get detailed user information."""
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get analysis count
    count_result = await session.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    analysis_count = count_result.scalar() or 0
    
    return _user_to_detail(user, analysis_count)


@router.patch("/users/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Update user information."""
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Apply updates
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    
    await session.commit()
    await session.refresh(user)
    
    logger.info(f"Admin {admin.email} updated user {user.email}: {update_dict}")
    
    # Get analysis count
    count_result = await session.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    analysis_count = count_result.scalar() or 0
    
    return _user_to_detail(user, analysis_count)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Delete a user and all their data."""
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting yourself (type ignore for SQLAlchemy Column comparison)
    if int(user.id) == int(admin.id):  # type: ignore[arg-type]
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Prevent deleting other admins
    if str(user.role) == "admin":  # type: ignore[arg-type]
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    user_email = str(user.email)  # type: ignore[arg-type]
    
    # Delete screenshots from S3 before deleting user
    # TODO: Re-enable screenshot cleanup once async version is implemented
    # storage_service = get_storage_service()
    # if storage_service:
    #     cleanup_service = ScreenshotCleanupService(storage_service)
    #     try:
    #         deleted_count = await cleanup_service.cleanup_user_screenshots(session, user_id)
    #         logger.info(f"Deleted {deleted_count} screenshots for user {user_email}")
    #     except Exception as e:
    #         logger.error(f"Failed to cleanup screenshots for user {user_id}: {e}")
    #         # Continue with user deletion even if screenshot cleanup fails
    
    # Delete user (cascade will handle analyses and pages)
    await session.delete(user)
    await session.commit()
    
    logger.warning(f"Admin {admin.email} deleted user {user_email} (ID: {user_id})")
    
    return {"status": "success", "message": f"User {user_email} deleted"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=8),
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Reset a user's password (admin only)."""
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash and set new password (type ignore for SQLAlchemy Column assignment)
    user.password_hash = hash_password(new_password)  # type: ignore[assignment]
    user.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    
    await session.commit()
    
    logger.warning(f"Admin {admin.email} reset password for user {user.email}")
    
    return {"status": "success", "message": f"Password reset for {user.email}"}


@router.get("/users/{user_id}/analyses")
async def get_user_analyses(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Get all analyses for a specific user."""
    
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await session.execute(
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "overall_score": a.overall_score,
            "status": a.status,
            "urls": a.urls,
            "created_at": a.created_at.isoformat(),
            "analysis_duration_seconds": a.analysis_duration_seconds,
            "error_message": a.error_message,
        }
        for a in analyses
    ]


# Email Template Management


class EmailTemplateSchema(BaseModel):
    """Email template data."""
    id: int
    name: str
    subject: str
    html_content: str
    text_content: str
    description: Optional[str] = None
    is_custom: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class EmailTemplateUpdate(BaseModel):
    """Email template update payload."""
    subject: str
    html_content: str
    text_content: str
    description: Optional[str] = None


@router.get("/email-templates", response_model=List[EmailTemplateSchema])
async def list_email_templates(
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """List all email templates."""
    
    result = await session.execute(select(EmailTemplate).order_by(EmailTemplate.name))
    templates = result.scalars().all()
    
    return [_template_to_schema(t) for t in templates]


@router.get("/email-templates/{template_name}", response_model=EmailTemplateSchema)
async def get_email_template(
    template_name: str,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Get a specific email template."""
    
    result = await session.execute(
        select(EmailTemplate).where(EmailTemplate.name == template_name)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        # Return default template from email_templates.py
        from ..services import email_templates
        
        # Get default template content
        defaults_map = {
            "magic_link": {
                "label": "Magic Link Login",
                "generator": lambda: email_templates.magic_link_email(
                    magic_link_url="https://funnelanalyzerpro.com/auth/magic?token={{MAGIC_LINK_TOKEN}}",
                    expires_minutes=15,
                    user_email="demo@example.com"
                )
            },
            "welcome": {
                "label": "Welcome Email",
                "generator": lambda: email_templates.welcome_email(
                    user_name="Demo User",
                    magic_link_url="https://funnelanalyzerpro.com/dashboard",
                    plan="free"
                )
            },
            "analysis_complete": {
                "label": "Analysis Complete",
                "generator": lambda: email_templates.analysis_complete_email(
                    user_name="Demo User",
                    analysis_url="https://funnelanalyzerpro.com/reports/{{ANALYSIS_ID}}",
                    overall_score=75,
                    top_issue="Improve value proposition clarity"
                )
            },
            "password_reset": {
                "label": "Password Reset",
                "generator": lambda: email_templates.password_reset_email(
                    reset_url="https://funnelanalyzerpro.com/auth/reset-password?token={{RESET_TOKEN}}",
                    user_email="demo@example.com"
                )
            }
        }
        
        if template_name not in defaults_map:
            raise HTTPException(status_code=404, detail="Template not found")
        
        default_data = defaults_map[template_name]["generator"]()
        
        return EmailTemplateSchema(
            id=0,
            name=template_name,
            subject=default_data["subject"],
            html_content=default_data["html"],
            text_content=default_data["text"],
            description=f"Default {defaults_map[template_name]['label']} template",
            is_custom=False,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
        )
    
    return _template_to_schema(template)


@router.put("/email-templates/{template_name}", response_model=EmailTemplateSchema)
async def update_email_template(
    template_name: str,
    update_data: EmailTemplateUpdate,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Update or create an email template."""
    
    result = await session.execute(
        select(EmailTemplate).where(EmailTemplate.name == template_name)
    )
    template = result.scalar_one_or_none()
    
    if template:
        # Update existing (type ignores for SQLAlchemy Column assignment)
        template.subject = update_data.subject  # type: ignore[assignment]
        template.html_content = update_data.html_content  # type: ignore[assignment]
        template.text_content = update_data.text_content  # type: ignore[assignment]
        template.description = update_data.description  # type: ignore[assignment]
        template.is_custom = 1  # type: ignore[assignment]
        template.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    else:
        # Create new
        template = EmailTemplate(
            name=template_name,
            subject=update_data.subject,
            html_content=update_data.html_content,
            text_content=update_data.text_content,
            description=update_data.description,
            is_custom=1,
        )
        session.add(template)
    
    await session.commit()
    await session.refresh(template)
    
    logger.info(f"Admin {admin.email} updated email template {template_name}")
    
    return _template_to_schema(template)


@router.delete("/email-templates/{template_name}")
async def delete_email_template(
    template_name: str,
    session: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
):
    """Delete a custom email template (revert to default)."""
    
    result = await session.execute(
        select(EmailTemplate).where(EmailTemplate.name == template_name)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await session.delete(template)
    await session.commit()
    
    logger.info(f"Admin {admin.email} deleted custom template {template_name} (reverted to default)")
    
    return {"status": "success", "message": f"Template {template_name} reverted to default"}

