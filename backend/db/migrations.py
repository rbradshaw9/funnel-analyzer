"""Lightweight database migration helpers executed during application startup."""

from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)


async def ensure_recipient_email_column(conn: AsyncConnection) -> None:
    """Ensure the `recipient_email` column exists on the analyses table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql("PRAGMA table_info(analyses)")
        columns: Sequence[tuple] = result.fetchall()
        has_column = any(col[1] == "recipient_email" for col in columns)
    else:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'analyses' AND column_name = 'recipient_email'"
        )
        has_column = result.first() is not None

    if has_column:
        return

    logger.info("Adding missing analyses.recipient_email column")
    await conn.exec_driver_sql("ALTER TABLE analyses ADD COLUMN recipient_email VARCHAR(255)")


async def ensure_screenshot_storage_key_column(conn: AsyncConnection) -> None:
    """Ensure the `screenshot_storage_key` column exists on analysis_pages."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql("PRAGMA table_info(analysis_pages)")
        columns: Sequence[tuple] = result.fetchall()
        has_column = any(col[1] == "screenshot_storage_key" for col in columns)
    else:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'analysis_pages' AND column_name = 'screenshot_storage_key'"
        )
        has_column = result.first() is not None

    if has_column:
        return

    logger.info("Adding missing analysis_pages.screenshot_storage_key column")
    await conn.exec_driver_sql("ALTER TABLE analysis_pages ADD COLUMN screenshot_storage_key VARCHAR(2048)")


async def ensure_user_role_column(conn: AsyncConnection) -> None:
    """Ensure the `role` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql("PRAGMA table_info(users)")
        columns: Sequence[tuple] = result.fetchall()
        has_column = any(col[1] == "role" for col in columns)
    else:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'role'"
        )
        has_column = result.first() is not None

    if has_column:
        return

    logger.info("Adding missing users.role column")
    await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'member'")


async def ensure_user_password_hash_column(conn: AsyncConnection) -> None:
    """Ensure the `password_hash` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql("PRAGMA table_info(users)")
        columns: Sequence[tuple] = result.fetchall()
        has_column = any(col[1] == "password_hash" for col in columns)
    else:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'password_hash'"
        )
        has_column = result.first() is not None

    if has_column:
        return

    logger.info("Adding missing users.password_hash column")
    await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")


async def ensure_user_plan_column(conn: AsyncConnection) -> None:
    """Ensure the `plan` column exists on the users table."""
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql("PRAGMA table_info(users)")
        columns: Sequence[tuple] = result.fetchall()
        has_column = any(col[1] == "plan" for col in columns)
    else:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'users' AND column_name = 'plan'"
        )
        has_column = result.first() is not None

    if has_column:
        return

    logger.info("Adding missing users.plan column")
    if dialect == "sqlite":
        await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN plan VARCHAR(50) DEFAULT 'free'")
        await conn.exec_driver_sql("UPDATE users SET plan = 'free' WHERE plan IS NULL")
    else:
        await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN plan VARCHAR(50) DEFAULT 'free' NOT NULL")