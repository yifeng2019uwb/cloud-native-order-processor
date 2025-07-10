"""
User Registration API Endpoint
Path: cloud-native-order-processor/services/user-service/src/routes/auth/register.py
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Union
import logging
from datetime import datetime, timezone
import sys
import os

# Simple path setup - Add common package to path
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src"))
# Add local src directory for user-service models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Add common package for shared models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src"))

# Import user-service API models (same directory structure)
from models.register_models import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from models.shared_models import ErrorResponse

# Import common DAO models - simple imports
from models.user import UserCreate, User

# Import dependencies and exceptions
from .dependencies import get_user_dao
from exceptions.internal_exceptions import (
    raise_user_exists,
    raise_database_error,
    raise_validation_error
)

logger = logging.getLogger(__name__)
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
    """Register a new user account with comprehensive validation and security"""
    try:
        # Log registration attempt (without sensitive data)
        logger.info(
            f"Registration attempt from {request.client.host if request.client else 'unknown'}",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        # Check if username already exists
        existing_user_by_username = await user_dao.get_user_by_username(user_data.username)
        if existing_user_by_username:
            raise_user_exists(f"username:{user_data.username}", existing_user_by_username.username)

        # Check if email already exists
        existing_user_by_email = await user_dao.get_user_by_email(user_data.email)
        if existing_user_by_email:
            raise_user_exists(f"email:{user_data.email}", existing_user_by_email.email)

        # Transform API model to DAO model - proper field mapping
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,           # Will be hashed in DAO
            name=f"{user_data.first_name} {user_data.last_name}",  # Combine for common model
            phone=user_data.phone
        )

        # Create the user via DAO
        try:
            created_user = await user_dao.create_user(user_create)
        except Exception as db_error:
            raise_database_error("user_creation", "users_table", db_error)

        # Log successful registration
        logger.info(
            f"User registered successfully: {user_data.username} ({user_data.email})",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        # Build response from created user data ONLY (what's actually stored)
        return RegistrationSuccessResponse(
            message="Account created successfully",
            user=UserRegistrationResponse(
                username=created_user.username,
                email=created_user.email,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                phone=created_user.phone,
                date_of_birth=created_user.date_of_birth,
                marketing_emails_consent=created_user.marketing_emails_consent,
                created_at=created_user.created_at,
                updated_at=created_user.updated_at
            )
        )

    except Exception as e:
        # All exceptions are handled by the secure exception handlers
        logger.error(
            f"Registration failed for {user_data.username} ({user_data.email}): {str(e)}",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "error_type": type(e).__name__,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        raise


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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }