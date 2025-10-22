"""
Authentication service for JWT validation.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict

from ..utils.config import settings


async def validate_jwt_token(token: str) -> Dict:
    """
    Validate JWT token and extract user information.
    
    TODO: Integrate with WordPress REST API or shared JWT secret.
    For now, returns mock validation.
    """
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            return {
                "valid": False,
                "message": "Token expired"
            }
        
        # Extract user info
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "message": "Token is valid"
        }
        
    except jwt.InvalidTokenError:
        return {
            "valid": False,
            "message": "Invalid token"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }


async def create_jwt_token(user_id: int, email: str) -> str:
    """
    Create JWT token for testing purposes.
    
    In production, WordPress would generate these tokens.
    """
    
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token
