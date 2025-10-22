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
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/funnel_analyzer"
    
    # Authentication
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # External services
    FRONTEND_URL: str = "http://localhost:3001"
    WORDPRESS_API_URL: Optional[str] = None
    
    # Analysis settings
    MAX_URLS_PER_ANALYSIS: int = 10
    SCRAPE_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
