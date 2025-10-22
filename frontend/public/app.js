const SAMPLE_ANALYSIS = {
  summary:
    "The funnel covers the following stages: Landing Page, Signup, Upgrade. Overall the flow is well-documented.",
  steps: [
    { title: "Landing Page", description: "Welcome visitors and highlight the value proposition." },
    { title: "Signup", description: "Collect the visitor's email address." },
    { title: "Upgrade", description: "Encourage upgrading to the premium plan." },
  ],
  recommendations: [
    "Include testimonials to build trust before the signup step.",
    "Showcase pricing benefits within the upgrade step.",
  ],
};

function renderList(container, items) {
  container.innerHTML = "";
  items.forEach((item) => {
    const element = document.createElement("li");
    if (typeof item === "string") {
      element.textContent = item;
    } else {
      element.innerHTML = `<strong>${item.title}</strong>: ${item.description}`;
    }
    container.appendChild(element);
  });
}

function renderAnalysis(target, analysis) {
  const { summary, steps, recommendations } = analysis;
  target.querySelector('[data-testid="analysis-summary"]').textContent = summary;
  renderList(target.querySelector('[data-testid="analysis-steps"]'), steps);
  renderList(
    target.querySelector('[data-testid="analysis-recommendations"]'),
    recommendations
  );
  target.hidden = false;
}

function bootstrapAnalyzeForm() {
  const form = document.getElementById("analysis-form");
  if (!form) {
    return;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const url = new FormData(form).get("url");
    if (!url) {
      return;
    }

    const results = document.getElementById("analysis-results");
    const customized = {
      ...SAMPLE_ANALYSIS,
      summary: SAMPLE_ANALYSIS.summary.replace(
        "Landing Page, Signup, Upgrade",
        `Landing Page, Signup, Upgrade for ${url}`
      ),
    };

    renderAnalysis(results, customized);
  });
}

function bootstrapEmbedView() {
  const container = document.querySelector("main[data-embed]");
  if (!container) {
    return;
  }

  const summaryTarget = container.querySelector('[data-testid="embed-summary"]');
  const stepsTarget = container.querySelector('[data-testid="embed-steps"]');
  const params = new URLSearchParams(window.location.search);
  const targetUrl = params.get("url") ?? "https://example.com";

  summaryTarget.textContent = SAMPLE_ANALYSIS.summary.replace(
    "Landing Page, Signup, Upgrade",
    `Landing Page, Signup, Upgrade for ${targetUrl}`
  );

  stepsTarget.innerHTML = "";
  SAMPLE_ANALYSIS.steps.forEach((step) => {
    const item = document.createElement("li");
    item.textContent = `${step.title}: ${step.description}`;
    stepsTarget.appendChild(item);
  });
}

bootstrapAnalyzeForm();
bootstrapEmbedView();
