"""Database models using SQLAlchemy with async support."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model for authentication and report ownership."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    wordpress_user_id = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)
    plan = Column(String(50), nullable=False, default="free", server_default="free")
    status = Column(String(50), nullable=False, default="active", server_default="active")
    role = Column(String(50), nullable=False, default="member", server_default="member")
    status_reason = Column(String(255), nullable=True)
    status_last_updated = Column(DateTime(timezone=True), nullable=True, server_onupdate=text("CURRENT_TIMESTAMP"))  # type: ignore
    subscription_id = Column(String(150), nullable=True, index=True)
    thrivecart_customer_id = Column(String(150), nullable=True, index=True)
    access_expires_at = Column(DateTime(timezone=True), nullable=True)
    portal_update_url = Column(String(2048), nullable=True)
    last_magic_link_sent_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String(255), nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'github', etc.
    oauth_provider_id = Column(String(255), nullable=True, index=True)  # Provider's user ID
    oauth_refresh_token = Column(String(512), nullable=True)  # For OAuth token refresh
    refresh_token_hash = Column(String(255), nullable=True)  # For JWT refresh token
    
    # Profile fields
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    avatar_url = Column(String(2048), nullable=True)
    onboarding_completed = Column(Integer, default=0)  # 0 = incomplete, 1 = complete
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=text("CURRENT_TIMESTAMP"))  # type: ignore

    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Analysis(Base):
    """Analysis model storing funnel analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Input data
    urls = Column(JSON, nullable=False)  # List of URLs analyzed
    
    # Analysis naming and versioning
    name = Column(String(255), nullable=True)  # Optional user-provided name
    parent_analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True, index=True)  # For re-runs
    
    # Analysis results
    scores = Column(JSON, nullable=False)  # {clarity: 85, value: 90, proof: 75, design: 88, flow: 82}
    overall_score = Column(Integer, nullable=False)  # Average or weighted score
    summary = Column(Text, nullable=False)  # Executive summary from GPT-4o
    detailed_feedback = Column(JSON, nullable=False)  # Per-page feedback
    pipeline_metrics = Column(JSON, nullable=True)  # Telemetry for scrape/screenshot/LLM stages
    recommendation_completions = Column(JSON, nullable=True)  # User completion tracking for recommendations
    
    # Metadata
    analysis_duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), default="completed")  # completed, failed, processing
    error_message = Column(Text, nullable=True)
    recipient_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyses")
    pages = relationship("AnalysisPage", back_populates="analysis", cascade="all, delete-orphan")
    
    # Self-referential relationship for re-run tracking
    parent_analysis = relationship("Analysis", remote_side=[id], backref="child_analyses")
    
    def __repr__(self):
        return f"<Analysis {self.id} - Score: {self.overall_score}>"


class AnalysisPage(Base):
    """Individual page data within an analysis."""
    
    __tablename__ = "analysis_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    
    url = Column(String(2048), nullable=False)
    page_type = Column(String(100), nullable=True)  # sales, order_form, upsell, thank_you
    
    # Scraped content
    title = Column(String(500), nullable=True)
    text_content = Column(Text, nullable=True)
    screenshot_url = Column(String(2048), nullable=True)
    screenshot_storage_key = Column(String(2048), nullable=True, index=True)
    
    # Page-specific scores
    page_scores = Column(JSON, nullable=True)
    page_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("Analysis", back_populates="pages")
    
    def __repr__(self):
        return f"<AnalysisPage {self.url}>"


class WebhookEvent(Base):
    """Raw webhook payloads for audit trails and replay support."""

    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    event_type = Column(String(150), nullable=True)
    payload = Column(JSON, nullable=False)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<WebhookEvent {self.source}:{self.id}>"


class EmailTemplate(Base):
    """Custom email templates for transactional emails."""

    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # magic_link, welcome, etc.
    subject = Column(String(500), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_custom = Column(Integer, default=1)  # 1 = custom, 0 = default
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=text("CURRENT_TIMESTAMP"))  # type: ignore

    def __repr__(self) -> str:
        return f"<EmailTemplate {self.name}>"


class FunnelSession(Base):
    """Track user sessions through funnel for conversion attribution."""

    __tablename__ = "funnel_sessions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    
    # Session identification
    session_id = Column(String(255), unique=True, nullable=False, index=True)  # Client-generated UUID
    fingerprint = Column(String(255), nullable=False, index=True)  # Device fingerprint hash
    
    # Visitor information (captured when available)
    email = Column(String(255), nullable=True, index=True)  # Captured at opt-in or checkout
    user_id = Column(String(255), nullable=True, index=True)  # External user ID if provided
    order_id = Column(String(255), nullable=True, index=True)  # Order ID if passed through funnel
    
    # Session metadata
    landing_page = Column(String(2048), nullable=True)
    referrer = Column(String(2048), nullable=True)
    utm_source = Column(String(255), nullable=True)
    utm_medium = Column(String(255), nullable=True)
    utm_campaign = Column(String(255), nullable=True)
    utm_content = Column(String(255), nullable=True)
    utm_term = Column(String(255), nullable=True)
    
    # Device/browser info for fingerprinting
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(1024), nullable=True)
    screen_resolution = Column(String(50), nullable=True)
    timezone = Column(String(100), nullable=True)
    language = Column(String(50), nullable=True)
    
    # Journey tracking
    page_views = Column(Integer, default=0)  # Count of pages viewed
    events = Column(JSON, nullable=True)  # [{type: 'click', target: 'cta-button', timestamp: ...}]
    last_page_url = Column(String(2048), nullable=True)
    
    # Timestamps
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    analysis = relationship("Analysis", backref="sessions")
    conversions = relationship("Conversion", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<FunnelSession {self.session_id}>"


class Conversion(Base):
    """Track conversions and attribute them to sessions."""

    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("funnel_sessions.id"), nullable=True, index=True)
    
    # Conversion identification
    conversion_id = Column(String(255), unique=True, nullable=False, index=True)  # External order/conversion ID
    
    # Conversion data from webhook
    email = Column(String(255), nullable=True, index=True)
    customer_name = Column(String(255), nullable=True)
    revenue = Column(Integer, nullable=True)  # Stored in cents to avoid floating point issues
    currency = Column(String(10), nullable=False, default="USD")
    product_name = Column(String(500), nullable=True)
    
    # Attribution metadata
    attribution_method = Column(String(100), nullable=True)  # email, order_id, fingerprint, probabilistic, none
    attribution_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    attribution_metadata = Column(JSON, nullable=True)  # Additional attribution context
    
    # Webhook metadata
    webhook_source = Column(String(100), nullable=True)  # stripe, infusionsoft, manual, etc.
    webhook_payload = Column(JSON, nullable=True)  # Original webhook payload
    
    # Timestamps
    converted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    attributed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", backref="conversions")
    session = relationship("FunnelSession", back_populates="conversions")

    def __repr__(self) -> str:
        return f"<Conversion {self.conversion_id} - ${self.revenue/100 if self.revenue else 0}>"

