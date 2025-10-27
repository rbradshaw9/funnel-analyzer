import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.models.database import Base, User
from backend.routes.auth import router as auth_router
from backend.db.session import get_db_session
from backend.utils.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _setup_app(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_session():
        async with session_factory() as session:
            yield session

    app = FastAPI()
    app.include_router(auth_router, prefix="/api/auth")
    app.dependency_overrides[get_db_session] = override_session

    async def fake_onboarding(session, user, plan=None, force=False):  # noqa: ARG001
        fake_onboarding.calls += 1
        return True

    fake_onboarding.calls = 0

    monkeypatch.setattr("backend.routes.auth.send_magic_link_onboarding", fake_onboarding)
    monkeypatch.setattr("backend.routes.auth.hash_password", lambda password: f"hashed-{password}")
    monkeypatch.setattr(
        "backend.routes.auth.verify_password",
        lambda password, password_hash: password_hash == f"hashed-{password}",
    )

    async def cleanup():
        app.dependency_overrides.clear()
        await engine.dispose()

    return app, session_factory, fake_onboarding, cleanup


@pytest.mark.anyio("asyncio")
async def test_register_creates_member_and_sends_onboarding(monkeypatch):
    app, session_factory, fake_onboarding, cleanup = await _setup_app(monkeypatch)
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "email": "member@example.com",
                    "password": "super-secret",
                    "full_name": "Member One",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "registered"
        assert data["email"] == "member@example.com"
        assert data["plan"] == "free"
        assert data["expires_in"] == settings.JWT_EXPIRATION_HOURS * 3600
        assert data["access_token"]
        assert fake_onboarding.calls == 1

        async with session_factory() as session:
            result = await session.execute(select(User).where(User.email == "member@example.com"))
            user = result.scalar_one()
            assert user.plan == "free"
            assert user.password_hash == "hashed-super-secret"
            assert user.full_name == "Member One"
    finally:
        await cleanup()


@pytest.mark.anyio("asyncio")
async def test_register_duplicate_email_returns_conflict(monkeypatch):
    app, session_factory, _, cleanup = await _setup_app(monkeypatch)
    try:
        async with session_factory() as session:
            session.add(
                User(
                    email="member@example.com",
                    password_hash="hashed-existing",
                    plan="basic",
                    status="active",
                    is_active=1,
                )
            )
            await session.commit()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/register",
                json={"email": "member@example.com", "password": "another-secret"},
            )

        assert response.status_code == 409
        assert response.json()["detail"].lower().startswith("email already registered")
    finally:
        await cleanup()


@pytest.mark.anyio("asyncio")
async def test_login_returns_session_token(monkeypatch):
    app, session_factory, _, cleanup = await _setup_app(monkeypatch)
    try:
        async with session_factory() as session:
            user = User(
                email="member@example.com",
                password_hash="hashed-valid-pass",
                plan="pro",
                status="active",
                is_active=1,
            )
            session.add(user)
            await session.commit()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={"email": "member@example.com", "password": "valid-pass"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"
        assert data["plan"] == "pro"
        assert data["email"] == "member@example.com"
        assert data["access_token"]
    finally:
        await cleanup()


@pytest.mark.anyio("asyncio")
async def test_login_rejects_wrong_password(monkeypatch):
    app, session_factory, _, cleanup = await _setup_app(monkeypatch)
    try:
        async with session_factory() as session:
            user = User(
                email="member@example.com",
                password_hash="hashed-correct",
                plan="free",
                status="active",
                is_active=1,
            )
            session.add(user)
            await session.commit()

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={"email": "member@example.com", "password": "wrong-pass"},
            )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    finally:
        await cleanup()
