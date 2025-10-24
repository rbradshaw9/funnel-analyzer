"""Tests for the in-memory rate limiter utilities."""

import pytest

from backend.utils.rate_limiter import (
    CompositeRateLimiter,
    RateLimitExceeded,
    SlidingWindowRateLimiter,
)


@pytest.mark.asyncio
async def test_sliding_window_rate_limiter_respects_limit():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60)

    allowed, retry_after = await limiter.hit("example")
    assert allowed and retry_after == 0

    allowed, retry_after = await limiter.hit("example")
    assert allowed and retry_after == 0

    allowed, retry_after = await limiter.hit("example")
    assert not allowed and retry_after > 0


@pytest.mark.asyncio
async def test_composite_rate_limiter_handles_missing_keys():
    limiter = CompositeRateLimiter()
    limiter.register("ip", SlidingWindowRateLimiter(limit=1, window_seconds=60))
    limiter.register("user", SlidingWindowRateLimiter(limit=1, window_seconds=60))

    # First request passes.
    await limiter.check({"ip": "ip:1", "user": "user:5"})

    # Second request from same IP should fail even if the user is omitted.
    with pytest.raises(RateLimitExceeded):
        await limiter.check({"ip": "ip:1", "user": None})

    # Different IP but same user should hit the per-user limit.
    with pytest.raises(RateLimitExceeded):
        await limiter.check({"ip": "ip:2", "user": "user:5"})
