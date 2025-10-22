# Funnel Analyzer

This repository contains a lightweight demonstration of a funnel analysis
stack. It includes a pure-Python backend with scraping helpers and GPT
analysis service stubs, alongside a static frontend that can be exercised
through Playwright end-to-end tests.

## Backend

The backend uses only the Python standard library. Run the test suite with:

```bash
python -m pytest
```

## Frontend

The frontend is a static site served via `http-server` with Playwright tests
located in `frontend/tests`.

```bash
cd frontend
npm install
npm run test:e2e
```

## Monorepo test helpers

The root `package.json` exposes a single `npm test` command that runs both the
backend pytest suite and the frontend Playwright scenarios.
