"""
User Profile API Endpoint
Path: cloud-native-order-processor/services/user-service/src/routes/auth/profile.py
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union
import logging
from datetime import datetime, timezone
import sys
import os

# Simple path setup - Add common package to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src"))

# Import user-service API models
from models.profile_models import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)
from models.shared_models import ErrorResponse

# Import common DAO models
from models.user import User

# Import dependencies
from .dependencies import get_user_dao
from .token_utils import verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
router = APIRouter(tags=["profile"])

# Use FastAPI security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_dao = Depends(get_user_dao)
) -> User:
    """Extract and validate user from JWT token"""
    try:
        # Use existing token verification utility
        payload = verify_access_token(credentials.credentials)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Get user from database using email from token
        user = await user_dao.get_user_by_email(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "model": UserProfileResponse
        },
        401: {
            "description": "Authentication failed",
            "model": ErrorResponse
        }
    }
)
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> UserProfileResponse:
    """Get current user profile (requires JWT token)"""
    try:
        logger.info(f"Profile accessed by user: {current_user.username}")

        # Use proper response model with all fields from database
        return UserProfileResponse(
            username=current_user.username,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            phone=current_user.phone,
            date_of_birth=current_user.date_of_birth,
            marketing_emails_consent=current_user.marketing_emails_consent,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )

    except Exception as e:
        logger.error(f"Failed to get profile for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put(
    "/me",
    response_model=Union[ProfileUpdateSuccessResponse, ProfileUpdateErrorResponse],
    responses={
        200: {
            "description": "Profile updated successfully",
            "model": ProfileUpdateSuccessResponse
        },
        400: {
            "description": "Invalid update data",
            "model": ProfileUpdateErrorResponse
        },
        401: {
            "description": "Authentication failed",
            "model": ErrorResponse
        },
        409: {
            "description": "Email already in use",
            "model": ProfileUpdateErrorResponse
        }
    }
)
async def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_dao = Depends(get_user_dao)
) -> ProfileUpdateSuccessResponse:
    """Update current user profile (requires JWT token)"""
    try:
        logger.info(f"Profile update attempt by user: {current_user.username}")

        # ✅ Security check: Users can only update their own profile
        if profile_data.username != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )

        # ✅ Update user profile using DAO (username from request as identifier)
        updated_user = await user_dao.update_user(
            username=profile_data.username,  # ✅ From request (identifier)
            email=profile_data.email,
            name=f"{profile_data.first_name} {profile_data.last_name}" if profile_data.first_name and profile_data.last_name else None,
            phone=profile_data.phone
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"Profile updated successfully for user: {current_user.username}")

        # Return updated profile data from database
        return ProfileUpdateSuccessResponse(
            message="Profile updated successfully",
            user=UserProfileResponse(
                username=updated_user.username,
                email=updated_user.email,
                first_name=profile_data.first_name or current_user.first_name,
                last_name=profile_data.last_name or current_user.last_name,
                phone=updated_user.phone,
                date_of_birth=profile_data.date_of_birth or current_user.date_of_birth,
                marketing_emails_consent=profile_data.marketing_emails_consent if profile_data.marketing_emails_consent is not None else current_user.marketing_emails_consent,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
            )
        )

    except HTTPException:
        raise
    except ValueError as e:
        # Handle email already in use or other validation errors
        logger.warning(f"Profile update validation failed for {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile update failed for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.get("/me/health", status_code=status.HTTP_200_OK)
async def profile_health():
    """Health check for profile service"""
    return {
        "service": "user-profile",
        "status": "healthy",
        "endpoints": [
            "GET /auth/me",
            "PUT /auth/me",
            "GET /auth/me/health"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }