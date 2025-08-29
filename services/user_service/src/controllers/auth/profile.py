"""
User Profile API Endpoint
Path: services/user_service/src/controllers/auth/profile.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)
from api_models.shared.common import ErrorResponse
from common.data.database import get_user_dao
from common.data.entities.user import UserResponse
from common.exceptions.shared_exceptions import (
    CNOPEntityNotFoundException as CNOPUserNotFoundException,
    CNOPEntityAlreadyExistsException as CNOPUserAlreadyExistsException
)
from common.shared.logging import BaseLogger, Loggers, LogActions
from user_exceptions.exceptions import CNOPUserValidationException
from validation.business_validators import (
    validate_email_uniqueness,
    validate_age_requirements
)
from .dependencies import get_current_user

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["profile"])


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

def get_profile(
    current_user: UserResponse = Depends(get_current_user)
) -> UserProfileResponse:
    """Get current user profile (requires JWT token)"""
    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Profile accessed by user: {current_user.username}")

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
        logger.error(action=LogActions.ERROR, message=f"Failed to get profile for user {current_user.username}: {str(e)}")
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
def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    user_dao = Depends(get_user_dao)
) -> ProfileUpdateSuccessResponse:
    """
    Update current user profile (JWT-only approach)

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Profile update attempt by user: {current_user.username}")

        # Layer 2: Business validation only
        if profile_data.email and profile_data.email != current_user.email:
            # Pass current username to exclude from uniqueness check
            validate_email_uniqueness(profile_data.email, user_dao, exclude_username=current_user.username)
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
            raise CNOPUserNotFoundException(f"User '{current_user.username}' not found")

        logger.info(action=LogActions.REQUEST_END, message=f"Profile updated successfully for user: {current_user.username}")

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
    except (CNOPUserNotFoundException, HTTPException, CNOPUserValidationException, CNOPUserAlreadyExistsException):
        raise
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Profile update failed for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )