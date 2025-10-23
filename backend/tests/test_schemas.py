"""Schema regression tests."""

from datetime import datetime

from backend.models.schemas import (
    AnalysisResponse,
    AuthValidateResponse,
    CTARecommendation,
    MagicLinkResponse,
)


def test_cta_recommendation_alias_round_trip() -> None:
    payload = {"copy": "Buy now", "location": "hero", "reason": "Drive clicks"}
    recommendation = CTARecommendation.model_validate(payload)

    assert recommendation.cta_copy == "Buy now"
    assert recommendation.model_dump(by_alias=True)["copy"] == "Buy now"


def test_analysis_response_accepts_cta_alias() -> None:
    payload = {
        "analysis_id": 1,
        "overall_score": 80,
        "scores": {
            "clarity": 80,
            "value": 82,
            "proof": 78,
            "design": 79,
            "flow": 81,
        },
        "summary": "Test summary",
        "pages": [
            {
                "url": "https://example.com",
                "page_type": "sales_page",
                "scores": {
                    "clarity": 80,
                    "value": 82,
                    "proof": 78,
                    "design": 79,
                    "flow": 81,
                },
                "feedback": "Solid page",
                "cta_recommendations": [
                    {"copy": "Buy now", "location": "hero", "reason": "Drive clicks"}
                ],
            }
        ],
        "created_at": datetime.utcnow().isoformat(),
    }

    response = AnalysisResponse.model_validate(payload)
    output = response.model_dump(by_alias=True)

    cta = output["pages"][0]["cta_recommendations"][0]
    assert cta["copy"] == "Buy now"


def test_auth_validate_response_defaults() -> None:
    response = AuthValidateResponse(valid=False, message="nope")
    assert response.access_granted is False


def test_magic_link_response_schema() -> None:
    payload = MagicLinkResponse(status="sent", message="ok")
    assert payload.status == "sent"


def test_analysis_response_accepts_pipeline_metrics() -> None:
    payload = {
        "analysis_id": 2,
        "overall_score": 78,
        "scores": {
            "clarity": 78,
            "value": 80,
            "proof": 75,
            "design": 79,
            "flow": 76,
        },
        "summary": "Telemetry test",
        "pages": [
            {
                "url": "https://example.com",
                "page_type": "sales_page",
                "scores": {
                    "clarity": 78,
                    "value": 80,
                    "proof": 75,
                    "design": 79,
                    "flow": 76,
                },
                "feedback": "Looks good",
            }
        ],
        "created_at": datetime.utcnow().isoformat(),
        "pipeline_metrics": {
            "stage_timings": {
                "scrape_seconds": 1.234,
                "analysis_seconds": 4.567,
                "screenshot_seconds": 0.321,
                "total_seconds": 6.789,
            },
            "screenshot": {
                "attempted": 1,
                "succeeded": 1,
                "failed": 0,
                "uploaded": 1,
                "timeouts": 0,
            },
            "llm_provider": "openai",
        },
    }

    response = AnalysisResponse.model_validate(payload)

    assert response.pipeline_metrics is not None
    assert response.pipeline_metrics.stage_timings is not None
    assert response.pipeline_metrics.stage_timings.scrape_seconds == 1.234
    assert response.pipeline_metrics.screenshot is not None
    assert response.pipeline_metrics.screenshot.uploaded == 1
