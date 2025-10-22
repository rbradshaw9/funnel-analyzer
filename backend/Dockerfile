# syntax=docker/dockerfile:1

# Use Python 3.11 slim image for FastAPI backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for PostgreSQL and Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure the work directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (optional, for screenshot functionality)
# RUN playwright install chromium && playwright install-deps

# Copy the rest of the backend source code
COPY . .

# Expose the default port used by the backend server
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/health')"

# Start the FastAPI application with Gunicorn
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:3000", "--timeout", "120"]
