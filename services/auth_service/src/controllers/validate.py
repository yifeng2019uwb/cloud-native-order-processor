"""
JWT Validation Controller
"""

import time
from typing import Union
from fastapi import APIRouter
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.security import TokenManager
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.shared.logging import BaseLogger, Loggers, LogActions

router = APIRouter(prefix="/internal/auth", tags=["internal"])
logger = BaseLogger(Loggers.AUTH)


def _determine_token_type(token_payload: dict) -> str:
    """Determine token type from JWT payload"""
    # Check for explicit token type claim
    token_type = token_payload.get('token_type', '').lower()
    if token_type in ['access', 'refresh']:
        return token_type

    # Check for JWT standard claims that might indicate token type
    if 'scope' in token_payload:
        return 'access'

    # Default to access token
    return 'access'


@router.post("/validate", response_model=Union[ValidateTokenResponse, ValidateTokenErrorResponse])
def validate_jwt_token(request: ValidateTokenRequest):
    """Validate JWT token and extract user context"""
    request_id = request.request_id or f"req-{int(time.time() * 1000)}"

    try:
        logger.info(action=LogActions.REQUEST_START, message="Validating JWT", extra={"request_id": request_id})

        # Validate token
        token_manager = TokenManager()
        user_context = token_manager.validate_token_comprehensive(request.token)

        logger.info(action=LogActions.AUTH_SUCCESS, message="Token valid", user=user_context["username"], extra={"request_id": request_id})

        return ValidateTokenResponse(
            valid=True,
            user=user_context["username"],
            expires_at=str(user_context.get("exp", "")),
            created_at=str(user_context.get("iat", "")),
            metadata=user_context.get("metadata", {}),
            request_id=request_id
        )

    except CNOPAuthTokenExpiredException:
        logger.warning(action=LogActions.AUTH_FAILED, message="Token expired", extra={"request_id": request_id})

        return ValidateTokenErrorResponse(
            valid=False,
            error="token_expired",
            message="JWT token has expired",
            request_id=request_id
        )

    except CNOPAuthTokenInvalidException as e:
        logger.warning(action=LogActions.AUTH_FAILED, message="Token invalid", extra={"request_id": request_id, "error": str(e)})

        return ValidateTokenErrorResponse(
            valid=False,
            error="token_invalid",
            message="JWT token is invalid",
            request_id=request_id
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message="Validation error", extra={"request_id": request_id, "error": str(e)})

        return ValidateTokenErrorResponse(
            valid=False,
            error="validation_error",
            message="Token validation failed",
            request_id=request_id
        )