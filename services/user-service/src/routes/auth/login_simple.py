from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import sys
import os
import logging

# Add common package path for DAO access
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)

from .dependencies import get_user_dao
from .token_utils import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login_user(
    login_data: UserLoginRequest,
    user_dao=Depends(get_user_dao)
):
    try:
        logger.info(f"Login attempt for: {login_data.email}")
        
        # Authenticate user
        user = await user_dao.authenticate_user(login_data.email, login_data.password)
        if not user:
            logger.warning(f"Authentication failed for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.info(f"User authenticated successfully: {login_data.email}")
        
        # Create JWT token
        token_data = create_access_token(user.email, user.name)
        
        return {
            "message": "Login successful!",
            "status": "success",
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "expires_in": token_data["expires_in"],
            "user": {
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "created_at": user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {login_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/login/health")
async def login_health():
    return {"service": "login", "status": "healthy"}
