"""Lightweight database migration helpers executed during application startup."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Sequence

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)


_MIGRATION_LOCK_KEY = 1_947_362_981


@asynccontextmanager
async def migration_lock(conn: AsyncConnection) -> AsyncIterator[None]:
    """Synchronize startup migrations across concurrent workers."""

    if conn.dialect.name != "postgresql":
        yield
        return

    logger.info("Acquiring advisory lock for startup migrations")
    await conn.exec_driver_sql(f"SELECT pg_advisory_lock({_MIGRATION_LOCK_KEY})")
    try:
        yield
    finally:
        await conn.exec_driver_sql(f"SELECT pg_advisory_unlock({_MIGRATION_LOCK_KEY})")


async def _sqlite_column_exists(conn: AsyncConnection, table: str, column: str) -> bool:
    result = await conn.exec_driver_sql(f"PRAGMA table_info({table})")
    columns: Sequence[tuple] = result.fetchall()
    return any(col[1] == column for col in columns)


async def _postgres_column_exists(conn: AsyncConnection, table: str, column: str) -> bool:
    result = await conn.exec_driver_sql(
        "SELECT column_name FROM information_schema.columns "
        f"WHERE table_name = '{table}' AND column_name = '{column}'"
    )
    return result.first() is not None


async def _add_sqlite_column_if_missing(
    conn: AsyncConnection,
    table: str,
    column: str,
    definition: str,
) -> bool:
    if await _sqlite_column_exists(conn, table, column):
        return False
    await conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    return True


async def _add_postgres_column_if_missing(
    conn: AsyncConnection,
    table: str,
    column: str,
    definition: str,
) -> None:
    await conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition}")


async def ensure_recipient_email_column(conn: AsyncConnection) -> None:
    """Ensure the `recipient_email` column exists on the analyses table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "analyses", "recipient_email", "VARCHAR(255)")
    else:
        exists = await _postgres_column_exists(conn, "analyses", "recipient_email")
        if not exists:
            await _add_postgres_column_if_missing(conn, "analyses", "recipient_email", "VARCHAR(255)")
        added = not exists

    if added:
        logger.info("Adding missing analyses.recipient_email column")


async def ensure_screenshot_storage_key_column(conn: AsyncConnection) -> None:
    """Ensure the `screenshot_storage_key` column exists on analysis_pages."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "analysis_pages", "screenshot_storage_key", "VARCHAR(2048)")
    else:
        exists = await _postgres_column_exists(conn, "analysis_pages", "screenshot_storage_key")
        if not exists:
            await _add_postgres_column_if_missing(conn, "analysis_pages", "screenshot_storage_key", "VARCHAR(2048)")
        added = not exists

    if added:
        logger.info("Adding missing analysis_pages.screenshot_storage_key column")


async def ensure_user_role_column(conn: AsyncConnection) -> None:
    """Ensure the `role` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "users", "role", "VARCHAR(50) DEFAULT 'member'")
    else:
        exists = await _postgres_column_exists(conn, "users", "role")
        if not exists:
            await _add_postgres_column_if_missing(conn, "users", "role", "VARCHAR(50) DEFAULT 'member'")
        added = not exists

    if added:
        logger.info("Adding missing users.role column")


async def ensure_user_password_hash_column(conn: AsyncConnection) -> None:
    """Ensure the `password_hash` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "users", "password_hash", "VARCHAR(255)")
    else:
        exists = await _postgres_column_exists(conn, "users", "password_hash")
        if not exists:
            await _add_postgres_column_if_missing(conn, "users", "password_hash", "VARCHAR(255)")
        added = not exists

    if added:
        logger.info("Adding missing users.password_hash column")


async def ensure_user_plan_column(conn: AsyncConnection) -> None:
    """Ensure the `plan` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "users", "plan", "VARCHAR(50) DEFAULT 'free'")
    else:
        logger.info("Ensuring users.plan column exists")
        exists = await _postgres_column_exists(conn, "users", "plan")
        if not exists:
            await _add_postgres_column_if_missing(conn, "users", "plan", "VARCHAR(50) DEFAULT 'free'")
        added = not exists

    await conn.exec_driver_sql("UPDATE users SET plan = 'free' WHERE plan IS NULL")

    if dialect != "sqlite":
        await conn.exec_driver_sql("ALTER TABLE users ALTER COLUMN plan SET DEFAULT 'free'")
        try:
            await conn.exec_driver_sql("ALTER TABLE users ALTER COLUMN plan SET NOT NULL")
        except ProgrammingError as exc:
            message = str(exc)
            if "does not exist" in message or "null values" in message:
                logger.warning("Could not enforce NOT NULL on users.plan column: %s", message)
            else:
                raise

    if added:
        logger.info("Ensured users.plan column with default 'free'")


