"""
JWT Validation Controller

Internal endpoint for JWT token validation.
"""

import time
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from typing import Union
from common.auth.security import TokenManager
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException

router = APIRouter(prefix="/internal/auth", tags=["internal"])
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=Union[ValidateTokenResponse, ValidateTokenErrorResponse])
def validate_jwt_token(request: ValidateTokenRequest):
    """
    Validate JWT token and extract user context.

    This endpoint is called internally by the Gateway to validate JWT tokens
    and extract user information for authentication purposes.
    """
    start_time = time.time()
    request_id = request.request_id or f"req-{int(start_time * 1000)}"

    try:
        logger.info("JWT token validation request received - request_id: %s, token_length: %d",
                   request_id, len(request.token))

        # Initialize token manager from common package
        token_manager = TokenManager()

        # Validate token and extract user context using common package
        user_context = token_manager.validate_token_comprehensive(request.token)

        # Calculate processing time
        duration_ms = int((time.time() - start_time) * 1000)

        # Log successful validation
        logger.info("JWT token validated successfully - request_id: %s, username: %s, role: %s, duration_ms: %d",
                   request_id, user_context["username"], user_context["role"], duration_ms)

        # Return success response
        return ValidateTokenResponse(
            valid=True,
            user=user_context["username"],
            expires_at=user_context["expires_at"],
            created_at=user_context["created_at"],
            metadata=user_context["metadata"],
            request_id=request_id
        )

    except CNOPAuthTokenExpiredException as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.warning("JWT token expired - request_id: %s, duration_ms: %d", request_id, duration_ms)

        # Return error response for expired token
        return ValidateTokenErrorResponse(
            valid=False,
            error="token_expired",
            message="JWT token has expired",
            request_id=request_id
        )

    except CNOPAuthTokenInvalidException as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.warning("JWT token invalid - request_id: %s, duration_ms: %d, error_message: %s",
                      request_id, duration_ms, str(e))

        # Return error response for invalid token
        return ValidateTokenErrorResponse(
            valid=False,
            error="token_invalid",
            message="JWT token is invalid",
            request_id=request_id
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.error("Unexpected error during token validation - request_id: %s, error: %s, error_type: %s, duration_ms: %d",
                    request_id, str(e), type(e).__name__, duration_ms)

        # Return generic error response
        return ValidateTokenErrorResponse(
            valid=False,
            error="validation_error",
            message="Token validation failed",
            request_id=request_id
        )
