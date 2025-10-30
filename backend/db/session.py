"""Async SQLAlchemy session and engine helpers."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from ..models.database import Base, User
from ..services.passwords import hash_password, verify_password
from .migrations import (
    ensure_recipient_email_column,
    ensure_screenshot_storage_key_column,
    ensure_user_password_hash_column,
    ensure_user_role_column,
    ensure_user_plan_column,
    ensure_user_additional_columns,
    ensure_pipeline_metrics_column,
    ensure_analysis_naming_columns,
    ensure_recommendation_completions_column,
    migration_lock,
)
from .migrations_oauth import ensure_user_oauth_columns
from ..utils.config import settings

logger = logging.getLogger(__name__)


def _build_async_database_url(raw_url: str) -> str:
    """Ensure the database URL uses an async driver."""
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if raw_url.startswith("sqlite://") and not raw_url.startswith("sqlite+aiosqlite://"):
        return raw_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return raw_url


ASYNC_DATABASE_URL = _build_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.DEBUG, future=True)

AsyncSessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create tables and ensure default users exist for demo flows."""
    async with engine.begin() as conn:
        async with migration_lock(conn):
            await conn.run_sync(Base.metadata.create_all)
            await ensure_recipient_email_column(conn)
            await ensure_screenshot_storage_key_column(conn)
            await ensure_user_role_column(conn)
            await ensure_user_password_hash_column(conn)
            await ensure_user_plan_column(conn)
            await ensure_user_additional_columns(conn)
            await ensure_pipeline_metrics_column(conn)
            await ensure_user_oauth_columns(conn)
            await ensure_analysis_naming_columns(conn)
            await ensure_recommendation_completions_column(conn)

    async with AsyncSessionFactory() as session:
        default_email = (settings.DEFAULT_USER_EMAIL or "").strip().lower()
        if default_email:
            query = select(User).where(User.email == default_email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                session.add(
                    User(
                        email=default_email,
                        full_name=settings.DEFAULT_USER_NAME,
                        is_active=1,
                    )
                )
                await session.commit()

        admin_email_raw = settings.DEFAULT_ADMIN_EMAIL or ""
        admin_password_raw = settings.DEFAULT_ADMIN_PASSWORD or ""
        admin_email = admin_email_raw.strip().lower()
        admin_password = admin_password_raw.strip()

        if admin_email and admin_password:
            result = await session.execute(select(User).where(User.email == admin_email))
            admin = result.scalar_one_or_none()
            password_matches = verify_password(admin_password, admin.password_hash) if admin else False

            if admin is None:
                session.add(
                    User(
                        email=admin_email,
                        full_name=settings.DEFAULT_ADMIN_NAME,
                        is_active=1,
                        role="admin",
                        password_hash=hash_password(admin_password),
                        status="active",
                        plan="pro",
                    )
                )
                await session.commit()
            else:
                updated = False
                if admin.role != "admin":
                    admin.role = "admin"
                    updated = True
                if not password_matches:
                    admin.password_hash = hash_password(admin_password)
                    updated = True
                if settings.DEFAULT_ADMIN_NAME and admin.full_name != settings.DEFAULT_ADMIN_NAME:
                    admin.full_name = settings.DEFAULT_ADMIN_NAME
                    updated = True
                if admin.is_active != 1:
                    admin.is_active = 1
                    updated = True
                if admin.status != "active":
                    admin.status = "active"
                    updated = True
                if admin.plan != "pro":
                    admin.plan = "pro"
                    updated = True

                if updated:
                    await session.commit()
        else:
            if admin_email_raw.strip() or admin_password_raw.strip():
                logger.warning(
                    "Admin account seeding skipped: both DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD must be provided."
                )
            else:
                logger.warning(
                    "Admin account seeding skipped: DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD are not set."
                )


async def reset_db() -> None:
    """Drop and recreate all tables. Use with caution in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await init_db()


def reset_db_sync() -> None:
    """Synchronous helper to reset the database."""
    asyncio.run(reset_db())
