"""Authentication endpoints for magic-link login and token validation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import User
from ..models.schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    AuthValidateRequest,
    AuthValidateResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    MemberLoginRequest,
    MemberLoginResponse,
    MemberRegistrationRequest,
    MemberRegistrationResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SetPasswordRequest,
    SetPasswordResponse,
)
from ..services.auth import create_jwt_token, create_magic_link_token, create_refresh_token, validate_jwt_token, validate_refresh_token
from ..services.email import get_email_service
from ..services.email_templates import magic_link_email
from ..services.onboarding import send_magic_link_onboarding
from ..services.passwords import hash_password, verify_password
from ..utils.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_email(value: str) -> str:
    return value.strip().lower()


async def _get_or_create_user(session: AsyncSession, email: str) -> User:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(email=email)
    session.add(user)
    await session.flush()
    logger.info("Created new user record for %s", email)
    return user


def _access_granted(user: User) -> bool:
    if user.status != "active":
        return False
    if user.access_expires_at:
        expires_at = user.access_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if expires_at <= now:
            return False
    return True


def _build_portal_message(status: str | None) -> str:
    if status == "past_due":
        return "Payment required"
    if status == "canceled":
        return "Subscription canceled"
    return "Token is valid"


def _build_session_payload(*, user: User, token: str, refresh_token: str, expires_delta: timedelta) -> dict:
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "expires_in": int(expires_delta.total_seconds()),
        "user_id": user.id,
        "email": user.email,
        "plan": user.plan,
    }


@router.post("/register", response_model=MemberRegistrationResponse, status_code=201)
async def register_member(
    request: MemberRegistrationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a password-based member account."""

    email = _normalize_email(request.email)

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    if result.scalar_one_or_none() is not None:
        logger.info("Registration attempt rejected for existing email %s", email)
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = hash_password(request.password)

    user = User(
        email=email,
        full_name=request.full_name,
        password_hash=password_hash,
        plan="free",
        status="active",
        is_active=1,
        role="member",
    )

    session.add(user)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        logger.info("Registration race condition detected for %s", email)
        raise HTTPException(status_code=409, detail="Email already registered")

    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    token = await create_jwt_token(
        user.id,
        user.email,
        expires_in=expires_delta,
        token_type="session",
    )
    
    # Create refresh token
    refresh_token, refresh_hash = await create_refresh_token(user.id, user.email)
    user.refresh_token_hash = refresh_hash

    await session.commit()

    try:
        await send_magic_link_onboarding(session=session, user=user, plan=user.plan)
    except Exception:  # noqa: BLE001 - onboarding is best-effort
        logger.exception("Failed to trigger onboarding email for %s", email)

    payload = _build_session_payload(user=user, token=token, refresh_token=refresh_token, expires_delta=expires_delta)
    return MemberRegistrationResponse(**payload)


