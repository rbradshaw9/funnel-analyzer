"""Simple in-memory rate limiter utilities for FastAPI endpoints."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple


class RateLimitExceeded(Exception):
    """Exception raised when a rate limit would be exceeded."""

    def __init__(self, retry_after: float) -> None:
        super().__init__("Rate limit exceeded")
        self.retry_after = retry_after


class SlidingWindowRateLimiter:
    """Sliding window rate limiter using an in-memory deque per key."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window = window_seconds
        self._records: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str) -> Tuple[bool, float]:
        """Register a hit for the given key.

        Args:
            key: Unique identifier for the entity being limited (e.g., IP or user ID).

        Returns:
            tuple(bool, float): (allowed, retry_after_seconds)
        """

        if self.limit <= 0:
            return True, 0.0

        now = time.monotonic()
        async with self._lock:
            bucket = self._records[key]

            # Drop entries that fell outside the window
            window_start = now - self.window
            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= self.limit:
                retry_after = self.window - (now - bucket[0])
                return False, max(retry_after, 0.0)

            bucket.append(now)
            return True, 0.0

    def reset(self) -> None:
        """Clear all tracked hits (useful for tests)."""

        self._records.clear()


class CompositeRateLimiter:
    """Helper to combine multiple rate limiters (e.g. per-IP and per-user)."""

    def __init__(self) -> None:
        self._limiters: Dict[str, SlidingWindowRateLimiter] = {}

    def register(self, name: str, limiter: SlidingWindowRateLimiter) -> None:
        self._limiters[name] = limiter

    async def check(self, keys: Dict[str, str]) -> None:
        for name, limiter in self._limiters.items():
            key = keys.get(name)
            if key is None:
                continue

            allowed, retry_after = await limiter.hit(key)
            if not allowed:
                raise RateLimitExceeded(retry_after)

    def reset(self) -> None:
        for limiter in self._limiters.values():
            limiter.reset()