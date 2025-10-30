"""Attribution service for matching conversions to funnel sessions."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import FunnelSession, Conversion
from ..utils.fingerprint import generate_fingerprint

logger = logging.getLogger(__name__)


class AttributionResult:
    """Result of attribution attempt with confidence scoring."""
    
    def __init__(
        self,
        session: Optional[FunnelSession] = None,
        method: str = "none",
        confidence: int = 0,
        metadata: Optional[dict] = None,
    ):
        self.session = session
        self.method = method
        self.confidence = confidence
        self.metadata = metadata or {}


class AttributionService:
    """
    Service for attributing conversions to funnel sessions.
    
    Implements a waterfall strategy:
    1. Email match (95% confidence)
    2. Order ID match (100% confidence if available)
    3. Session fingerprint match (90% confidence)
    4. User ID match (85% confidence)
    5. Probabilistic match based on IP + timing (50-70% confidence)
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def attribute_conversion(
        self,
        analysis_id: int,
        email: Optional[str] = None,
        order_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        conversion_time: Optional[datetime] = None,
    ) -> AttributionResult:
        """
        Attribute a conversion to a session using waterfall strategy.
        
        Args:
            analysis_id: The analysis/funnel report ID
            email: Customer email from checkout/webhook
            order_id: Order ID if tracked through funnel
            user_id: External user ID if available
            session_fingerprint: Client-provided session fingerprint
            ip_address: IP address at conversion time
            user_agent: User agent at conversion time
            conversion_time: When the conversion occurred
        
        Returns:
            AttributionResult with matched session and confidence
        """
        conversion_time = conversion_time or datetime.utcnow()
        
        # Strategy 1: Order ID match (highest confidence)
        if order_id:
            result = await self._match_by_order_id(analysis_id, order_id)
            if result.session:
                logger.info(f"Attribution via order_id: {order_id} -> session {result.session.session_id}")
                return result
        
        # Strategy 2: Email match (very high confidence for opt-in funnels)
        if email:
            result = await self._match_by_email(analysis_id, email, conversion_time)
            if result.session:
                logger.info(f"Attribution via email: {email} -> session {result.session.session_id}")
                return result
        
        # Strategy 3: Session fingerprint match (high confidence)
        if session_fingerprint:
            result = await self._match_by_session_fingerprint(analysis_id, session_fingerprint)
            if result.session:
                logger.info(f"Attribution via fingerprint: {session_fingerprint} -> session {result.session.session_id}")
                return result
        
        # Strategy 4: User ID match (high confidence if using external auth)
        if user_id:
            result = await self._match_by_user_id(analysis_id, user_id)
            if result.session:
                logger.info(f"Attribution via user_id: {user_id} -> session {result.session.session_id}")
                return result
        
        # Strategy 5: Probabilistic match based on device fingerprint + timing
        if ip_address and user_agent:
            result = await self._match_probabilistic(
                analysis_id, ip_address, user_agent, conversion_time
            )
            if result.session:
                logger.info(
                    f"Attribution via probabilistic: IP {ip_address} -> session {result.session.session_id} "
                    f"(confidence: {result.confidence}%)"
                )
                return result
        
        # No match found
        logger.warning(f"No attribution found for analysis {analysis_id}")
        return AttributionResult(method="none", confidence=0)
    
    async def _match_by_order_id(self, analysis_id: int, order_id: str) -> AttributionResult:
        """Match by order ID tracked in session."""
        query = select(FunnelSession).where(
            and_(
                FunnelSession.analysis_id == analysis_id,
                FunnelSession.order_id == order_id,
            )
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            return AttributionResult(
                session=session,
                method="order_id",
                confidence=100,
                metadata={"matched_order_id": order_id}
            )
        
        return AttributionResult(method="order_id_failed", confidence=0)
    
    async def _match_by_email(
        self, analysis_id: int, email: str, conversion_time: datetime
    ) -> AttributionResult:
        """
        Match by email, preferring the most recent session.
        
        For opt-in funnels, email is captured early and is highly reliable.
        For direct-purchase funnels, we get it at checkout.
        """
        # Look for sessions within the last 24 hours with this email
        time_window = conversion_time - timedelta(hours=24)
        
        query = (
            select(FunnelSession)
            .where(
                and_(
                    FunnelSession.analysis_id == analysis_id,
                    FunnelSession.email == email.lower().strip(),
                    FunnelSession.first_seen_at >= time_window,
                )
            )
            .order_by(desc(FunnelSession.last_seen_at))
        )
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            # Calculate confidence based on time proximity
            time_diff = (conversion_time - session.last_seen_at).total_seconds() / 60  # minutes
            
            if time_diff <= 30:  # Within 30 minutes
                confidence = 95
            elif time_diff <= 120:  # Within 2 hours
                confidence = 90
            elif time_diff <= 360:  # Within 6 hours
                confidence = 85
            else:  # Within 24 hours
                confidence = 75
            
            return AttributionResult(
                session=session,
                method="email",
                confidence=confidence,
                metadata={
                    "matched_email": email,
                    "time_diff_minutes": int(time_diff)
                }
            )
        
        return AttributionResult(method="email_failed", confidence=0)
    
    async def _match_by_session_fingerprint(
        self, analysis_id: int, session_fingerprint: str
    ) -> AttributionResult:
        """Match by client-provided session fingerprint (UUID)."""
        query = select(FunnelSession).where(
            and_(
                FunnelSession.analysis_id == analysis_id,
                FunnelSession.session_id == session_fingerprint,
            )
        )
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            return AttributionResult(
                session=session,
                method="session_fingerprint",
                confidence=90,
                metadata={"matched_session_id": session_fingerprint}
            )
        
        return AttributionResult(method="session_fingerprint_failed", confidence=0)
    
    async def _match_by_user_id(self, analysis_id: int, user_id: str) -> AttributionResult:
        """Match by external user ID (for sites with authentication)."""
        query = (
            select(FunnelSession)
            .where(
                and_(
                    FunnelSession.analysis_id == analysis_id,
                    FunnelSession.user_id == user_id,
                )
            )
            .order_by(desc(FunnelSession.last_seen_at))
        )
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            return AttributionResult(
                session=session,
                method="user_id",
                confidence=85,
                metadata={"matched_user_id": user_id}
            )
        
        return AttributionResult(method="user_id_failed", confidence=0)
    
    async def _match_probabilistic(
        self,
        analysis_id: int,
        ip_address: str,
        user_agent: str,
        conversion_time: datetime,
    ) -> AttributionResult:
        """
        Probabilistic matching based on device fingerprint and timing.
        
        This is a fallback when we don't have explicit identifiers.
        Works well for direct-purchase funnels where conversion happens
        quickly after landing.
        """
        # Generate device fingerprint
        device_fingerprint = generate_fingerprint(
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        # Look for sessions within the last 2 hours with matching fingerprint
        time_window = conversion_time - timedelta(hours=2)
        
        query = (
            select(FunnelSession)
            .where(
                and_(
                    FunnelSession.analysis_id == analysis_id,
                    FunnelSession.fingerprint == device_fingerprint,
                    FunnelSession.first_seen_at >= time_window,
                )
            )
            .order_by(desc(FunnelSession.last_seen_at))
        )
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            # Calculate confidence based on time proximity
            time_diff = (conversion_time - session.last_seen_at).total_seconds() / 60  # minutes
            
            if time_diff <= 5:  # Within 5 minutes
                confidence = 70
            elif time_diff <= 15:  # Within 15 minutes
                confidence = 65
            elif time_diff <= 30:  # Within 30 minutes
                confidence = 60
            elif time_diff <= 60:  # Within 1 hour
                confidence = 55
            else:  # Within 2 hours
                confidence = 50
            
            return AttributionResult(
                session=session,
                method="probabilistic",
                confidence=confidence,
                metadata={
                    "matched_fingerprint": device_fingerprint,
                    "time_diff_minutes": int(time_diff),
                    "ip_address": ip_address,
                }
            )
        
        return AttributionResult(method="probabilistic_failed", confidence=0)
