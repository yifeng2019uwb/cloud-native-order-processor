"""
User Login API Endpoint
Path: services/user_service/src/controllers/auth/login.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.auth.login import (
    UserLoginRequest,
    LoginSuccessResponse,
    LoginErrorResponse
)
from api_models.shared.common import ErrorResponse
from api_models.shared.common import UserBaseInfo

# Import common DAO models
from common.entities.user import User

# Import dependencies
from common.database import get_user_dao
from common.security import TokenManager, AuditLogger

# Import exceptions
from common.exceptions.shared_exceptions import InvalidCredentialsException, UserNotFoundException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


@router.post(
    "/login",
    response_model=Union[LoginSuccessResponse, LoginErrorResponse],
    responses={
        200: {
            "description": "Login successful",
            "model": LoginSuccessResponse
        },
        401: {
            "description": "Authentication failed",
            "model": LoginErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        }
    }
)
async def login_user(
    login_data: UserLoginRequest,
    user_dao=Depends(get_user_dao)
) -> LoginSuccessResponse:
    """
    Authenticate user with username and password

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (authentication, etc.)
    """
    # Initialize security managers
    token_manager = TokenManager()
    audit_logger = AuditLogger()

    # Get client IP for audit logging (optional for now)
    client_ip = None
    user_agent = None

    try:
        logger.info(f"Login attempt for: {login_data.username}")

        # Layer 2: Business validation only
        # Authenticate user using username
        user = user_dao.authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(f"Authentication failed for: {login_data.username}")
            audit_logger.log_login_failure(login_data.username, "Invalid credentials", client_ip, user_agent)
            raise InvalidCredentialsException(f"Invalid credentials for user '{login_data.username}'")

        logger.info(f"User authenticated successfully: {login_data.username}")

        # Create JWT token using centralized TokenManager
        token_data = token_manager.create_access_token(user.username, user.role)

        # Log successful login and token creation
        audit_logger.log_login_success(user.username, client_ip, user_agent)
        audit_logger.log_token_created(user.username, "access_token", client_ip)

        # Create UserLoginResponse with only token data
        from api_models.auth.login import UserLoginResponse

        login_response = UserLoginResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"]
        )

        # Wrap in LoginSuccessResponse
        return LoginSuccessResponse(
            message="Login successful",
            data=login_response
        )

    except InvalidCredentialsException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except UserNotFoundException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise