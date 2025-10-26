"""
User Profile API Endpoint
Path: services/user_service/src/controllers/auth/profile.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileResponse
)
from common.data.database.dependencies import get_user_dao
from common.data.entities.user import User
from common.exceptions.shared_exceptions import (
    CNOPEntityNotFoundException as CNOPUserNotFoundException
)
from common.shared.logging import BaseLogger, LogAction, LoggerName
from common.shared.constants.api_constants import ErrorMessages
from api_info_enum import ApiTags, ApiPaths
from user_exceptions.exceptions import CNOPUserAlreadyExistsException, CNOPUserValidationException
from validation.business_validators import (
    validate_email_uniqueness,
    validate_age_requirements
)
from .dependencies import get_current_user
from common.auth.gateway.header_validator import get_request_id_from_request

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)
router = APIRouter(tags=[ApiTags.AUTHENTICATION.value])


@router.get(
    ApiPaths.PROFILE.value,
    response_model=UserProfileResponse
)

def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> UserProfileResponse:
    """Get current user profile (requires JWT token)"""
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Profile accessed by user: {current_user.username}", request_id=request_id)

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
        logger.error(action=LogAction.ERROR, message=f"Failed to get profile for user {current_user.username}: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.INTERNAL_SERVER_ERROR
        )


@router.put(
    ApiPaths.PROFILE.value,
    response_model=ProfileResponse
)
def update_profile(
    profile_data: UserProfileUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    user_dao = Depends(get_user_dao)
) -> ProfileResponse:
    """
    Update current user profile (JWT-only approach)

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Profile update attempt by user: {current_user.username}", request_id=request_id)

        # Layer 2: Business validation only
        if profile_data.email and profile_data.email != current_user.email:
            # Pass current username to exclude from uniqueness check
            validate_email_uniqueness(profile_data.email, user_dao, exclude_username=current_user.username)
        if profile_data.date_of_birth:
            validate_age_requirements(profile_data.date_of_birth)

        # Create updated User object directly
        updated_user = user_dao.update_user(User(
            username=current_user.username,
            email=profile_data.email or current_user.email,
            password=current_user.password,  # Keep existing password
            first_name=profile_data.first_name or current_user.first_name,
            last_name=profile_data.last_name or current_user.last_name,
            phone=profile_data.phone or current_user.phone,
            date_of_birth=profile_data.date_of_birth or current_user.date_of_birth,
            marketing_emails_consent=current_user.marketing_emails_consent,
            role=current_user.role,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        ))

        if not updated_user:
            raise CNOPUserNotFoundException(f"{ErrorMessages.USER_NOT_FOUND}: {current_user.username}")

        logger.info(action=LogAction.REQUEST_END, message=f"Profile updated successfully for user: {current_user.username}", request_id=request_id)

        return ProfileResponse(
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
        logger.error(action=LogAction.ERROR, message=f"Profile update failed for user {current_user.username}: {str(e)}", request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.INTERNAL_SERVER_ERROR
        )