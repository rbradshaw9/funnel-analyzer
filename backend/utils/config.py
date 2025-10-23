"""
Configuration management using Pydantic settings.
Loads environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Core settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API Keys
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    
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

    # Object storage (screenshots)
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: Optional[str] = None
    AWS_S3_ACCESS_KEY_ID: Optional[str] = None
    AWS_S3_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    AWS_S3_BASE_URL: Optional[str] = None
    AWS_S3_PUBLIC_URL_EXPIRY_SECONDS: int = 86400

    # Email provider (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_DEFAULT_FROM: Optional[str] = None
    EMAIL_DEFAULT_REPLY_TO: Optional[str] = None

    # Automation / integrations
    THRIVECART_WEBHOOK_SECRET: Optional[str] = None
    MAUTIC_BASE_URL: Optional[str] = None
    MAUTIC_CLIENT_ID: Optional[str] = None
    MAUTIC_CLIENT_SECRET: Optional[str] = None
    MAUTIC_API_USERNAME: Optional[str] = None
    MAUTIC_API_PASSWORD: Optional[str] = None
    
    # Analysis settings
    MAX_URLS_PER_ANALYSIS: int = 10
    SCRAPE_TIMEOUT_SECONDS: int = 30
    

settings = Settings()
