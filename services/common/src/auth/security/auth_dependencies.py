"""
Authentication Dependencies for Services

This module provides common authentication dependency functions that can be used
across all services for consistent JWT validation and user authentication.
"""

import time
from typing import Optional

from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

from ..gateway.header_validator import get_request_id_from_request
from .token_manager import TokenManager
from .jwt_constants import JwtFields, JWTConfig
from ...data.entities.user import DEFAULT_USER_ROLE
from ...shared.constants.api_constants import HTTPStatus, ErrorMessages, RequestHeaders
from ...shared.logging import BaseLogger, Loggers, LogActions


class AuthenticatedUser(BaseModel):
    """Authenticated user information from JWT token"""
    username: str = Field(..., description="User username")
    role: str = Field(..., description="User role")
    request_id: str = Field(..., description="Request ID for tracing")


def get_current_user(request: Request) -> AuthenticatedUser:
    """
    Get current user from JWT token validation

    Args:
        request: FastAPI Request object

    Returns:
        AuthenticatedUser object with validated user information

    Raises:
        HTTPException: If JWT token is invalid or missing
    """

    # Get Authorization header
    auth_header = request.headers.get(RequestHeaders.AUTHORIZATION)
    if not auth_header or not auth_header.startswith(f"{JWTConfig.TOKEN_TYPE_BEARER.title()} "):
        logger.warning(action=LogActions.ACCESS_DENIED, message="Missing or invalid Authorization header")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.AUTHENTICATION_FAILED
        )

    # Extract token
    token = auth_header.split(f"{JWTConfig.TOKEN_TYPE_BEARER.title()} ")[1]

    try:
        # Validate JWT token
        token_manager = TokenManager()
        user_context = token_manager.validate_token_comprehensive(token)

        # Extract request ID for tracing
        request_id = get_request_id_from_request(request)

        # Create authenticated user object
        authenticated_user = AuthenticatedUser(
            username=user_context[JwtFields.USERNAME],
            role=user_context.get(JwtFields.ROLE, DEFAULT_USER_ROLE),
            request_id=request_id
        )

        logger.info(action=LogActions.AUTH_SUCCESS, message=f"User authenticated via JWT: {authenticated_user.username}")
        return authenticated_user

    except Exception as e:
        logger.warning(action=LogActions.ACCESS_DENIED, message=f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.AUTHENTICATION_FAILED
        )


# Initialize logger for this module
logger = BaseLogger(Loggers.AUDIT)
