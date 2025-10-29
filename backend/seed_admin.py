#!/usr/bin/env python3
"""
Seed admin user in production database.
Run this as a one-time job on Railway or locally to create the admin account.

Usage:
    python backend/seed_admin.py

Environment variables required:
    DATABASE_URL - PostgreSQL connection string
    DEFAULT_ADMIN_EMAIL - Admin email (default: ryan@funnelanalyzerpro.com)
    DEFAULT_ADMIN_PASSWORD - Admin password (default: FiR43Tx2-)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path so we can import backend module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.db.session import AsyncSessionFactory, engine
from backend.models.database import User, Base
from backend.services.passwords import hash_password
from backend.utils.config import settings

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_admin():
    """Create or update admin user in database."""
    
    # Get admin credentials from environment
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "ryan@funnelanalyzerpro.com")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "FiR43Tx2-")
    
    logger.info("=" * 70)
    logger.info("ADMIN USER SEEDING SCRIPT")
    logger.info("=" * 70)
    logger.info(f"Database URL: {settings.DATABASE_URL[:30]}...")
    logger.info(f"Admin Email: {admin_email}")
    logger.info(f"Admin Password: {'*' * len(admin_password)}")
    logger.info("=" * 70)
    
    try:
        # Create tables if they don't exist
        logger.info("Creating database tables if needed...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables ready")
        
        # Check if admin user exists
        async with AsyncSessionFactory() as session:
            stmt = select(User).where(User.email == admin_email)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info(f"ℹ️  Admin user '{admin_email}' already exists")
                logger.info(f"   Current role: {existing_user.role}")
                logger.info(f"   Has password: {bool(existing_user.password_hash)}")
                
                # Check if needs update
                if existing_user.role != "admin":
                    logger.warning(f"   ⚠️  User role is '{existing_user.role}', should be 'admin'")
                    logger.info("   To fix: Update user role to 'admin' in database manually")
                elif not existing_user.password_hash:
                    logger.warning(f"   ⚠️  User has no password hash")
                    logger.info("   To fix: Set password hash in database manually")
                else:
                    logger.info("✅ Admin user already configured correctly")
                    
            else:
                logger.info(f"Creating new admin user '{admin_email}'...")
                
                # Create new admin user
                password_hash = hash_password(admin_password)
                new_user = User(
                    email=admin_email,
                    role="admin",
                    password_hash=password_hash,
                    is_active=True,
                    email_verified=True,
                    plan="pro"  # Give admin pro plan
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                
                logger.info("✅ Admin user created successfully")
                logger.info(f"   User ID: {new_user.id}")
                logger.info(f"   Email: {new_user.email}")
                logger.info(f"   Role: {new_user.role}")
                logger.info(f"   Plan: {new_user.plan}")
        
        # Verify admin user can be queried
        logger.info("\nVerifying admin user...")
        async with AsyncSessionFactory() as session:
            stmt = select(User).where(User.email == admin_email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user and user.role == "admin" and user.password_hash:
                logger.info("✅ VERIFICATION PASSED")
                logger.info("=" * 70)
                logger.info("Admin account is ready!")
                logger.info(f"Email: {admin_email}")
                logger.info(f"Password: {admin_password}")
                logger.info("=" * 70)
                return True
            else:
                logger.error("❌ VERIFICATION FAILED - admin user not found or incomplete")
                return False
                
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(seed_admin())
    sys.exit(0 if success else 1)
