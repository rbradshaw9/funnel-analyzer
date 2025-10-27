import asyncio

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.db.session import get_db_session
from backend.main import app
from backend.models.database import Base, User
from backend.services.oauth import ProviderProfile


class _FakeAuth0Client:
    def __init__(self, profile: ProviderProfile) -> None:
        self.profile = profile
        self.requests: list[tuple[str, str]] = []

    async def exchange_code(self, code: str, redirect_uri: str) -> ProviderProfile:  # noqa: D401 - simple proxy
        self.requests.append((code, redirect_uri))
        return self.profile


def _run_async(coro):
    return asyncio.run(coro)


def test_auth0_callback_creates_new_user(monkeypatch):
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async def override_get_db_session():
            async with Session() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_get_db_session

        profile = ProviderProfile(
            provider="auth0",
            provider_id="auth0|123",
            email="social@example.com",
            name="Social User",
        )
        fake_client = _FakeAuth0Client(profile)
        monkeypatch.setattr("backend.routes.auth.get_auth0_client", lambda: fake_client)

        try:
            async with AsyncClient(app=app, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/oauth/auth0/callback",
                    json={
                        "code": "valid-code",
                        "redirect_uri": "https://frontend.example.com/auth/callback",
                    },
                )

            assert response.status_code == 200
            body = response.json()
            assert body["provider"] == "auth0"
            assert body["email"] == "social@example.com"
            assert body["user_id"] > 0
            assert body["access_token"]
            assert fake_client.requests == [("valid-code", "https://frontend.example.com/auth/callback")]

            async with Session() as session:
                user = await session.get(User, body["user_id"])
                assert user is not None
                assert user.auth0_user_id == "auth0|123"
                assert user.full_name == "Social User"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    _run_async(scenario())


def test_auth0_callback_links_existing_user(monkeypatch):
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            user = User(
                email="member@example.com",
                plan="pro",
                status="active",
                is_active=1,
            )
            session.add(user)
            await session.commit()
            existing_id = user.id

        async def override_get_db_session():
            async with Session() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_get_db_session

        profile = ProviderProfile(
            provider="auth0",
            provider_id="auth0|456",
            email="member@example.com",
            name="Member",
        )
        fake_client = _FakeAuth0Client(profile)
        monkeypatch.setattr("backend.routes.auth.get_auth0_client", lambda: fake_client)

        try:
            async with AsyncClient(app=app, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/oauth/auth0/callback",
                    json={
                        "code": "second-code",
                        "redirect_uri": "https://frontend.example.com/auth/callback",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == existing_id

            async with Session() as session:
                refreshed = await session.get(User, existing_id)
                assert refreshed is not None
                assert refreshed.auth0_user_id == "auth0|456"
                assert refreshed.email == "member@example.com"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    _run_async(scenario())


def test_auth0_callback_rejects_inactive_account(monkeypatch):
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            user = User(
                email="inactive@example.com",
                plan="pro",
                status="canceled",
                is_active=1,
            )
            session.add(user)
            await session.commit()
            inactive_id = user.id

        async def override_get_db_session():
            async with Session() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_get_db_session

        profile = ProviderProfile(
            provider="auth0",
            provider_id="auth0|789",
            email="inactive@example.com",
            name="Inactive",
        )
        fake_client = _FakeAuth0Client(profile)
        monkeypatch.setattr("backend.routes.auth.get_auth0_client", lambda: fake_client)

        try:
            async with AsyncClient(app=app, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/oauth/auth0/callback",
                    json={
                        "code": "inactive-code",
                        "redirect_uri": "https://frontend.example.com/auth/callback",
                    },
                )

            assert response.status_code == 403

            async with Session() as session:
                refreshed = await session.get(User, inactive_id)
                assert refreshed is not None
                assert refreshed.auth0_user_id is None
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    _run_async(scenario())
