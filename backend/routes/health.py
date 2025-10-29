"""
Health check and diagnostic endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.session import get_db_session
from ..models.database import User

router = APIRouter(prefix="/health", tags=["health"])


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
