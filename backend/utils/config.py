"""
Configuration management using Pydantic settings.
Loads environment variables with validation.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    MAGIC_LINK_EXPIRATION_MINUTES: int = 30
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_CLIENT_ID: Optional[str] = None
    AUTH0_CLIENT_SECRET: Optional[str] = None
    AUTH0_AUDIENCE: Optional[str] = None

    # Default demo user (used until real auth integration is completed)
    DEFAULT_USER_EMAIL: str = "demo@funnelanalyzer.pro"
    DEFAULT_USER_NAME: str = "Demo User"
    # Optional admin bootstrap credentials. Provide secure values via environment
    # variables in deployments that require an initial admin account.
    DEFAULT_ADMIN_EMAIL: Optional[str] = None
    DEFAULT_ADMIN_NAME: str = "Funnel Analyzer Admin"
    DEFAULT_ADMIN_PASSWORD: Optional[str] = None
    
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
    EMAIL_DEFAULT_FROM: Optional[str] = "Funnel Analyzer Pro Reports <reports@funnelanalyzerpro.com>"
    EMAIL_DEFAULT_REPLY_TO: Optional[str] = "support@funnelanalyzerpro.com"

    # Automation / integrations
    THRIVECART_WEBHOOK_SECRET: Optional[str] = None
    THRIVECART_BASIC_PRODUCT_IDS: list[str] = Field(default_factory=list)
    THRIVECART_PRO_PRODUCT_IDS: list[str] = Field(default_factory=list)
    THRIVECART_BASIC_PLAN_NAMES: list[str] = Field(default_factory=lambda: [
        "Funnel Analyzer Basic",
        "Funnel Analyzer Basic Plan",
    ])
    THRIVECART_PRO_PLAN_NAMES: list[str] = Field(default_factory=lambda: [
        "Funnel Analyzer Pro",
        "Funnel Analyzer Growth Pro",
    ])
    MAUTIC_BASE_URL: Optional[str] = None
    MAUTIC_CLIENT_ID: Optional[str] = None
    MAUTIC_CLIENT_SECRET: Optional[str] = None
    MAUTIC_API_USERNAME: Optional[str] = None
    MAUTIC_API_PASSWORD: Optional[str] = None
    
    # Analysis settings
    MAX_URLS_PER_ANALYSIS: int = 10
    SCRAPE_TIMEOUT_SECONDS: int = 30
    ANALYSIS_RATE_LIMIT_PER_IP: int = 10
    ANALYSIS_RATE_LIMIT_PER_USER: int = 25
    ANALYSIS_RATE_LIMIT_WINDOW_SECONDS: int = 3600
    

settings = Settings()
