"""
Database models using SQLAlchemy with async support.
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication and report ownership."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    wordpress_user_id = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
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
    
    # Metadata
    analysis_duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), default="completed")  # completed, failed, processing
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
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
    
    # Page-specific scores
    page_scores = Column(JSON, nullable=True)
    page_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AnalysisPage {self.url}>"
