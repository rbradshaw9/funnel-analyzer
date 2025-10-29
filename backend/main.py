"""
Funnel Analyzer Pro - FastAPI Backend
Main application entry point with CORS, routes, and lifecycle handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import logging

from .db.session import init_db
from .routes import analysis, auth, metrics, reports, webhooks, oauth, user, admin, health, cleanup
from .utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    await init_db()
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
    "https://funnelanalyzerpro.com",
    "https://www.funnelanalyzerpro.com",
]

if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL.rstrip("/"))

# Add session middleware for OAuth (required by authlib)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,  # Use the same secret for simplicity
    max_age=3600,  # 1 hour session lifetime for OAuth flow
)

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
app.include_router(oauth.router, prefix="/api", tags=["OAuth"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(cleanup.router, prefix="/api/admin/screenshots", tags=["Cleanup"])
app.include_router(health.router, tags=["Health"])


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
    openai_status = "configured" if (settings.OPENAI_API_KEY or "").strip() else "not_configured"

    return {
        "status": "healthy",
        "database": "connected",
        "openai": openai_status,
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
