"""Password hashing and verification helpers."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Hash the provided password using bcrypt."""
    if not password:
        raise ValueError("Password must not be empty")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a password against a stored bcrypt hash."""
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
