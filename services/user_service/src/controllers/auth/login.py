"""
User Login API Endpoint
Path: services/user_service/src/controllers/auth/login.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status
from api_models.auth.login import (
    UserLoginRequest,
    LoginSuccessResponse,
    LoginErrorResponse,
    UserLoginResponse
)
from api_models.shared.common import ErrorResponse, UserBaseInfo
from common.data.entities.user import User
from common.data.database.dependencies import get_user_dao
from common.auth.security import TokenManager, AuditLogger
from common.exceptions.shared_exceptions import CNOPInvalidCredentialsException, CNOPUserNotFoundException, CNOPInternalServerException
from user_exceptions import CNOPUserValidationException
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
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
def login_user(
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
        logger.info(action=LogActions.REQUEST_START, message=f"Login attempt for: {login_data.username}")

        # Layer 2: Business validation only
        # Authenticate user using username
        user = user_dao.authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(action=LogActions.AUTH_FAILED, message=f"Authentication failed for: {login_data.username}")
            audit_logger.log_login_failure(login_data.username, "Invalid credentials", client_ip, user_agent)
            raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{login_data.username}'")

        logger.info(action=LogActions.AUTH_SUCCESS, message=f"User authenticated successfully: {login_data.username}")

        # Create JWT token using centralized TokenManager
        token_data = token_manager.create_access_token(user.username, user.role)

        # Log successful login and token creation
        audit_logger.log_login_success(user.username, client_ip, user_agent)
        audit_logger.log_token_created(user.username, "access_token", client_ip)

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

    except CNOPInvalidCredentialsException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except CNOPUserNotFoundException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except CNOPUserValidationException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except Exception as e:
        # Log unexpected errors and re-raise as internal server error
        logger.error(action=LogActions.ERROR, message=f"Unexpected error during login: {e}")
        raise CNOPInternalServerException(f"Internal server error during login: {e}")