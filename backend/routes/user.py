"""User profile management endpoints."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import User
from ..services.auth import validate_jwt_token

router = APIRouter()
logger = logging.getLogger(__name__)


class UpdateProfileRequest(BaseModel):
    """Payload for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    onboarding_completed: Optional[bool] = None


class ProfileResponse(BaseModel):
    """User profile data response."""

    user_id: int
    email: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    avatar_url: Optional[str] = None
    onboarding_completed: bool = False
    plan: str
    status: str


async def get_current_user(request: Request, session: AsyncSession) -> User:
    """Extract and validate user from Authorization header."""
    
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Validate the token
    validation = await validate_jwt_token(token)
    if not validation.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = validation.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Get user from database
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """Get current user's profile information."""
    
    user = await get_current_user(request, session)
    
    return ProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        onboarding_completed=bool(user.onboarding_completed),
        plan=user.plan or "free",
        status=user.status or "active",
    )


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    request_body: UpdateProfileRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """Update current user's profile information."""
    
    user = await get_current_user(request, session)
    
    # Update fields if provided
    if request_body.full_name is not None:
        user.full_name = request_body.full_name
    
    if request_body.company is not None:
        user.company = request_body.company
    
    if request_body.job_title is not None:
        user.job_title = request_body.job_title
    
    if request_body.onboarding_completed is not None:
        user.onboarding_completed = 1 if request_body.onboarding_completed else 0
    
    await session.commit()
    await session.refresh(user)
    
    logger.info(f"Profile updated for user {user.email}")
    
    return ProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        onboarding_completed=bool(user.onboarding_completed),
        plan=user.plan or "free",
        status=user.status or "active",
    )
