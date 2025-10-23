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