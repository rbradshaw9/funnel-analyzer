"""
Configuration management using Pydantic settings.
Loads environment variables with validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Core settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Keys
    OPENAI_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./funnel_analyzer.db"
    
    # Authentication
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Default demo user (used until real auth integration is completed)
    DEFAULT_USER_EMAIL: str = "demo@funnelanalyzer.pro"
    DEFAULT_USER_NAME: str = "Demo User"
    
    # External services
    FRONTEND_URL: str = "http://localhost:3001"
    WORDPRESS_API_URL: Optional[str] = None
    
    # Analysis settings
    MAX_URLS_PER_ANALYSIS: int = 10
    SCRAPE_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env (like frontend vars)


settings = Settings()
