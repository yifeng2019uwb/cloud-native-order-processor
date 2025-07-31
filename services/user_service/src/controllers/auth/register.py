"""
User Register API Endpoint
Path: services/user_service/src/controllers/auth/register.py
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models (same directory structure)
from api_models.auth.registration import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from api_models.shared.common import ErrorResponse

# Import common DAO models - simple imports
from common.entities.user import UserCreate, User

# Import dependencies and simplified exceptions
from .dependencies import get_user_dao
from exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserRegistrationException,
    UserValidationException,
    InternalServerException,
)
from controllers.token_utilis import create_access_token

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
async def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    user_dao = Depends(get_user_dao)
) -> RegistrationSuccessResponse:
    """Register a new user account with comprehensive validation and security"""
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

    try:
        # Check if username already exists
        existing_user_by_username = await user_dao.get_user_by_username(user_data.username)
        if existing_user_by_username:
            raise UserAlreadyExistsException(
                f"Username '{user_data.username}' already exists"
            )

        # Check if email already exists
        existing_user_by_email = await user_dao.get_user_by_email(user_data.email)
        if existing_user_by_email:
            raise UserAlreadyExistsException(
                f"Email '{user_data.email}' already exists"
            )

        # Transform API model to DAO model - proper field mapping
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,           # Will be hashed in DAO
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )

        # Create the user via DAO
        created_user = await user_dao.create_user(user_create)

        # Log successful registration
        logger.info(
            f"User registered successfully: {created_user.username}",
            extra={
                "user_id": created_user.user_id,
                "username": created_user.username,
                "email": created_user.email,
                "registration_timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        # Return success response (no token - user must login separately)
        return RegistrationSuccessResponse(
            message="User registered successfully. Please login to access your account."
        )

    except (UserAlreadyExistsException, UserValidationException):
        # Re-raise these exceptions as they should be handled by the exception mapper
        raise
    except Exception as e:
        # Log unexpected errors and convert to internal server exception
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise InternalServerException(f"Registration failed: {str(e)}")