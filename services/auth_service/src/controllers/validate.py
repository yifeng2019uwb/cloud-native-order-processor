"""
JWT Validation Controller
"""

import time
from typing import Union
from fastapi import APIRouter
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.security import TokenManager
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.shared.logging import BaseLogger, Loggers, LogActions, LogFields
from api_info_enum import ApiTags, ApiPaths
from constants import TokenValidationMessages, TokenErrorTypes, TokenTypes, TokenPayloadFields, RequestDefaults

router = APIRouter(tags=[ApiTags.INTERNAL.value])
logger = BaseLogger(Loggers.AUTH)

# API endpoint path constant
API_VALIDATE_PATH = "/validate"


def _determine_token_type(token_payload: dict) -> str:
    """Determine token type from JWT payload"""
    # Check for explicit token type claim
    token_type = token_payload.get(TokenPayloadFields.TOKEN_TYPE, '').lower()
    if token_type in [TokenTypes.ACCESS, TokenTypes.REFRESH]:
        return token_type

    # Check for JWT standard claims that might indicate token type
    if TokenPayloadFields.SCOPE in token_payload:
        return TokenTypes.ACCESS

    # Default to access token
    return TokenTypes.ACCESS


@router.post(API_VALIDATE_PATH, response_model=Union[ValidateTokenResponse, ValidateTokenErrorResponse])
def validate_jwt_token(request: ValidateTokenRequest):
    """Validate JWT token and extract user context"""
    request_id = request.request_id or f"{RequestDefaults.REQUEST_ID_PREFIX}{int(time.time() * 1000)}"

    try:
        logger.info(action=LogActions.REQUEST_START, message=TokenValidationMessages.VALIDATING_JWT, extra={LogFields.REQUEST_ID: request_id})

        # Validate token
        token_manager = TokenManager()
        user_context = token_manager.validate_token_comprehensive(request.token)

        logger.info(action=LogActions.AUTH_SUCCESS, message=TokenValidationMessages.TOKEN_VALID, user=user_context[TokenPayloadFields.USERNAME], extra={LogFields.REQUEST_ID: request_id})

        return ValidateTokenResponse(
            valid=True,
            user=user_context[TokenPayloadFields.USERNAME],
            expires_at=str(user_context.get(TokenPayloadFields.EXPIRATION, RequestDefaults.EMPTY_STRING)),
            created_at=str(user_context.get(TokenPayloadFields.ISSUED_AT, RequestDefaults.EMPTY_STRING)),
            metadata=user_context.get(TokenPayloadFields.METADATA, RequestDefaults.EMPTY_DICT),
            request_id=request_id
        )

    except CNOPAuthTokenExpiredException:
        logger.warning(action=LogActions.AUTH_FAILED, message=TokenValidationMessages.TOKEN_EXPIRED, extra={LogFields.REQUEST_ID: request_id})

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.TOKEN_EXPIRED,
            message=TokenValidationMessages.TOKEN_EXPIRED,
            request_id=request_id
        )

    except CNOPAuthTokenInvalidException as e:
        logger.warning(action=LogActions.AUTH_FAILED, message=TokenValidationMessages.TOKEN_INVALID, extra={LogFields.REQUEST_ID: request_id, LogFields.ERROR: str(e)})

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.TOKEN_INVALID,
            message=TokenValidationMessages.TOKEN_INVALID,
            request_id=request_id
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=TokenValidationMessages.VALIDATION_FAILED, extra={LogFields.REQUEST_ID: request_id, LogFields.ERROR: str(e)})

        return ValidateTokenErrorResponse(
            valid=False,
            error=TokenErrorTypes.VALIDATION_ERROR,
            message=TokenValidationMessages.VALIDATION_FAILED,
            request_id=request_id
        )