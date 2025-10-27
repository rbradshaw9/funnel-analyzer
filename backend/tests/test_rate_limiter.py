"""Tests for the in-memory rate limiter utilities."""

import asyncio
import pytest

from backend.utils.rate_limiter import (
    CompositeRateLimiter,
    RateLimitExceeded,
    SlidingWindowRateLimiter,
)


def test_sliding_window_rate_limiter_respects_limit():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60)

    async def scenario() -> None:
        allowed, retry_after = await limiter.hit("example")
        assert allowed and retry_after == 0

        allowed, retry_after = await limiter.hit("example")
        assert allowed and retry_after == 0

        allowed, retry_after = await limiter.hit("example")
        assert not allowed and retry_after > 0

    asyncio.run(scenario())


def test_composite_rate_limiter_handles_missing_keys():
    limiter = CompositeRateLimiter()
    limiter.register("ip", SlidingWindowRateLimiter(limit=1, window_seconds=60))
    limiter.register("user", SlidingWindowRateLimiter(limit=1, window_seconds=60))

    async def scenario() -> None:
        # First request passes.
        await limiter.check({"ip": "ip:1", "user": "user:5"})

        # Second request from same IP should fail even if the user is omitted.
        with pytest.raises(RateLimitExceeded):
            await limiter.check({"ip": "ip:1", "user": None})

        # Different IP but same user should hit the per-user limit.
        with pytest.raises(RateLimitExceeded):
            await limiter.check({"ip": "ip:2", "user": "user:5"})

    asyncio.run(scenario())
