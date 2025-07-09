"""
User Registration API Endpoint
Path: /cloud-native-order-processor/services/user-service/src/routes/auth/register.py
"""
import sys
import os
# from typing import Union

# Add common package to path
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)


from fastapi import APIRouter, HTTPException, Depends, status, Request
import logging
from datetime import datetime

# Import models from common package
from models.user import UserCreate, UserResponse
from models.auth import TokenResponse

# Import database dependencies
from database.dao.user_dao import UserDAO
from .dependencies import get_user_dao

# Import exceptions (we'll create these)
# from exceptions.internal_exceptions import (
#     raise_user_exists,
#     raise_database_error,
#     raise_validation_error
# )

logger = logging.getLogger(__name__)

# Router for registration endpoint
router = APIRouter(tags=["registration"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User successfully registered",
            "model": UserResponse
        },
        409: {
            "description": "User already exists"
        },
        422: {
            "description": "Invalid input data"
        },
        503: {
            "description": "Service unavailable"
        }
    }
)
async def register_user(
    user_data: UserCreate,
    request: Request,
    user_dao: UserDAO = Depends(get_user_dao)
) -> UserResponse:
    """
    Register a new user account

    This endpoint creates a new user account with the provided information.
    All input data is validated according to business rules:

    - **Email**: Must be valid email format and unique
    - **Password**: 8-128 characters with complexity requirements
    - **Name**: 2-100 characters, letters/spaces/hyphens/apostrophes only
    - **Phone**: Optional, 10-20 characters if provided

    **Security Features:**
    - Password is hashed before storage
    - Input validation prevents malicious data
    - Rate limiting applied (handled by middleware)
    - No sensitive information in error messages

    **Returns:**
    - **201**: User successfully created with user information
    - **409**: User already exists (generic message for security)
    - **422**: Invalid input data
    - **503**: Database or service unavailable
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

        # Check if user already exists
        existing_user = await user_dao.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

        # Additional business validation (if needed)
        # await _validate_business_rules(user_data, request)

        # Create the user
        created_user = await user_dao.create_user(user_data)

        # Log successful registration
        logger.info(
            f"User registered successfully: {user_data.email}",
            extra={
                "email": user_data.email,
                "user_id": created_user.user_id if hasattr(created_user, 'user_id') else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Return success response with user data
        return UserResponse(
            email=created_user.email,
            name=created_user.name,
            phone=created_user.phone,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )

    except Exception as e:
        # All exceptions are handled by the secure exception handlers
        # This allows internal exceptions to be logged with full context
        # while clients receive only safe, standardized responses
        logger.error(
            f"Registration failed for {user_data.email}: {str(e)}",
            extra={
                "email": user_data.email,
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        raise


async def _validate_business_rules(user_data: UserRegistrationRequest, request: Request) -> None:
    """
    Additional business rule validation beyond Pydantic model validation

    Args:
        user_data: Validated user registration data
        request: FastAPI request object for context

    Raises:
        InternalValidationError: If business rules are violated
    """
    # Example: Check for suspicious patterns
    suspicious_patterns = [
        "test@test.com",
        "admin@",
        "root@",
        "noreply@",
        "no-reply@"
    ]

    if any(pattern in user_data.email.lower() for pattern in suspicious_patterns):
        logger.warning(
            f"Suspicious email pattern detected: {user_data.email}",
            extra={
                "email": user_data.email,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        # Continue with registration but flag for review
        # In production, you might want to require additional verification

    # Example: Validate phone number country code if provided
    if user_data.phone and user_data.phone.startswith('+'):
        # Extract country code and validate against allowed list
        # This is just an example - implement based on your requirements
        pass

    # Example: Check name for potential abuse (updated for first_name/last_name)
    blocked_names = ["admin", "root", "test", "null", "undefined"]
    if (any(blocked in user_data.first_name.lower() for blocked in blocked_names) or
        any(blocked in user_data.last_name.lower() for blocked in blocked_names)):
        raise_validation_error(
            field="name",
            value=f"{user_data.first_name} {user_data.last_name}",
            rule="blocked_name_validation",
            details=f"Name '{user_data.first_name} {user_data.last_name}' contains blocked terms"
        )

    logger.debug(f"Business rules validation passed for {user_data.email}")


# Health check specific to registration service
@router.get(
    "/register/health",
    response_model=dict,
    tags=["health"]
)
async def registration_health_check() -> dict:
    """
    Health check endpoint for registration service

    Returns basic service status and available endpoints.
    Used by load balancers and monitoring systems.
    """
    return {
        "service": "user-registration",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": [
            "POST /auth/register",
            "GET /auth/register/health"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }