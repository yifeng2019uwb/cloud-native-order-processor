from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import sys
import os
import logging

# Add common package path for DAO access
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)

from models.user import UserCreate
from .dependencies import get_user_dao

logger = logging.getLogger(__name__)
router = APIRouter(tags=["registration"])

class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

@router.post("/register")
async def register_user_simple(
    user_data: UserRegistrationRequest,
    user_dao=Depends(get_user_dao)
):
    try:
        logger.info(f"Registration attempt for: {user_data.email}")
        
        # Check if user already exists
        existing_user = await user_dao.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        
        # Create DAO model
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,  # Will be hashed in DAO
            name=f"{user_data.first_name} {user_data.last_name}",
            phone=None  # Optional for now
        )
        
        logger.info(f"Creating user in database: {user_data.email}")
        
        # Create user in database
        created_user = await user_dao.create_user(user_create)
        
        logger.info(f"User created successfully: {user_data.email}")
        
        return {
            "message": "User registered successfully!",
            "status": "success",
            "user": {
                "username": user_data.username,
                "email": created_user.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "created_at": created_user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/register/health")
async def registration_health():
    return {"service": "registration", "status": "healthy"}
