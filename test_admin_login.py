#!/usr/bin/env python3
"""
Quick diagnostic script to test admin login locally.
Run from project root: python test_admin_login.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_admin_login():
    """Test if admin user exists and password verification works."""
    from backend.db.session import get_db_session
    from backend.models.database import User
    from backend.services.passwords import verify_password
    from sqlalchemy import select
    
    print("=" * 60)
    print("ADMIN LOGIN DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Get database session
    async for session in get_db_session():
        # Check if admin user exists
        email = "ryan@funnelanalyzerpro.com"
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"\n❌ PROBLEM: User '{email}' does NOT exist in database")
            print("\nAll users in database:")
            all_users_stmt = select(User)
            all_result = await session.execute(all_users_stmt)
            all_users = all_result.scalars().all()
            for u in all_users:
                print(f"  - {u.email} (role: {u.role}, has_password: {bool(u.password_hash)})")
            return False
        
        print(f"\n✅ User '{email}' found in database")
        print(f"   Role: {user.role}")
        print(f"   Has password hash: {bool(user.password_hash)}")
        
        if user.role != "admin":
            print(f"\n❌ PROBLEM: User role is '{user.role}', not 'admin'")
            return False
        
        print(f"\n✅ User role is 'admin'")
        
        if not user.password_hash:
            print(f"\n❌ PROBLEM: User has no password hash set")
            return False
        
        print(f"\n✅ User has password hash")
        print(f"   Hash (first 30 chars): {user.password_hash[:30]}...")
        
        # Test password verification
        test_password = "FiR43Tx2-"
        print(f"\n🔐 Testing password verification with: {test_password}")
        
        try:
            is_valid = verify_password(test_password, user.password_hash)
            if is_valid:
                print(f"✅ Password verification SUCCESSFUL")
            else:
                print(f"❌ Password verification FAILED - password does not match hash")
                return False
        except Exception as e:
            print(f"❌ Password verification threw exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL CHECKS PASSED - Admin login should work")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = asyncio.run(test_admin_login())
    sys.exit(0 if success else 1)
