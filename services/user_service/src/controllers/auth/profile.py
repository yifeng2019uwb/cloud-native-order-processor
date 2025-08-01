"""
User Profile API Endpoint
Path: cloud-native-order-processor/services/user-service/src/routes/auth/profile.py
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)
from api_models.shared.common import ErrorResponse

# Import common DAO models
from common.entities.user import User

# Import dependencies
from common.database import get_user_dao
from controllers.token_utilis import verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import exceptions
from exceptions import UserNotFoundException, TokenExpiredException, UserAlreadyExistsException
from common.exceptions.shared_exceptions import UserValidationException

# Import validation functions
from validation.field_validators import (
    validate_name,
    validate_email,
    validate_phone,
    validate_date_of_birth
)
from validation.business_validators import (
    validate_email_uniqueness,
    validate_age_requirements
)

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
        username = verify_access_token(credentials.credentials)

        if not username:
            raise TokenExpiredException("Token has expired")

        # Get user from database using username from token
        user = await user_dao.get_user_by_username(username)
        if not user:
            raise UserNotFoundException(f"User '{username}' not found")

        return user

    except (TokenExpiredException, UserNotFoundException):
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

        return UserProfileResponse(
            username=current_user.username,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            phone=current_user.phone,
            date_of_birth=current_user.date_of_birth,
            marketing_emails_consent=current_user.marketing_emails_consent
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
    """Update current user profile (JWT-only approach)"""
    try:
        logger.info(f"Profile update attempt by user: {current_user.username}")

        # Field validation - validate format and sanitize input
        if profile_data.first_name:
            validate_name(profile_data.first_name)
        if profile_data.last_name:
            validate_name(profile_data.last_name)
        if profile_data.email:
            validate_email(profile_data.email)
        if profile_data.phone:
            validate_phone(profile_data.phone)
        if profile_data.date_of_birth:
            validate_date_of_birth(profile_data.date_of_birth)

        # Business validation - check business rules
        if profile_data.email and profile_data.email != current_user.email:
            await validate_email_uniqueness(profile_data.email, user_dao)
        if profile_data.date_of_birth:
            validate_age_requirements(profile_data.date_of_birth)

        updated_user = await user_dao.update_user(
            username=current_user.username,
            email=profile_data.email,
            name=f"{profile_data.first_name} {profile_data.last_name}" if profile_data.first_name and profile_data.last_name else None,
            phone=profile_data.phone
        )

        if not updated_user:
            raise UserNotFoundException(f"User '{current_user.username}' not found")

        logger.info(f"Profile updated successfully for user: {current_user.username}")

        return ProfileUpdateSuccessResponse(
            message="Profile updated successfully",
            user=UserProfileResponse(
                username=updated_user.username,
                email=updated_user.email,
                first_name=profile_data.first_name or current_user.first_name,
                last_name=profile_data.last_name or current_user.last_name,
                phone=updated_user.phone,
                date_of_birth=profile_data.date_of_birth or current_user.date_of_birth,
                marketing_emails_consent=profile_data.marketing_emails_consent if profile_data.marketing_emails_consent is not None else current_user.marketing_emails_consent
            )
        )

    except (UserNotFoundException, TokenExpiredException, HTTPException, UserValidationException, UserAlreadyExistsException):
        raise
    except Exception as e:
        logger.error(f"Profile update failed for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )