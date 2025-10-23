"""Authentication helpers for issuing and validating JWT tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

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
