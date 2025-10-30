"""Database migrations for conversion tracking tables."""

import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def migration_lock(conn: AsyncConnection):
    """Minimal lock context for migration safety."""
    yield


async def ensure_funnel_sessions_table(conn: AsyncConnection) -> None:
    """Create funnel_sessions table if it doesn't exist."""
    try:
        await conn.execute(text("SELECT 1 FROM funnel_sessions LIMIT 1"))
        logger.info("✓ funnel_sessions table exists")
    except Exception:
        logger.info("Creating funnel_sessions table...")
        await conn.execute(text("""
            CREATE TABLE funnel_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                session_id VARCHAR(255) NOT NULL UNIQUE,
                fingerprint VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                user_id VARCHAR(255),
                order_id VARCHAR(255),
                landing_page VARCHAR(2048),
                referrer VARCHAR(2048),
                utm_source VARCHAR(255),
                utm_medium VARCHAR(255),
                utm_campaign VARCHAR(255),
                utm_content VARCHAR(255),
                utm_term VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent VARCHAR(1024),
                screen_resolution VARCHAR(50),
                timezone VARCHAR(100),
                language VARCHAR(50),
                page_views INTEGER DEFAULT 0,
                events TEXT,
                last_page_url VARCHAR(2048),
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        """))
        
        # Create indexes
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_analysis_id ON funnel_sessions(analysis_id)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_session_id ON funnel_sessions(session_id)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_fingerprint ON funnel_sessions(fingerprint)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_email ON funnel_sessions(email)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_user_id ON funnel_sessions(user_id)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_order_id ON funnel_sessions(order_id)"))
        await conn.execute(text("CREATE INDEX ix_funnel_sessions_first_seen_at ON funnel_sessions(first_seen_at)"))
        
        logger.info("✓ funnel_sessions table created")


async def ensure_conversions_table(conn: AsyncConnection) -> None:
    """Create conversions table if it doesn't exist."""
    try:
        await conn.execute(text("SELECT 1 FROM conversions LIMIT 1"))
        logger.info("✓ conversions table exists")
    except Exception:
        logger.info("Creating conversions table...")
        await conn.execute(text("""
            CREATE TABLE conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                session_id INTEGER,
                conversion_id VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255),
                customer_name VARCHAR(255),
                revenue INTEGER,
                currency VARCHAR(10) DEFAULT 'USD',
                product_name VARCHAR(500),
                attribution_method VARCHAR(100),
                attribution_confidence INTEGER,
                attribution_metadata TEXT,
                webhook_source VARCHAR(100),
                webhook_payload TEXT,
                converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attributed_at TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id),
                FOREIGN KEY (session_id) REFERENCES funnel_sessions(id)
            )
        """))
        
        # Create indexes
        await conn.execute(text("CREATE INDEX ix_conversions_analysis_id ON conversions(analysis_id)"))
        await conn.execute(text("CREATE INDEX ix_conversions_session_id ON conversions(session_id)"))
        await conn.execute(text("CREATE INDEX ix_conversions_conversion_id ON conversions(conversion_id)"))
        await conn.execute(text("CREATE INDEX ix_conversions_email ON conversions(email)"))
        await conn.execute(text("CREATE INDEX ix_conversions_converted_at ON conversions(converted_at)"))
        
        logger.info("✓ conversions table created")
