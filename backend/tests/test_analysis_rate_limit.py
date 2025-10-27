"""Integration tests around the analysis endpoint rate limiting."""

import asyncio
import sys
import types
from datetime import datetime

fake_bcrypt = types.SimpleNamespace(
    hashpw=lambda password, salt: b"stub-hash",
    gensalt=lambda: b"stub-salt",
    checkpw=lambda password, hashed: True,
)
sys.modules.setdefault("bcrypt", fake_bcrypt)

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from backend.models.schemas import AnalysisResponse, PageAnalysis, ScoreBreakdown
from backend.routes.analysis import analysis_rate_limiter, router as analysis_router
from backend.routes.dependencies import get_current_user
from backend.db.session import get_db_session
from backend.utils.rate_limiter import SlidingWindowRateLimiter


app = FastAPI()
app.include_router(analysis_router, prefix="/api")


def test_analyze_endpoint_enforces_rate_limit(monkeypatch):
    # Use tight limits to make the test fast and deterministic.
    analysis_rate_limiter._limiters["ip"] = SlidingWindowRateLimiter(limit=1, window_seconds=60)
    analysis_rate_limiter._limiters["user"] = SlidingWindowRateLimiter(limit=1, window_seconds=60)
    analysis_rate_limiter.reset()

    async def fake_analyze_funnel(urls, session, user_id, recipient_email):  # noqa: ARG001
        score = ScoreBreakdown(clarity=50, value=50, proof=50, design=50, flow=50)
        page = PageAnalysis(url=str(urls[0]), scores=score, feedback="Looks good")
        return AnalysisResponse(
            analysis_id=1,
            overall_score=50,
            scores=score,
            summary="Stub summary",
            pages=[page],
            created_at=datetime.utcnow(),
        )

    monkeypatch.setattr("backend.routes.analysis.analyze_funnel", fake_analyze_funnel)

    async def fake_session():
        yield None

    app.dependency_overrides[get_db_session] = fake_session
    app.dependency_overrides[get_current_user] = lambda: types.SimpleNamespace(id=42)

    async def scenario() -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {"urls": ["https://example.com"], "email": None}
            first_response = await client.post("/api/analyze", json=payload)
            assert first_response.status_code == 200

            second_response = await client.post("/api/analyze", json=payload)
            assert second_response.status_code == 429
            assert "Retry-After" in second_response.headers
            assert second_response.json()["detail"].lower().startswith("too many analysis requests")

    asyncio.run(scenario())

    analysis_rate_limiter.reset()
    app.dependency_overrides.clear()
