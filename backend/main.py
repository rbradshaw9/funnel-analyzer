"""
Funnel Analyzer Pro - FastAPI Backend
Main application entry point with CORS, routes, and lifecycle handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

try:
    from .routes import analysis, auth, reports  # type: ignore[attr-defined]
    from .utils.config import settings  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - fallback for direct script execution
    from routes import analysis, auth, reports
    from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("🚀 Starting Funnel Analyzer Pro API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("🛑 Shutting down Funnel Analyzer Pro API")


# Initialize FastAPI app
app = FastAPI(
    title="Funnel Analyzer Pro API",
    description="Analyze and score marketing funnels using AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vercel frontend and WordPress embedding
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://app.smarttoolclub.com",
]

if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://([a-zA-Z0-9-]+)\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Funnel Analyzer Pro API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check with system status."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
