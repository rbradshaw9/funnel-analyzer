from backend.gpt_service import GPTAnalysisService, format_analysis_response


def test_gpt_service_returns_summary_and_recommendations():
    service = GPTAnalysisService()
    steps = [
        {"title": "Landing", "description": "Introduce"},
        {"title": "Signup", "description": ""},
        {"title": "Upgrade", "description": "Upsell"},
    ]

    analysis = service.summarize(steps)

    assert "Landing" in analysis["summary"]
    assert len(analysis["recommendations"]) >= 2


def test_format_analysis_response_merges_sections():
    service = GPTAnalysisService()
    steps = [{"title": "Landing", "description": "Intro"}]
    response = format_analysis_response(
        "https://example.com", steps, service.summarize(steps)
    )

    assert response["url"] == "https://example.com"
    assert response["steps"] == steps
    assert "summary" in response
