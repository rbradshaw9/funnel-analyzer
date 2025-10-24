"""Database models using SQLAlchemy with async support."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
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
    status_last_updated = Column(DateTime(timezone=True), nullable=True, onupdate=func.now)
    subscription_id = Column(String(150), nullable=True, index=True)
    thrivecart_customer_id = Column(String(150), nullable=True, index=True)
    access_expires_at = Column(DateTime(timezone=True), nullable=True)
    portal_update_url = Column(String(2048), nullable=True)
    last_magic_link_sent_at = Column(DateTime(timezone=True), nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    
    # Analysis results
    scores = Column(JSON, nullable=False)  # {clarity: 85, value: 90, proof: 75, design: 88, flow: 82}
    overall_score = Column(Integer, nullable=False)  # Average or weighted score
    summary = Column(Text, nullable=False)  # Executive summary from GPT-4o
    detailed_feedback = Column(JSON, nullable=False)  # Per-page feedback
    pipeline_metrics = Column(JSON, nullable=True)  # Telemetry for scrape/screenshot/LLM stages
    
    # Metadata
    analysis_duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), default="completed")  # completed, failed, processing
    error_message = Column(Text, nullable=True)
    recipient_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyses")
    pages = relationship("AnalysisPage", back_populates="analysis", cascade="all, delete-orphan")
    
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