@router.post("/login", response_model=MemberLoginResponse)
async def member_login(
    request: MemberLoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Authenticate a member using email and password."""

    email = _normalize_email(request.email)

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning("Member login failed for %s: account not found", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user.password_hash):
        logger.warning("Member login failed for %s: incorrect password", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active or not _access_granted(user):
        logger.warning("Member login blocked for %s: inactive account", email)
        raise HTTPException(status_code=403, detail="Account inactive")

    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    token = await create_jwt_token(
        user.id,
        user.email,
        expires_in=expires_delta,
        token_type="session",
    )
    
    # Create refresh token
    refresh_token, refresh_hash = await create_refresh_token(user.id, user.email)
    user.refresh_token_hash = refresh_hash
    await session.commit()

    payload = _build_session_payload(user=user, token=token, refresh_token=refresh_token, expires_delta=expires_delta)
    return MemberLoginResponse(**payload)


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Send a magic-link email to the requested address."""

    email = _normalize_email(request.email)
    email_service = get_email_service()
    if not email_service:
        logger.error("Magic link requested but email service is not configured")
        raise HTTPException(status_code=503, detail="Email service unavailable")

    user = await _get_or_create_user(session, email)

    token = await create_magic_link_token(user.id, user.email)
    login_url = f"{settings.FRONTEND_URL.rstrip('/')}/dashboard?token={token}"
    expires_minutes = max(1, settings.MAGIC_LINK_EXPIRATION_MINUTES)

    # Use professional email template
    email_data = magic_link_email(
        magic_link_url=login_url,
        expires_minutes=expires_minutes,
        user_email=email
    )

    sent = await email_service.send_email(
        to_email=email,
        subject=email_data["subject"],
        html_content=email_data["html"],
        plain_text_content=email_data["text"],
    )

    if sent:
        user.last_magic_link_sent_at = datetime.now(timezone.utc)
        await session.commit()
        logger.info("Magic link sent to %s", email)
        return MagicLinkResponse(status="sent", message="Magic link sent")

    await session.rollback()
    logger.error("SendGrid failed to deliver magic link to %s", email)
    return MagicLinkResponse(status="skipped", message="Failed to send magic link")


@router.post("/validate", response_model=AuthValidateResponse)
async def validate_token(
    request: AuthValidateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Validate a JWT and enrich response with subscription status."""

    result = await validate_jwt_token(request.token)
    if not result.get("valid"):
        logger.warning("Invalid token received: %s", result.get("message"))
        return AuthValidateResponse(**result)

    user = None
    user_id = result.get("user_id")
    if user_id is not None:
        user = await session.get(User, user_id)

    if user is None and result.get("email"):
        email = _normalize_email(result["email"])
        stmt = select(User).where(User.email == email)
        query = await session.execute(stmt)
        user = query.scalar_one_or_none()

    if user is None:
        logger.error("Token valid but user record missing (user_id=%s)", user_id)
        return AuthValidateResponse(valid=False, message="User not found")

    access_granted = _access_granted(user)
    message = _build_portal_message(user.status)

    return AuthValidateResponse(
        valid=True,
        user_id=user.id,
        email=user.email,
        message=message,
        plan=user.plan,
        status=user.status,
        status_reason=user.status_reason,
        access_granted=access_granted,
        access_expires_at=user.access_expires_at,
        portal_update_url=user.portal_update_url,
        token_type=result.get("token_type"),
        expires_at=result.get("expires_at"),
        has_password=bool(user.password_hash),
    )


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Authenticate an admin user using email + password credentials."""

    email = _normalize_email(request.email)
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or user.role != "admin":
        logger.warning("Admin login failed for %s: no admin account", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user.password_hash):
        logger.warning("Admin login failed for %s: bad password", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    token = await create_jwt_token(user.id, user.email, expires_in=expires_delta, token_type="admin_session")

    return AdminLoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Exchange a valid refresh token for a new access token and refresh token."""

    # Find user by validating refresh token
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    user = None
    for candidate in users:
        if candidate.refresh_token_hash:
            validation = await validate_refresh_token(request.refresh_token, candidate.refresh_token_hash)
            if validation.get("valid"):
                user = candidate
                break
    
    if user is None:
        logger.warning("Refresh token validation failed: no matching user found")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check if user account is active
    if not user.is_active or not _access_granted(user):
        logger.warning("Refresh blocked for user %s: account inactive", user.email)
        raise HTTPException(status_code=403, detail="Account inactive")
    
    # Generate new access token
    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    access_token = await create_jwt_token(
        user.id,
        user.email,
        expires_in=expires_delta,
        token_type="session",
    )
    
    # Rotate refresh token (create new one and invalidate old)
    new_refresh_token, new_refresh_hash = await create_refresh_token(user.id, user.email)
    user.refresh_token_hash = new_refresh_hash
    await session.commit()
    
    logger.info("Successfully refreshed tokens for user %s", user.email)
    
    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=int(expires_delta.total_seconds()),
    )


@router.post("/set-password", response_model=SetPasswordResponse)
async def set_password(
    request_body: SetPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """Set a password for user accounts that don't have one (OAuth or magic-link users)."""

    # Extract token from Authorization header
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
    
    # Check if user already has a password
    if user.password_hash:
        logger.info(f"User {user.email} attempted to set password but already has one")
        raise HTTPException(status_code=400, detail="Password already set. Use password reset instead.")
    
    # Hash and set the password
    user.password_hash = hash_password(request_body.password)
    await session.commit()
    
    logger.info(f"Password successfully set for user {user.email}")
    
    return SetPasswordResponse()
