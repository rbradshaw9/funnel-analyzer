#!/bin/bash
set -e

# Ensure Playwright browsers are installed (retry if build-time install failed)
echo "Checking Playwright browser installation..."
if ! playwright install chromium --with-deps 2>/dev/null; then
    echo "WARNING: Playwright Chromium installation failed. Screenshot features may not work."
fi

# Run database migrations
echo "Running database migrations..."
python -m backend.scripts.add_email_templates_table || echo "Migration failed or already applied"

# Use Railway's PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

echo "Starting Gunicorn on port $PORT"

exec gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120

