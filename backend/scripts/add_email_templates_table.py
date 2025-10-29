"""
Database migration: Add email_templates table

Run with:
    python -m backend.scripts.add_email_templates_table
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from backend.db.session import engine


async def add_email_templates_table():
    """Add email_templates table to database."""
    
    async with engine.begin() as conn:
        # Check if table exists
        result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'email_templates'
                )
                """
            )
        )
        table_exists = result.scalar()
        
        if table_exists:
            print("✓ email_templates table already exists")
            return
        
        print("Creating email_templates table...")
        
        await conn.execute(
            text(
                """
                CREATE TABLE email_templates (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    subject VARCHAR(500) NOT NULL,
                    html_content TEXT NOT NULL,
                    text_content TEXT NOT NULL,
                    description TEXT,
                    is_custom INTEGER DEFAULT 1,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                
                CREATE INDEX ix_email_templates_name ON email_templates(name);
                """
            )
        )
        
        print("✓ email_templates table created successfully")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_email_templates_table())
