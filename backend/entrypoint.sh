#!/bin/bash
set -e

# Use Railway's PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

echo "🚀 Starting Funnel Analyzer Pro API on port $PORT"

# Start Gunicorn immediately - health checks need this running ASAP
# Run background tasks (Playwright, migrations) AFTER server starts
exec gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --preload &

GUNICORN_PID=$!

# Give Gunicorn a moment to start
sleep 2

# Install Playwright in background (don't block startup)
echo "📦 Installing Playwright browsers in background..."
(playwright install chromium --with-deps 2>&1 | head -20 || echo "⚠️  Playwright installation failed") &

# Run database migrations in background
echo "🔧 Running database migrations in background..."
(python -m backend.scripts.add_email_templates_table 2>&1 || echo "⚠️  Migration failed or already applied") &

# Wait for Gunicorn process
wait $GUNICORN_PID

