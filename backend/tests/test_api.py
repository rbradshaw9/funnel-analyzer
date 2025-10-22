from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    data: dict[str, Any] = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Funnel Analyzer Pro API"


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    data: dict[str, Any] = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "openai" in data


def test_analyze_endpoint_returns_mock_payload(client: TestClient) -> None:
    payload = {"urls": ["https://example.com", "https://example.com/checkout"]}
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == HTTPStatus.OK

    data: dict[str, Any] = response.json()
    assert "analysis_id" in data
    assert data["overall_score"] >= 0
    assert data["pages"]
    assert len(data["pages"]) == len(payload["urls"])
