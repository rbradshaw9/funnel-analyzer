"""Authentication helpers for issuing and validating JWT tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import secrets

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from ..services.passwords import hash_password, verify_password
from ..utils.config import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def validate_jwt_token(token: str) -> Dict:
    """Validate a JWT and return decoded user details when valid."""

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        exp_ts = payload.get("exp")
        expires_at: Optional[datetime] = None
        if exp_ts:
            if isinstance(exp_ts, (int, float)):
                expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
            elif isinstance(exp_ts, datetime):
                expires_at = exp_ts.astimezone(timezone.utc)

        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "token_type": payload.get("token_type", "session"),
            "expires_at": expires_at,
            "message": "Token is valid",
        }

    except ExpiredSignatureError:
        return {
            "valid": False,
            "message": "Token expired",
        }
    except InvalidTokenError:
        return {
            "valid": False,
            "message": "Invalid token",
        }
    except Exception as exc:  # noqa: BLE001 - catch unexpected decoding errors
        return {
            "valid": False,
            "message": f"Validation error: {exc}",
        }


def _build_payload(user_id: int, email: str, *, expires_delta: timedelta, token_type: str) -> Dict:
    now = _now_utc()
    return {
        "user_id": user_id,
        "email": email,
        "exp": now + expires_delta,
        "iat": now,
        "token_type": token_type,
    }


async def create_jwt_token(
    user_id: int,
    email: str,
    *,
    expires_in: Optional[timedelta] = None,
    token_type: str = "session",
) -> str:
    """Issue a signed JWT for the given user."""

    expires_delta = expires_in or timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = _build_payload(user_id, email, expires_delta=expires_delta, token_type=token_type)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_magic_link_token(user_id: int, email: str) -> str:
    """Issue a short-lived token for magic-link authentication."""

    minutes = max(1, settings.MAGIC_LINK_EXPIRATION_MINUTES)
    expires_delta = timedelta(minutes=minutes)
    payload = _build_payload(user_id, email, expires_delta=expires_delta, token_type="magic_link")
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(user_id: int, email: str) -> tuple[str, str]:
    """Create a refresh token and return both the token and its hash.
    
    Returns:
        tuple: (refresh_token, refresh_token_hash)
    """
    # Generate a secure random token
    token = secrets.token_urlsafe(64)
    
    # Create a JWT that includes the token and metadata
    expires_delta = timedelta(days=30)  # Refresh tokens last 30 days
    payload = {
        "user_id": user_id,
        "email": email,
        "token": token,
        "exp": _now_utc() + expires_delta,
        "iat": _now_utc(),
        "token_type": "refresh",
    }
    refresh_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    # Hash the token for storage
    token_hash = hash_password(token)
    
    return refresh_token, token_hash


async def validate_refresh_token(refresh_token: str, stored_hash: str) -> Dict:
    """Validate a refresh token against the stored hash.
    
    Args:
        refresh_token: The JWT refresh token from the client
        stored_hash: The hashed token from the database
        
    Returns:
        Dictionary with validation result and user info
    """
    try:
        # Decode the JWT
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        # Verify it's a refresh token
        if payload.get("token_type") != "refresh":
            return {"valid": False, "message": "Not a refresh token"}
        
        # Extract the random token from payload
        token = payload.get("token")
        if not token:
            return {"valid": False, "message": "Invalid token format"}
        
        # Verify the token matches the stored hash
        if not verify_password(token, stored_hash):
            return {"valid": False, "message": "Token does not match"}
        
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "message": "Refresh token is valid",
        }
        
    except ExpiredSignatureError:
        return {"valid": False, "message": "Refresh token expired"}
    except InvalidTokenError:
        return {"valid": False, "message": "Invalid refresh token"}
    except Exception as exc:
        return {"valid": False, "message": f"Validation error: {exc}"}
