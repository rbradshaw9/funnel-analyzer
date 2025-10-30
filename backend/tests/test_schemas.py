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


def test_performance_data_accepts_opportunity_details() -> None:
    payload = {
        "analysis_id": 3,
        "overall_score": 85,
        "scores": {
            "clarity": 85,
            "value": 83,
            "proof": 84,
            "design": 82,
            "flow": 86,
        },
        "summary": "Performance data test",
        "pages": [
            {
                "url": "https://example.com",
                "page_type": "landing_page",
                "scores": {
                    "clarity": 85,
                    "value": 83,
                    "proof": 84,
                    "design": 82,
                    "flow": 86,
                },
                "feedback": "Performance looks solid.",
                "performance_data": {
                    "performance_score": 72,
                    "lcp": 3.42,
                    "fid": 185,
                    "cls": 0.09,
                    "fcp": 1.95,
                    "speed_index": 4.12,
                    "opportunities": [
                        "Eliminate render-blocking resources (save ≈950ms) — Consider deferring non-critical JS.",
                        "Reduce initial server response time (save ≈620ms) — Optimize backend processing.",
                    ],
                    "opportunity_details": [
                        {
                            "title": "Eliminate render-blocking resources",
                            "description": "Consider deferring non-critical JS.",
                            "savings_ms": 950,
                            "score": 0.2,
                        }
                    ],
                    "core_web_vitals": {
                        "lcp": {"value": 3.42, "displayValue": "3.4 s", "score": 0.6},
                        "fid_proxy": {"value": 185, "displayValue": "185 ms", "score": 0.75},
                    },
                    "analysis_timestamp": "2024-05-01T12:00:00.000Z",
                    "url": "https://example.com",
                },
            }
        ],
        "created_at": datetime.utcnow().isoformat(),
    }

    response = AnalysisResponse.model_validate(payload)
    page = response.pages[0]

    assert page.performance_data is not None
    assert page.performance_data.performance_score == 72
    assert page.performance_data.opportunity_details is not None
    assert page.performance_data.opportunity_details[0]["title"] == "Eliminate render-blocking resources"
