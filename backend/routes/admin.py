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
from ..models.database import User, Analysis
from ..services.auth import validate_jwt_token
from ..services.passwords import hash_password

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
    
    if user.role != "admin":
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
        
        user_items.append(UserListItem(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            plan=user.plan,
            status=user.status,
            role=user.role,
            created_at=user.created_at,
            last_magic_link_sent_at=user.last_magic_link_sent_at,
            analysis_count=analysis_count,
            oauth_provider=user.oauth_provider,
        ))
    
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
    
    return UserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        plan=user.plan,
        status=user.status,
        role=user.role,
        status_reason=user.status_reason,
        subscription_id=user.subscription_id,
        thrivecart_customer_id=user.thrivecart_customer_id,
        access_expires_at=user.access_expires_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_magic_link_sent_at=user.last_magic_link_sent_at,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        company=user.company,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        onboarding_completed=bool(user.onboarding_completed),
        analysis_count=analysis_count,
    )


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
    
    user.updated_at = datetime.now(timezone.utc)
    
    await session.commit()
    await session.refresh(user)
    
    logger.info(f"Admin {admin.email} updated user {user.email}: {update_dict}")
    
    # Get analysis count
    count_result = await session.execute(
        select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    )
    analysis_count = count_result.scalar() or 0
    
    return UserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        plan=user.plan,
        status=user.status,
        role=user.role,
        status_reason=user.status_reason,
        subscription_id=user.subscription_id,
        thrivecart_customer_id=user.thrivecart_customer_id,
        access_expires_at=user.access_expires_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_magic_link_sent_at=user.last_magic_link_sent_at,
        oauth_provider=user.oauth_provider,
        oauth_provider_id=user.oauth_provider_id,
        company=user.company,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        onboarding_completed=bool(user.onboarding_completed),
        analysis_count=analysis_count,
    )


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
    
    # Prevent deleting yourself
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Prevent deleting other admins
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    user_email = user.email
    
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
    
    # Hash and set new password
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    
    await session.commit()
    
    logger.warning(f"Admin {admin.email} reset password for user {user.email}")
    
    return {"status": "success", "message": f"Password reset for {user.email}"}
