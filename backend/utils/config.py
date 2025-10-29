"""
Configuration management using Pydantic settings.
Loads environment variables with validation.
"""

from typing import Optional, Union
import json

from pydantic import Field, field_validator
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
    GOOGLE_PAGESPEED_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./funnel_analyzer.db"
    
    # Authentication
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    MAGIC_LINK_EXPIRATION_MINUTES: int = 30

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
    EMAIL_DEFAULT_FROM: Optional[str] = "Ryan at Funnel Analyzer Pro <ryan@funnelanalyzerpro.com>"
    EMAIL_DEFAULT_REPLY_TO: Optional[str] = "ryan@funnelanalyzerpro.com"

    # OAuth providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: Optional[str] = None  # e.g. https://api.funnelanalyzerpro.com/api/auth/oauth/callback

    # Automation / integrations
    THRIVECART_WEBHOOK_SECRET: Optional[str] = None
    THRIVECART_BASIC_PRODUCT_IDS: Union[list[str], str] = Field(default_factory=list)
    THRIVECART_PRO_PRODUCT_IDS: Union[list[str], str] = Field(default_factory=list)
    THRIVECART_BASIC_PLAN_NAMES: list[str] = Field(default_factory=lambda: [
        "Funnel Analyzer Basic",
        "Funnel Analyzer Basic Plan",
    ])
    THRIVECART_PRO_PLAN_NAMES: list[str] = Field(default_factory=lambda: [
        "Funnel Analyzer Pro",
        "Funnel Analyzer Growth Pro",
    ])
    
    @field_validator('THRIVECART_BASIC_PRODUCT_IDS', 'THRIVECART_PRO_PRODUCT_IDS', mode='before')
    @classmethod
    def parse_product_ids(cls, v):
        """Parse product IDs from various formats (JSON array, CSV, single value)."""
        if not v:
            return []
        if isinstance(v, list):
            return [str(item) for item in v]
        if isinstance(v, str):
            # Try parsing as JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
                return [str(parsed)]
            except (json.JSONDecodeError, ValueError):
                # Try comma-separated values
                if ',' in v:
                    return [item.strip() for item in v.split(',') if item.strip()]
                # Single value
                return [v.strip()]
        # Handle integers or other types
        return [str(v)]
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
