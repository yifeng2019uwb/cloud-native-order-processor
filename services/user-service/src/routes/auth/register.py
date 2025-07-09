from fastapi import APIRouter, HTTPException, Depends, status, Request
import logging
from datetime import datetime
"""
User Registration API Endpoint
Path: cloud-native-order-processor/services/user-service/src/routes/auth/register.py
"""
import sys
import os
from typing import Union
import importlib.util

# Calculate paths
user_service_path = os.path.dirname(__file__)  # routes/auth/
models_path = os.path.join(user_service_path, "..", "..")  # back to src/
common_path = os.path.join(user_service_path, "..", "..", "..", "..", "common", "src")

# Add user-service models path for API models
sys.path.insert(0, models_path)

# Import API layer models (from user-service)
from models.register_models import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from models.shared_models import ErrorResponse

# Remove user-service path to avoid conflicts
sys.path.remove(models_path)

# Add common path for DAO models
sys.path.insert(0, common_path)

# Import DAO layer models using direct file loading to avoid conflicts
spec = importlib.util.spec_from_file_location(
    "common_user_models",
    os.path.join(common_path, "models", "user.py")
)
common_user_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_user_models)

# Extract the classes we need from common package
UserCreate = common_user_models.UserCreate
User = common_user_models.User

# Import database dependencies
from .dependencies import get_user_dao

# Import exceptions
from exceptions.internal_exceptions import (
    raise_user_exists,
    raise_database_error,
    raise_validation_error
)

logger = logging.getLogger(__name__)

# Router for registration endpoints
router = APIRouter(tags=["registration"])


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
    """
    Register a new user account with comprehensive validation and security
    """
    try:
        # Log registration attempt (without sensitive data)
        logger.info(
            f"Registration attempt from {request.client.host if request.client else 'unknown'}",
            extra={
                "email": user_data.email,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Check if user already exists by email
        existing_user_by_email = await user_dao.get_user_by_email(user_data.email)
        if existing_user_by_email:
            raise_user_exists(user_data.email, existing_user_by_email.email)

        # Transform API model to DAO model
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,  # Will be hashed in DAO
            name=f"{user_data.first_name} {user_data.last_name}",  # Combine names for common model
            phone=user_data.phone
        )

        # Create the user via DAO
        try:
            created_user = await user_dao.create_user(user_create)
        except Exception as db_error:
            raise_database_error("user_creation", "users_table", db_error)

        # Log successful registration
        logger.info(
            f"User registered successfully: {user_data.email}",
            extra={
                "email": user_data.email,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Transform DAO response back to API response model
        return RegistrationSuccessResponse(
            message="Account created successfully",
            user=UserRegistrationResponse(
                username=user_data.username,  # From original request
                email=created_user.email,
                first_name=user_data.first_name,  # From original request
                last_name=user_data.last_name,   # From original request
                phone=created_user.phone,
                date_of_birth=user_data.date_of_birth,  # From original request
                marketing_emails_consent=user_data.marketing_emails_consent,  # From original request
                created_at=created_user.created_at,
                updated_at=created_user.updated_at
            )
        )

    except Exception as e:
        # All exceptions are handled by the secure exception handlers
        logger.error(
            f"Registration failed for {user_data.email}: {str(e)}",
            extra={
                "email": user_data.email,
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        raise


# Health check specific to registration service
@router.get("/register/health", status_code=status.HTTP_200_OK)
async def registration_health_check():
    """Health check for registration service"""
    return {
        "service": "user-registration",
        "status": "healthy",
        "endpoints": [
            "POST /auth/register",
            "GET /auth/register/health"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }