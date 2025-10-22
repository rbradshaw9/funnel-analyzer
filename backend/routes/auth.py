"""
Authentication route - JWT validation for WordPress integration.
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import AuthValidateRequest, AuthValidateResponse
from ..services.auth import validate_jwt_token
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=AuthValidateResponse)
async def validate_token(request: AuthValidateRequest):
    """
    Validate JWT token from WordPress or manual login.
    
    This endpoint verifies the token signature and extracts user information.
    Token should be passed from WordPress membership site.
    """
    try:
        logger.info("Validating JWT token")
        
        # Validate token and extract user info
        result = await validate_jwt_token(request.token)
        
        if result["valid"]:
            logger.info(f"Token validated for user: {result.get('email', 'unknown')}")
        else:
            logger.warning("Invalid token received")
        
        return result
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
