from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
import sys
import os
import logging
from typing import Optional

# Add common package path
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)

from .dependencies import get_user_dao
from .token_utils import verify_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["profile"])

class UserProfile(BaseModel):
    email: str
    name: str
    phone: Optional[str]
    created_at: str

async def get_current_user(authorization: str = Header(None), user_dao=Depends(get_user_dao)):
    """Extract user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    user = await user_dao.get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.get("/me")
async def get_profile(current_user=Depends(get_current_user)):
    """Get current user profile (requires JWT token)"""
    return {
        "message": "Profile retrieved successfully!",
        "status": "success",
        "user": {
            "email": current_user.email,
            "name": current_user.name,
            "phone": current_user.phone,
            "created_at": current_user.created_at.isoformat()
        }
    }

@router.get("/me/health")
async def profile_health():
    return {"service": "profile", "status": "healthy"}
