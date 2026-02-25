"""
JWT Validation Controller
"""

import time
from typing import Union
from fastapi import APIRouter
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.security.token_manager import TokenManager
from common.auth.security.jwt_constants import RequestDefaults, JwtFields, TokenTypes, TokenErrorTypes
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.shared.logging import BaseLogger, LoggerName, LogAction, LogField
from api_info_enum import ApiTags, ApiPaths
from constants import TokenValidationMessages

router = APIRouter(tags=[ApiTags.INTERNAL.value])
logger = BaseLogger(LoggerName.AUTH)

# API endpoint path constant
API_VALIDATE_PATH = "/validate"


def _determine_token_type(token_payload: dict) -> str:
    """Determine token type from JWT payload"""
    # Check for explicit token_type field (note: different from 'type' field)
    token_type = token_payload.get(JwtFields.TOKEN_TYPE, RequestDefaults.EMPTY_STRING).lower()
    if token_type in [TokenTypes.ACCESS, TokenTypes.REFRESH]:
        return token_type

    # Check for JWT standard claims that might indicate token type
    if TokenTypes.SCOPE in token_payload:
        return TokenTypes.ACCESS

    # Default to access token
    return TokenTypes.ACCESS


@router.post(API_VALIDATE_PATH, response_model=Union[ValidateTokenResponse, ValidateTokenErrorResponse])
def validate_jwt_token(request: ValidateTokenRequest):
    """Validate JWT token and extract user context"""
    request_id = request.request_id or f"{RequestDefaults.REQUEST_ID_PREFIX}{int(time.time() * 1000)}"

    try:
        # Validate token (internal per-request check; no success log to avoid flooding — login already logs auth_success)
        token_manager = TokenManager()
        user_context = token_manager.validate_token_comprehensive(request.token)

        return ValidateTokenResponse(
            valid=True,
            user=user_context.username,
            expires_at=str(user_context.expiration),
            created_at=str(user_context.issued_at),
            metadata=user_context.metadata,
            request_id=request_id
        )

    except CNOPAuthTokenExpiredException:
        logger.warning(action=LogAction.AUTH_FAILED, message=TokenValidationMessages.TOKEN_EXPIRED, extra=f'{{"{LogField.REQUEST_ID}": "{request_id}"}}')

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.TOKEN_EXPIRED,
            message=TokenValidationMessages.TOKEN_EXPIRED,
            request_id=request_id
        )

    except CNOPAuthTokenInvalidException as e:
        logger.warning(action=LogAction.AUTH_FAILED, message=TokenValidationMessages.TOKEN_INVALID, extra=f'{{"{LogField.REQUEST_ID}": "{request_id}", "{LogField.ERROR}": "{str(e)}"}}')

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.TOKEN_INVALID,
            message=TokenValidationMessages.TOKEN_INVALID,
            request_id=request_id
        )

    except Exception as e:
        logger.error(action=LogAction.ERROR, message=TokenValidationMessages.VALIDATION_FAILED, extra=f'{{"{LogField.REQUEST_ID}": "{request_id}", "{LogField.ERROR}": "{str(e)}"}}')

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.VALIDATION_ERROR,
            message=TokenValidationMessages.VALIDATION_FAILED,
            request_id=request_id
        )