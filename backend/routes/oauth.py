"""OAuth authentication routes for Google and GitHub login."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import User
from ..services.oauth import oauth, validate_oauth_config, extract_user_info_from_google, extract_user_info_from_github
from ..services.auth import create_jwt_token
from ..utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth flow."""
    validate_oauth_config("google")
    
    redirect_uri = settings.OAUTH_REDIRECT_URI
    if not redirect_uri:
        raise HTTPException(status_code=500, detail="OAuth redirect URI not configured")
    
    # Add provider to callback URL
    callback_uri = f"{redirect_uri}?provider=google"
    
    return await oauth.google.authorize_redirect(request, callback_uri)


@router.get("/github")
async def github_login(request: Request):
    """Initiate GitHub OAuth flow."""
    validate_oauth_config("github")
    
    redirect_uri = settings.OAUTH_REDIRECT_URI
    if not redirect_uri:
        raise HTTPException(status_code=500, detail="OAuth redirect URI not configured")
    
    # Add provider to callback URL
    callback_uri = f"{redirect_uri}?provider=github"
    
    return await oauth.github.authorize_redirect(request, callback_uri)


@router.get("/callback")
async def oauth_callback(
    request: Request,
    provider: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Handle OAuth callback from provider."""
    validate_oauth_config(provider)
    
    # Get OAuth client for provider
    client = getattr(oauth, provider, None)
    if not client:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    # Exchange authorization code for token
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        logger.error(f"OAuth token exchange failed for {provider}: {e}")
        # Redirect to frontend with error
        frontend_url = settings.FRONTEND_URL or "http://localhost:3001"
        return RedirectResponse(f"{frontend_url}/auth/error?message=OAuth+authentication+failed")
    
    # Extract user information based on provider
    if provider == "google":
        user_info = extract_user_info_from_google(token)
    elif provider == "github":
        # GitHub requires additional API call to get user data
        user_response = await client.get("user", token=token)
        user_data = user_response.json()
        
        # If email is private, fetch from emails endpoint
        if not user_data.get("email"):
            emails_response = await client.get("user/emails", token=token)
            emails = emails_response.json()
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    user_data["email"] = email_obj["email"]
                    break
        
        user_info = extract_user_info_from_github(token, user_data)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    email = user_info.get("email")
    provider_id = user_info.get("provider_id")
    
    if not email or not provider_id:
        logger.error(f"Missing email or provider_id from {provider} OAuth response")
        frontend_url = settings.FRONTEND_URL or "http://localhost:3001"
        return RedirectResponse(f"{frontend_url}/auth/error?message=Could+not+retrieve+user+information")
    
    # Check if user exists with this OAuth provider
    result = await db.execute(
        select(User).where(
            User.oauth_provider == provider,
            User.oauth_provider_id == provider_id
        )
    )
    user = result.scalar_one_or_none()
    
    # If not found by OAuth ID, check by email
    if not user:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            # Link existing account with OAuth provider
            user.oauth_provider = provider
            user.oauth_provider_id = provider_id
            if user_info.get("picture"):
                user.avatar_url = user_info["picture"]
            logger.info(f"Linked existing user {email} with {provider} OAuth")
        else:
            # Create new user account
            user = User(
                email=email,
                full_name=user_info.get("name"),
                oauth_provider=provider,
                oauth_provider_id=provider_id,
                avatar_url=user_info.get("picture"),
                is_active=1,
                status="active",
                plan="free",  # New OAuth users start with free plan
                onboarding_completed=0,
            )
            db.add(user)
            logger.info(f"Created new user {email} via {provider} OAuth")
    
    # Store refresh token if available
    if token.get("refresh_token"):
        user.oauth_refresh_token = token["refresh_token"]
    
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT access token
    access_token = await create_jwt_token(user.id, user.email)
    
    # Redirect to frontend with token
    frontend_url = settings.FRONTEND_URL or "http://localhost:3001"
    return RedirectResponse(f"{frontend_url}/auth/success?token={access_token}")
