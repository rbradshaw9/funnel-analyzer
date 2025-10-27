"""OAuth authentication service for Google and GitHub."""

from __future__ import annotations

import logging
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException

from ..utils.config import settings

logger = logging.getLogger(__name__)

# Initialize OAuth registry
oauth = OAuth()

# Register Google OAuth provider
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    logger.info("Google OAuth provider registered")
else:
    logger.warning("Google OAuth not configured (GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing)")

# Register GitHub OAuth provider
if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    oauth.register(
        name="github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )
    logger.info("GitHub OAuth provider registered")
else:
    logger.warning("GitHub OAuth not configured (GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET missing)")


def validate_oauth_config(provider: str) -> None:
    """Validate OAuth configuration for a specific provider.
    
    Raises:
        HTTPException: If provider is not configured
    """
    if provider == "google":
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth not configured on server"
            )
    elif provider == "github":
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="GitHub OAuth not configured on server"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported OAuth provider: {provider}"
        )

    if not settings.OAUTH_REDIRECT_URI:
        raise HTTPException(
            status_code=500,
            detail="OAuth redirect URI not configured"
        )


def extract_user_info_from_google(token: dict) -> dict:
    """Extract user information from Google OAuth token.
    
    Args:
        token: OAuth token response from Google
        
    Returns:
        Dictionary with email, name, picture, provider_id
    """
    userinfo = token.get("userinfo", {})
    return {
        "email": userinfo.get("email", "").strip().lower(),
        "name": userinfo.get("name", ""),
        "picture": userinfo.get("picture"),
        "provider_id": userinfo.get("sub"),
    }


def extract_user_info_from_github(token: dict, user_data: dict) -> dict:
    """Extract user information from GitHub OAuth token and user data.
    
    Args:
        token: OAuth token response from GitHub
        user_data: User data from GitHub API
        
    Returns:
        Dictionary with email, name, picture, provider_id
    """
    return {
        "email": user_data.get("email", "").strip().lower(),
        "name": user_data.get("name") or user_data.get("login", ""),
        "picture": user_data.get("avatar_url"),
        "provider_id": str(user_data.get("id")),
    }
