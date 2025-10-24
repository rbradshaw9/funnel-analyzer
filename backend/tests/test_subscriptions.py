import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.models.database import Base, User
from backend.services.subscriptions import apply_thrivecart_membership_update


def _run_async(coro):
    return asyncio.run(coro)


def test_thrivecart_payment_activates_user():
    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            payload = {
                "event": "subscription_payment",
                "subscription": {
                    "status": "active",
                    "subscription_id": "sub_123",
                    "product_name": "Funnel Analyzer Pro",
                    "next_payment_date": "2025-01-01T12:00:00Z",
                },
                "customer": {
                    "email": "member@example.com",
                    "customer_id": "cust_456",
                    "portal_access_url": "https://portal.funnelanalyzerpro.com/account",
                },
            }
            result = await apply_thrivecart_membership_update(session, payload)
            assert result is not None
            user = result.user
            assert user.email == "member@example.com"
            assert user.plan == "pro"
            assert result.plan_slug == "pro"
            assert user.status == "active"
            assert result.just_activated is True
            assert user.subscription_id == "sub_123"
            assert user.thrivecart_customer_id == "cust_456"
            assert user.portal_update_url == "https://portal.funnelanalyzerpro.com/account"
            assert user.access_expires_at is not None
            expiry = user.access_expires_at
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            expected_expiry = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
            assert abs((expiry - expected_expiry).total_seconds()) < 1

        await engine.dispose()

    _run_async(scenario())


def test_thrivecart_failed_payment_sets_past_due():
    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            success_payload = {
                "event": "subscription_payment",
                "subscription": {
                    "status": "active",
                    "subscription_id": "sub_789",
                },
                "customer": {"email": "trouble@example.com"},
            }
            await apply_thrivecart_membership_update(session, success_payload)

            failure_payload = {
                "event": "subscription_payment_failed",
                "subscription": {
                    "status": "past_due",
                },
                "customer": {"email": "trouble@example.com"},
            }
            result = await apply_thrivecart_membership_update(session, failure_payload)
            assert result is not None
            user = result.user
            assert user.status == "past_due"
            assert user.is_active == 0
            assert user.access_expires_at is not None
            expiry = user.access_expires_at
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            assert expiry <= datetime.now(timezone.utc)
            assert user.status_reason is not None

        await engine.dispose()

    _run_async(scenario())


def test_thrivecart_payload_without_email_is_ignored():
    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            result = await apply_thrivecart_membership_update(session, {"event": "subscription_payment"})
            assert result is None
            users = await session.execute(select(User))
            assert users.scalars().all() == []

        await engine.dispose()

    _run_async(scenario())
