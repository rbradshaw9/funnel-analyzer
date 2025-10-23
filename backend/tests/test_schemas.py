"""Schema regression tests."""

from datetime import datetime

from backend.models.schemas import AnalysisResponse, CTARecommendation


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
