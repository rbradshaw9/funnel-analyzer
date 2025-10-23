"""Async SQLAlchemy session and engine helpers."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from ..models.database import Base, User
from .migrations import ensure_recipient_email_column, ensure_screenshot_storage_key_column
from ..utils.config import settings


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
    """Create tables and ensure a default user exists for demo flows."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_recipient_email_column(conn)
    await ensure_screenshot_storage_key_column(conn)

    async with AsyncSessionFactory() as session:
        query = select(User).where(User.email == settings.DEFAULT_USER_EMAIL)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            session.add(
                User(
                    email=settings.DEFAULT_USER_EMAIL,
                    full_name=settings.DEFAULT_USER_NAME,
                    is_active=1,
                )
            )
            await session.commit()


async def reset_db() -> None:
    """Drop and recreate all tables. Use with caution in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await init_db()


def reset_db_sync() -> None:
    """Synchronous helper to reset the database."""
    asyncio.run(reset_db())
