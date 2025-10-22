"""Deterministic GPT analysis service stub.

The real project would call into an LLM provider. For testing purposes we
provide a deterministic implementation that produces an analysis summary and
annotated recommendations based solely on the extracted funnel steps.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence


class GPTAnalysisService:
    """Simple, deterministic service that summarizes funnel steps."""

    def summarize(self, steps: Sequence[dict[str, str]]) -> dict[str, object]:
        if not steps:
            return {
                "summary": "No funnel steps were detected in the provided page.",
                "recommendations": [
                    "Ensure that your landing page clearly communicates the conversion journey.",
                ],
            }

        headlines = ", ".join(step["title"] for step in steps)
        coverage = len([step for step in steps if step.get("description")])
        coverage_ratio = coverage / len(steps)
        tone = "well-documented" if coverage_ratio > 0.75 else "partially described"

        recommendations: List[str] = [
            "Consider adding more context to each step to guide your visitors.",
            "Provide a clear call-to-action at the end of the funnel.",
        ]
        if coverage_ratio < 0.5:
            recommendations.insert(
                0, "Add descriptive copy to the majority of your funnel steps."
            )

        return {
            "summary": f"The funnel covers the following stages: {headlines}. Overall the flow is {tone}.",
            "recommendations": recommendations,
        }


def format_analysis_response(
    url: str,
    steps: Iterable[dict[str, str]],
    analysis: dict[str, object],
) -> dict[str, object]:
    """Combine raw scraping results with the GPT analysis output."""

    steps_list = list(steps)
    return {
        "url": url,
        "steps": steps_list,
        "summary": analysis["summary"],
        "recommendations": analysis.get("recommendations", []),
    }


__all__ = ["GPTAnalysisService", "format_analysis_response"]
