# syntax=docker/dockerfile:1

# Use Python 3.11 slim image for FastAPI backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for PostgreSQL, lxml, and Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure the work directory
WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (optional, for screenshot functionality)
# RUN playwright install chromium && playwright install-deps

# Copy the rest of the backend source code
COPY backend/ ./backend

# Ensure Python can resolve the backend package
ENV PYTHONPATH=/app

# Copy entrypoint script
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the default port used by the backend server
EXPOSE 8080

# Start the FastAPI application using entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
