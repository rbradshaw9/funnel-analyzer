"""LLM provider registry to allow swapping model vendors without touching business logic."""

from __future__ import annotations

import logging
from typing import Protocol

from ..utils.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    async def analyze_page(self, *args, **kwargs):  # noqa: ANN401 - protocol mirrors provider signature
        ...

    async def analyze_funnel_summary(self, *args, **kwargs):  # noqa: ANN401
        ...


_provider_cache: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider as a singleton."""
    global _provider_cache

    if _provider_cache is not None:
        return _provider_cache

    provider_key = settings.LLM_PROVIDER.lower()

    if provider_key == "openai":
        from .openai_service import get_openai_service

        _provider_cache = get_openai_service()
        logger.info("LLM provider initialised: OpenAI")
        return _provider_cache

    raise ValueError(f"Unsupported LLM provider '{settings.LLM_PROVIDER}'")


def reset_llm_provider() -> None:
    global _provider_cache
    _provider_cache = None
