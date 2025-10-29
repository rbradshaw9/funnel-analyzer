#!/usr/bin/env python3
"""
Admin initialization script.
Creates or updates an admin user account.

Usage:
    python init_admin.py
    python init_admin.py --email admin@example.com --password mypassword
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir.parent))

from datetime import datetime, timezone
from backend.db.session import AsyncSessionFactory
from backend.models.database import User
from backend.services.passwords import hash_password
from sqlalchemy import select


async def create_or_update_admin(email: str, password: str, full_name: str = "Admin User"):
    """Create or update an admin user."""
    
    async with AsyncSessionFactory() as session:
        try:
            # Check if user exists
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✓ User {email} already exists")
                
                # Update to admin if not already
                updated = False
                if user.role != "admin":
                    user.role = "admin"
                    updated = True
                    print(f"  → Updated role to admin")
                
                # Update password
                user.password_hash = hash_password(password)
                updated = True
                print(f"  → Updated password")
                
                # Ensure active status
                if user.status != "active":
                    user.status = "active"
                    updated = True
                    print(f"  → Updated status to active")
                
                if user.plan == "free":
                    user.plan = "pro"
                    updated = True
                    print(f"  → Updated plan to pro")
                
                if full_name and not user.full_name:
                    user.full_name = full_name
                    updated = True
                
                user.updated_at = datetime.now(timezone.utc)
                
                if updated:
                    await session.commit()
                    print(f"✓ Admin user {email} updated successfully")
                else:
                    print(f"✓ Admin user {email} already configured correctly")
            else:
                # Create new admin user
                user = User(
                    email=email,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    role="admin",
                    status="active",
                    plan="pro",
                    is_active=1,
                    onboarding_completed=1,
                )
                session.add(user)
                await session.commit()
                print(f"✓ Created new admin user: {email}")
            
            print(f"\n✓ Admin Setup Complete!")
            print(f"  Email: {email}")
            print(f"  Role: {user.role}")
            print(f"  Plan: {user.plan}")
            print(f"  Status: {user.status}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            await session.rollback()
            raise


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize admin user")
    parser.add_argument("--email", default="ryan@funnelanalyzerpro.com", help="Admin email address")
    parser.add_argument("--password", default="FiR43Tx2-", help="Admin password")
    parser.add_argument("--name", default="Ryan Bradshaw", help="Admin full name")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Admin User Initialization")
    print("=" * 60)
    print(f"Email: {args.email}")
    print(f"Name: {args.name}")
    print("=" * 60)
    print()
    
    await create_or_update_admin(args.email, args.password, args.name)
    
    print()
    print("=" * 60)
    print("You can now login at:")
    print("  https://funnelanalyzerpro.com/admin")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
