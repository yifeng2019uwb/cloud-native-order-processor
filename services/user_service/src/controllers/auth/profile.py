"""
User Profile API Endpoint
Path: services/user_service/src/controllers/auth/profile.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Union
import logging

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
from common.security import TokenManager

# Import exceptions
from common.exceptions.shared_exceptions import (
    EntityNotFoundException as UserNotFoundException,
    TokenExpiredException,
    EntityAlreadyExistsException as UserAlreadyExistsException,
    EntityValidationException as UserValidationException
)

# Import business validation functions only (Layer 2)
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
        # Initialize TokenManager
        token_manager = TokenManager()

        # Use centralized token verification
        username = token_manager.verify_access_token(credentials.credentials)

        if not username:
            raise TokenExpiredException("Token has expired")

        # Get user from database using username from token
        user = user_dao.get_user_by_username(username)
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
    "/profile",
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
    "/profile",
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
    """
    Update current user profile (JWT-only approach)

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    try:
        logger.info(f"Profile update attempt by user: {current_user.username}")

        # Layer 2: Business validation only
        if profile_data.email and profile_data.email != current_user.email:
            validate_email_uniqueness(profile_data.email, user_dao)
        if profile_data.date_of_birth:
            validate_age_requirements(profile_data.date_of_birth)

        updated_user = user_dao.update_user(
            username=current_user.username,
            email=profile_data.email,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
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
                marketing_emails_consent=current_user.marketing_emails_consent,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
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