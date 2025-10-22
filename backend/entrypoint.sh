#!/bin/bash
set -e

# Use Railway's PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

echo "Starting Gunicorn on port $PORT"

exec gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120
