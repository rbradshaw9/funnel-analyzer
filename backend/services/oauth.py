"""OAuth provider helpers."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional

import httpx
from jose import jwt as jose_jwt

from ..utils.config import settings

logger = logging.getLogger(__name__)


class OAuthConfigurationError(Exception):
    """Raised when an OAuth provider is not correctly configured."""


class OAuthExchangeError(Exception):
    """Raised when an OAuth provider exchange fails."""


@dataclass(slots=True)
class ProviderProfile:
    """Normalized profile returned from an OAuth provider."""

    provider: str
    provider_id: str
    email: str
    name: Optional[str] = None
    access_token: Optional[str] = None
    id_token: Optional[str] = None


class Auth0OAuthClient:
    """Minimal Auth0 client for exchanging authorization codes."""

    def __init__(self) -> None:
        self.domain = (settings.AUTH0_DOMAIN or "").strip()
        self.client_id = (settings.AUTH0_CLIENT_ID or "").strip()
        self.client_secret = (settings.AUTH0_CLIENT_SECRET or "").strip()
        self.audience = (settings.AUTH0_AUDIENCE or "").strip()

        if not self.domain or not self.client_id or not self.client_secret:
            raise OAuthConfigurationError("Auth0 credentials are not configured")

    async def exchange_code(self, code: str, redirect_uri: str) -> ProviderProfile:
        if not code:
            raise OAuthExchangeError("Authorization code missing")
        if not redirect_uri:
            raise OAuthExchangeError("Redirect URI missing")

        token_url = f"https://{self.domain}/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if self.audience:
            payload["audience"] = self.audience

        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(token_url, data=payload)
            try:
                token_response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - error branch
                logger.warning("Auth0 token exchange failed: %s", exc)
                raise OAuthExchangeError("Failed to exchange authorization code with Auth0") from exc

            tokens = token_response.json()
            access_token = tokens.get("access_token")
            id_token = tokens.get("id_token")

            profile: Optional[dict] = None
            if access_token:
                userinfo_url = f"https://{self.domain}/userinfo"
                userinfo_response = await client.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if userinfo_response.status_code == 200:
                    profile = userinfo_response.json()
                else:  # pragma: no cover - fallback branch
                    logger.info(
                        "Auth0 userinfo call returned status %s",
                        userinfo_response.status_code,
                    )

            if profile is None and id_token:
                try:
                    profile = jose_jwt.get_unverified_claims(id_token)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Unable to decode Auth0 id_token: %s", exc)

        if not profile:
            raise OAuthExchangeError("Auth0 user profile not available")

        provider_id = profile.get("sub")
        email = profile.get("email")
        if not provider_id or not email:
            raise OAuthExchangeError("Auth0 profile missing required fields")

        name = profile.get("name") or profile.get("nickname")
        return ProviderProfile(
            provider="auth0",
            provider_id=provider_id,
            email=email,
            name=name,
            access_token=access_token,
            id_token=id_token,
        )


_auth0_client: Optional[Auth0OAuthClient] = None


def get_auth0_client() -> Optional[Auth0OAuthClient]:
    """Return a cached Auth0 client when configuration is present."""

    global _auth0_client

    try:
        if _auth0_client is None:
            _auth0_client = Auth0OAuthClient()
    except OAuthConfigurationError:
        logger.info("Auth0 integration is not fully configured; skipping client init")
        return None

    return _auth0_client


def reset_auth0_client() -> None:
    """Reset cached Auth0 client (primarily for tests)."""

    global _auth0_client
    _auth0_client = None


__all__ = [
    "Auth0OAuthClient",
    "OAuthConfigurationError",
    "OAuthExchangeError",
    "ProviderProfile",
    "get_auth0_client",
    "reset_auth0_client",
]
