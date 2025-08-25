"""
User Register API Endpoint
Path: services/user_service/src/controllers/auth/register.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Union
import logging
from datetime import datetime, timezone
from decimal import Decimal

# Import user-service API models (same directory structure)
from api_models.auth.registration import (
    UserRegistrationRequest,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from api_models.shared.common import ErrorResponse

# Import common DAO models - simple imports
from common.entities.user import UserCreate, User, Balance, BalanceCreate

# Import dependencies and simplified exceptions
from common.database import get_user_dao, get_balance_dao
from common.exceptions.shared_exceptions import (
    UserNotFoundException,
    UserValidationException,
    InternalServerException
)
from user_exceptions import (
    UserAlreadyExistsException
)
from common.security import TokenManager

# Import business validation functions only (Layer 2)
from validation.business_validators import (
    validate_username_uniqueness,
    validate_email_uniqueness,
    validate_age_requirements
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["register"])


@router.post(
    "/register",
    response_model=Union[RegistrationSuccessResponse, RegistrationErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User successfully registered",
            "model": RegistrationSuccessResponse
        },
        409: {
            "description": "User already exists",
            "model": RegistrationErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse
        }
    }
)
def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    user_dao = Depends(get_user_dao),
    balance_dao = Depends(get_balance_dao)
) -> RegistrationSuccessResponse:
    """
    Register a new user account with comprehensive validation and security

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    # Log register attempt (without sensitive data)
    logger.info(
        f"Register attempt from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": user_data.username,
            "email": user_data.email,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    logger.warning(f"🔍 DEBUG: [REGISTER] Starting registration for user: {user_data.username}")
    logger.warning(f"🔍 DEBUG: [REGISTER] User data received: username={user_data.username}, email={user_data.email}")
    logger.warning(f"🔍 DEBUG: [REGISTER] user_dao type: {type(user_dao)}")
    logger.warning(f"🔍 DEBUG: [REGISTER] balance_dao type: {type(balance_dao)}")

    try:
        # Layer 2: Business validation only
        logger.warning(f"🔍 DEBUG: [REGISTER] About to call validate_username_uniqueness for: {user_data.username}")
        validate_username_uniqueness(user_data.username, user_dao)
        logger.warning(f"🔍 DEBUG: [REGISTER] validate_username_uniqueness completed successfully")

        logger.warning(f"🔍 DEBUG: [REGISTER] About to call validate_email_uniqueness for: {user_data.email}")
        validate_email_uniqueness(user_data.email, user_dao)
        logger.warning(f"🔍 DEBUG: [REGISTER] validate_email_uniqueness completed successfully")

        logger.warning(f"🔍 DEBUG: [REGISTER] About to call validate_age_requirements")
        validate_age_requirements(user_data.date_of_birth)
        logger.warning(f"🔍 DEBUG: [REGISTER] validate_age_requirements completed successfully")

        # Transform API model to DAO model - proper field mapping
        logger.warning(f"🔍 DEBUG: [REGISTER] About to create UserCreate object")
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,           # Will be hashed in DAO
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )
        logger.warning(f"🔍 DEBUG: [REGISTER] UserCreate object created successfully")

        # Create the user via DAO (sync operation)
        logger.warning(f"🔍 DEBUG: [REGISTER] About to call user_dao.create_user")
        created_user = user_dao.create_user(user_create)
        logger.warning(f"🔍 DEBUG: [REGISTER] user_dao.create_user completed successfully")

        # Create initial balance record with 0 balance (sync operation)
        logger.warning(f"🔍 DEBUG: [REGISTER] About to create BalanceCreate object")
        balance_create = BalanceCreate(
            username=created_user.username,
            initial_balance=Decimal('0.00')
        )
        logger.warning(f"🔍 DEBUG: [REGISTER] BalanceCreate object created successfully")

        logger.warning(f"🔍 DEBUG: [REGISTER] About to call balance_dao.create_balance")
        balance_dao.create_balance(balance_create)
        logger.warning(f"🔍 DEBUG: [REGISTER] balance_dao.create_balance completed successfully")

        # Log successful registration
        logger.info(f"User registered successfully: {user_data.username}")

        # Return simple success response - no user data
        return RegistrationSuccessResponse(
            message="User registered successfully"
        )

    except (UserAlreadyExistsException, UserValidationException):
        # Re-raise these exceptions as they should be handled by the exception mapper
        raise
    except Exception as e:
        # Log unexpected errors and convert to internal server exception
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise InternalServerException(f"Registration failed: {str(e)}")