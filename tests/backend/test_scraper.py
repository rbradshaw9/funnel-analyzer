from backend.scraper import extract_funnel_steps


SAMPLE_HTML = """
<html>
  <body>
    <section class="funnel-step">
      <h2>Landing</h2>
      <p>Introduce the visitor to our solution.</p>
    </section>
    <section class="funnel-step">
      <h2>Signup</h2>
      <p>Create an account to continue.</p>
    </section>
    <section class="funnel-step">
      <h2>Upgrade</h2>
      <p>Upgrade to access premium features.</p>
    </section>
  </body>
</html>
"""


def test_extract_funnel_steps_returns_ordered_results():
    steps = extract_funnel_steps(SAMPLE_HTML)

    assert len(steps) == 3
    assert steps[0]["title"] == "Landing"
    assert steps[1]["description"] == "Create an account to continue."
    assert all("title" in step and "description" in step for step in steps)


def test_extract_funnel_steps_handles_missing_descriptions():
    html = """
    <ul>
      <li class="funnel-step"><strong>Landing</strong></li>
      <li class="funnel-step">Checkout<p>Checkout securely.</p></li>
    </ul>
    """

    steps = extract_funnel_steps(html)

    assert steps[0]["description"] == ""
    assert steps[1]["description"] == "Checkout securely."
