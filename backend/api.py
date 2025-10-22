"""Lightweight in-process API surface for funnel analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

from .gpt_service import GPTAnalysisService, format_analysis_response
from .scraper import extract_funnel_steps


@dataclass
class AnalyzeRequest:
    url: str
    html: str | None = None

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if not (parsed.scheme and parsed.netloc):
            raise ValueError("`url` must be an absolute URL")


class FunnelAPI:
    """A simple object that mimics typical API routes for testing."""

    def __init__(self, service: GPTAnalysisService | None = None) -> None:
        self._service = service or GPTAnalysisService()

    def health(self) -> Dict[str, str]:
        return {"status": "ok"}

    def analyze(self, payload: AnalyzeRequest) -> Dict[str, object]:
        if not payload.html:
            raise ValueError("HTML content is required for analysis in this demo.")

        steps = extract_funnel_steps(payload.html)
        analysis = self._service.summarize(steps)
        return format_analysis_response(payload.url, steps, analysis)

    def embed(self, url: str) -> Dict[str, object]:
        parsed = urlparse(url)
        if not (parsed.scheme and parsed.netloc):
            raise ValueError("`url` must be an absolute URL")

        sample_steps = [
            {"title": "Landing Page", "description": "Introduce the product"},
            {"title": "Signup", "description": "Collect user details"},
            {"title": "Upgrade", "description": "Promote premium plans"},
        ]
        analysis = self._service.summarize(sample_steps)
        response = format_analysis_response(url, sample_steps, analysis)
        return {
            "url": response["url"],
            "summary": response["summary"],
            "steps": response["steps"],
        }


app = FunnelAPI()


__all__ = ["AnalyzeRequest", "FunnelAPI", "app"]
