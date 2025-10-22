import pytest

from backend.api import AnalyzeRequest, FunnelAPI

api = FunnelAPI()


HTML_FIXTURE = """
<section class="funnel-step">
  <h2>Landing</h2>
  <p>Introduce visitors.</p>
</section>
<section class="funnel-step">
  <h2>Checkout</h2>
  <p>Collect payment details.</p>
</section>
"""


def test_health_endpoint_returns_ok():
    assert api.health() == {"status": "ok"}


def test_analyze_endpoint_processes_html_payload():
    payload = AnalyzeRequest(url="https://example.com", html=HTML_FIXTURE)

    body = api.analyze(payload)

    assert body["url"] == payload.url
    assert len(body["steps"]) == 2
    assert "summary" in body


def test_embed_endpoint_returns_static_payload():
    body = api.embed("https://example.com")

    assert body["url"] == "https://example.com"
    assert len(body["steps"]) == 3


def test_analyze_requires_valid_url():
    with pytest.raises(ValueError):
        AnalyzeRequest(url="/relative", html=HTML_FIXTURE)


def test_analyze_requires_html_content():
    payload = AnalyzeRequest(url="https://example.com")

    with pytest.raises(ValueError):
        api.analyze(payload)
