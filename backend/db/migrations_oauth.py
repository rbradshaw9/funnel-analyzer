"""OAuth-related database migrations."""

import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncConnection

from backend.db.migrations import (
    _add_postgres_column_if_missing,
    _add_sqlite_column_if_missing,
    _postgres_column_exists,
)

logger = logging.getLogger(__name__)


async def ensure_user_oauth_columns(conn: AsyncConnection) -> None:
    """Add OAuth provider and profile completion columns to users table."""

    dialect = conn.dialect.name

    # Column definition: (name, postgres_def, sqlite_def)
    columns: Sequence[tuple[str, str, str]] = (
        ("oauth_provider", "VARCHAR(50)", "VARCHAR(50)"),
        ("oauth_provider_id", "VARCHAR(255)", "VARCHAR(255)"),
        ("oauth_refresh_token", "VARCHAR(512)", "VARCHAR(512)"),
        ("refresh_token_hash", "VARCHAR(255)", "VARCHAR(255)"),
        ("company", "VARCHAR(200)", "VARCHAR(200)"),
        ("job_title", "VARCHAR(100)", "VARCHAR(100)"),
        ("avatar_url", "VARCHAR(512)", "VARCHAR(512)"),
        ("onboarding_completed", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0"),
    )

    for name, pg_def, sqlite_def in columns:
        if dialect == "sqlite":
            newly_added = await _add_sqlite_column_if_missing(conn, "users", name, sqlite_def)
        else:
            exists = await _postgres_column_exists(conn, "users", name)
            if not exists:
                await _add_postgres_column_if_missing(conn, "users", name, pg_def)
            newly_added = not exists

        if newly_added:
            logger.info("Ensured users.%s column exists", name)

    # Add index on oauth_provider_id for fast lookups
    if dialect == "sqlite":
        try:
            await conn.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON users(oauth_provider_id)"
            )
            logger.info("Created index idx_users_oauth_provider_id")
        except Exception as exc:
            logger.warning("Failed to create idx_users_oauth_provider_id: %s", exc)
    else:
        try:
            await conn.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON users(oauth_provider_id)"
            )
            logger.info("Created index idx_users_oauth_provider_id")
        except Exception as exc:
            logger.warning("Failed to create idx_users_oauth_provider_id: %s", exc)
