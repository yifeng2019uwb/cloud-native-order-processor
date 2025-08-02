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
from controllers.token_utilis import create_access_token

# Import exceptions
from user_exceptions import InvalidCredentialsException

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
    try:
        logger.info(f"Login attempt for: {login_data.username}")

        # Layer 2: Business validation only
        # Authenticate user using username
        user = user_dao.authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(f"Authentication failed for: {login_data.username}")
            raise InvalidCredentialsException(f"Invalid credentials for user '{login_data.username}'")

        logger.info(f"User authenticated successfully: {login_data.username}")

        # Create JWT token using username and role
        token_data = create_access_token(user.username, user.role)

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
        raise
    except Exception as e:
        logger.error(f"Login failed for {login_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )