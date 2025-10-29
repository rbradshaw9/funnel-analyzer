"""
Health check and diagnostic endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from ..db.session import get_db_session
from ..models.database import User
from ..services.passwords import verify_password

router = APIRouter(prefix="/health", tags=["health"])


class PasswordTestRequest(BaseModel):
    email: str
    password: str


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "Funnel Analyzer Pro API"
    }


@router.get("/db")
async def database_health(session: AsyncSession = Depends(get_db_session)):
    """Check database connection and admin user status."""
    try:
        # Try to query the database
        stmt = select(User).where(User.email == "ryan@funnelanalyzerpro.com")
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        # Count total users
        count_stmt = select(User)
        count_result = await session.execute(count_stmt)
        all_users = count_result.scalars().all()
        
        return {
            "status": "healthy",
            "database": "connected",
            "admin_user_exists": admin_user is not None,
            "admin_user_details": {
                "email": admin_user.email if admin_user else None,
                "role": admin_user.role if admin_user else None,
                "has_password": bool(admin_user.password_hash) if admin_user else False,
                "is_active": bool(admin_user.is_active) if admin_user else False,
                "status": admin_user.status if admin_user else None,
            } if admin_user else None,
            "total_users": len(all_users),
            "user_emails": [u.email for u in all_users[:10]]  # First 10 only
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


@router.post("/test-password")
async def test_password_verification(
    request: PasswordTestRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Test password verification for debugging (REMOVE IN PRODUCTION)."""
    try:
        # Normalize email
        email = request.email.strip().lower()
        
        # Find user
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "success": False,
                "error": "User not found",
                "email": email
            }
        
        # Test password verification
        try:
            password_valid = verify_password(request.password, user.password_hash)
            return {
                "success": True,
                "email": user.email,
                "role": user.role,
                "has_password_hash": bool(user.password_hash),
                "password_hash_length": len(user.password_hash) if user.password_hash else 0,
                "password_valid": password_valid,
                "verification_method": "bcrypt"
            }
        except Exception as verify_error:
            return {
                "success": False,
                "error": f"Password verification failed: {str(verify_error)}",
                "email": user.email,
                "has_password_hash": bool(user.password_hash),
                "password_hash_length": len(user.password_hash) if user.password_hash else 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