async def ensure_pipeline_metrics_column(conn: AsyncConnection) -> None:
    """Ensure the `pipeline_metrics` column exists on the analyses table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "analyses", "pipeline_metrics", "JSON")
    else:
        exists = await _postgres_column_exists(conn, "analyses", "pipeline_metrics")
        if not exists:
            await _add_postgres_column_if_missing(conn, "analyses", "pipeline_metrics", "JSON")
        added = not exists

    if added:
        logger.info("Adding missing analyses.pipeline_metrics column")


async def ensure_user_additional_columns(conn: AsyncConnection) -> None:
    """Backfill recently added nullable columns on the users table."""

    dialect = conn.dialect.name

    # Column definition: (name, postgres_def, sqlite_def, postgres_backfill, sqlite_backfill)
    columns: Sequence[tuple[str, str, str, Optional[str], Optional[str]]] = (
        (
            "status",
            "VARCHAR(50) DEFAULT 'active'",
            "VARCHAR(50) DEFAULT 'active'",
            "UPDATE users SET status = 'active' WHERE status IS NULL",
            "UPDATE users SET status = 'active' WHERE status IS NULL",
        ),
        (
            "status_reason",
            "VARCHAR(255)",
            "VARCHAR(255)",
            None,
            None,
        ),
        (
            "status_last_updated",
            "TIMESTAMPTZ DEFAULT NOW()",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "UPDATE users SET status_last_updated = NOW() WHERE status_last_updated IS NULL",
            "UPDATE users SET status_last_updated = CURRENT_TIMESTAMP WHERE status_last_updated IS NULL",
        ),
        (
            "subscription_id",
            "VARCHAR(150)",
            "VARCHAR(150)",
            None,
            None,
        ),
        (
            "thrivecart_customer_id",
            "VARCHAR(150)",
            "VARCHAR(150)",
            None,
            None,
        ),
        (
            "access_expires_at",
            "TIMESTAMPTZ",
            "TIMESTAMP",
            None,
            None,
        ),
        (
            "portal_update_url",
            "VARCHAR(2048)",
            "VARCHAR(2048)",
            None,
            None,
        ),
        (
            "last_magic_link_sent_at",
            "TIMESTAMPTZ",
            "TIMESTAMP",
            None,
            None,
        ),
    )

    for name, pg_def, sqlite_def, pg_backfill, sqlite_backfill in columns:
        if dialect == "sqlite":
            newly_added = await _add_sqlite_column_if_missing(conn, "users", name, sqlite_def)
            if sqlite_backfill:
                await conn.exec_driver_sql(sqlite_backfill)
        else:
            exists = await _postgres_column_exists(conn, "users", name)
            if not exists:
                await _add_postgres_column_if_missing(conn, "users", name, pg_def)
            newly_added = not exists
            if pg_backfill:
                await conn.exec_driver_sql(pg_backfill)

        if newly_added:
            logger.info("Ensured users.%s column exists", name)

    if dialect != "sqlite":
        await conn.exec_driver_sql("ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active'")
        await conn.exec_driver_sql("ALTER TABLE users ALTER COLUMN status_last_updated SET DEFAULT NOW()")


async def ensure_analysis_naming_columns(conn: AsyncConnection) -> None:
    """Ensure analysis naming and versioning columns exist."""
    dialect = conn.dialect.name
    
    columns = (
        # (column_name, postgres_def, sqlite_def)
        ("name", "VARCHAR(255)", "VARCHAR(255)"),
        ("parent_analysis_id", "INTEGER", "INTEGER"),
    )
    
    for name, pg_def, sqlite_def in columns:
        if dialect == "sqlite":
            newly_added = await _add_sqlite_column_if_missing(conn, "analyses", name, sqlite_def)
        else:
            exists = await _postgres_column_exists(conn, "analyses", name)
            if not exists:
                await _add_postgres_column_if_missing(conn, "analyses", name, pg_def)
            newly_added = not exists
        
        if newly_added:
            logger.info("Ensured analyses.%s column exists", name)
    
    # Add index on parent_analysis_id for faster lookups
    if dialect == "postgresql":
        try:
            await conn.exec_driver_sql(
                "CREATE INDEX IF NOT EXISTS idx_analyses_parent_analysis_id ON analyses(parent_analysis_id)"
            )
        except Exception:  # noqa: BLE001
            pass  # Index may already exist


async def ensure_recommendation_completions_column(conn: AsyncConnection) -> None:
    """Ensure the `recommendation_completions` column exists on analyses table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        added = await _add_sqlite_column_if_missing(conn, "analyses", "recommendation_completions", "TEXT DEFAULT '{}'")
    else:
        exists = await _postgres_column_exists(conn, "analyses", "recommendation_completions")
        if not exists:
            await _add_postgres_column_if_missing(conn, "analyses", "recommendation_completions", "JSONB DEFAULT '{}'::jsonb")
        added = not exists

    if added:
        logger.info("Adding missing analyses.recommendation_completions column")
