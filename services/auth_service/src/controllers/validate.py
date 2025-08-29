"""
JWT Validation Controller

Internal endpoint for JWT token validation.
"""

import time
from typing import Union
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.security import TokenManager
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.shared.logging import BaseLogger, Loggers, LogActions

router = APIRouter(prefix="/internal/auth", tags=["internal"])
logger = BaseLogger(Loggers.AUTH)


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
        logger.info(action=LogActions.REQUEST_START, message="JWT token validation request received",
                   extra={"request_id": request_id, "token_length": len(request.token)})

        # Initialize token manager from common package
        token_manager = TokenManager()

        # Validate token and extract user context using common package
        user_context = token_manager.validate_token_comprehensive(request.token)

        # Calculate processing time
        duration_ms = int((time.time() - start_time) * 1000)

        # Log successful validation
        logger.info(action=LogActions.AUTH_SUCCESS, message="JWT token validated successfully",
                   user=user_context["username"], duration_ms=duration_ms,
                   extra={"request_id": request_id, "role": user_context.get("role", "unknown")})

        # Return success response
        return ValidateTokenResponse(
            valid=True,
            user=user_context["username"],
            expires_at=str(user_context.get("exp", "")),
            created_at=str(user_context.get("iat", "")),
            metadata={"token_type": user_context.get("token_type", "")},
            request_id=request_id
        )

    except CNOPAuthTokenExpiredException as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.warning(action=LogActions.AUTH_FAILED, message="JWT token expired",
                      duration_ms=duration_ms, extra={"request_id": request_id})

        # Return error response for expired token
        return ValidateTokenErrorResponse(
            valid=False,
            error="token_expired",
            message="JWT token has expired",
            request_id=request_id
        )

    except CNOPAuthTokenInvalidException as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.warning(action=LogActions.AUTH_FAILED, message="JWT token invalid",
                      duration_ms=duration_ms, extra={"request_id": request_id, "error_message": str(e)})

        # Return error response for invalid token
        return ValidateTokenErrorResponse(
            valid=False,
            error="token_invalid",
            message="JWT token is invalid",
            request_id=request_id
        )

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.error(action=LogActions.ERROR, message="Unexpected error during token validation",
                    duration_ms=duration_ms, extra={"request_id": request_id, "error": str(e), "error_type": type(e).__name__})

        # Return generic error response
        return ValidateTokenErrorResponse(
            valid=False,
            error="validation_error",
            message="Token validation failed",
            request_id=request_id
        )
