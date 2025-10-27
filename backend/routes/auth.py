"""Authentication endpoints for magic-link login and token validation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
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
    OAuthCallbackRequest,
    OAuthLoginResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    MemberLoginRequest,
    MemberLoginResponse,
    MemberRegistrationRequest,
    MemberRegistrationResponse,
)
from ..services.auth import create_jwt_token, create_magic_link_token, validate_jwt_token
from ..services.email import get_email_service
from ..services.passwords import verify_password
from ..services.oauth import get_auth0_client, OAuthExchangeError
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


async def _get_user_by_auth0_id(session: AsyncSession, provider_id: str) -> User | None:
    stmt = select(User).where(User.auth0_user_id == provider_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


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


def _build_session_payload(*, user: User, token: str, expires_delta: timedelta) -> dict:
    return {
        "access_token": token,
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

    await session.commit()

    try:
        await send_magic_link_onboarding(session=session, user=user, plan=user.plan)
    except Exception:  # noqa: BLE001 - onboarding is best-effort
        logger.exception("Failed to trigger onboarding email for %s", email)

    payload = _build_session_payload(user=user, token=token, expires_delta=expires_delta)
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

    payload = _build_session_payload(user=user, token=token, expires_delta=expires_delta)
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

    subject = "Your Funnel Analyzer login link"
    html_content = (
        "<p>Hi there,</p>"
        "<p>Use the button below to sign in to Funnel Analyzer. This link expires in "
        f"{expires_minutes} minutes.</p>"
        f"<p><a href=\"{login_url}\" style=\"display:inline-block;padding:12px 18px;"
        "background-color:#4f46e5;color:#ffffff;border-radius:8px;text-decoration:none;"
        "font-weight:600\">Access your dashboard</a></p>"
        f"<p>If the button doesn't work, copy and paste this URL into your browser:<br />"
        f"<span style=\"word-break:break-all;color:#4f46e5\">{login_url}</span></p>"
        "<p>If you did not request this link, you can safely ignore this email.</p>"
        "<p>— Funnel Analyzer Pro</p>"
    )
    plain_text = (
        "Use the link below to sign in to Funnel Analyzer. "
        f"This link expires in {expires_minutes} minutes.\n\n{login_url}\n\n"
        "If you did not request this link, you can ignore this email."
    )

    sent = await email_service.send_email(
        to_email=email,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_text,
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
    )


@router.post("/oauth/auth0/callback", response_model=OAuthLoginResponse)
async def auth0_callback(
    request: OAuthCallbackRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Exchange an Auth0 authorization code for a Funnel Analyzer JWT."""

    client = get_auth0_client()
    if client is None:
        logger.error("Auth0 login attempted but integration is not configured")
        raise HTTPException(status_code=503, detail="Auth0 integration not configured")

    try:
        profile = await client.exchange_code(request.code, str(request.redirect_uri))
    except OAuthExchangeError as exc:
        logger.warning("Auth0 code exchange failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - defensive logging
        logger.exception("Unexpected Auth0 error: %s", exc)
        raise HTTPException(status_code=500, detail="Auth0 login failed") from exc

    email = _normalize_email(profile.email)
    provider_id = profile.provider_id

    user = await _get_user_by_auth0_id(session, provider_id)
    created = False

    if user is None:
        user = await _get_user_by_email(session, email)
        if user is None:
            user = User(
                email=email,
                full_name=profile.name,
                auth0_user_id=provider_id,
                status="active",
                plan="free",
                is_active=1,
            )
            session.add(user)
            created = True
        else:
            if user.auth0_user_id and user.auth0_user_id != provider_id:
                await session.rollback()
                logger.error(
                    "Auth0 login for %s rejected: provider mismatch (existing=%s, incoming=%s)",
                    email,
                    user.auth0_user_id,
                    provider_id,
                )
                raise HTTPException(
                    status_code=409,
                    detail="Email already linked to another Auth0 account",
                )
            user.auth0_user_id = provider_id
            if profile.name and not user.full_name:
                user.full_name = profile.name
    else:
        if user.email != email:
            user.email = email
        if profile.name and not user.full_name:
            user.full_name = profile.name

    await session.flush()
    user_id = user.id

    if not _access_granted(user):
        await session.rollback()
        logger.warning(
            "Auth0 login blocked for %s (user_id=%s) due to inactive account",
            email,
            user_id,
        )
        raise HTTPException(status_code=403, detail="Account is not active")

    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    token = await create_jwt_token(
        user_id,
        user.email,
        expires_in=expires_delta,
        token_type="session",
    )

    await session.commit()

    logger.info(
        "Auth0 login successful for %s (user_id=%s, created=%s)",
        email,
        user_id,
        created,
    )

    return OAuthLoginResponse(
        access_token=token,
        expires_in=int(expires_delta.total_seconds()),
        user_id=user_id,
        email=user.email,
        provider="auth0",
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
