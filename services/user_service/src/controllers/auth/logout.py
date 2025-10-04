"""
User Logout API Endpoint
Path: cloud-native-order-processor/services/user-service/src/controllers/auth/logout.py
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, status
from api_models.auth.logout import (
    LogoutRequest,
    LogoutSuccessResponse,
    LogoutErrorResponse
)
from api_models.shared.common import ErrorResponse
from common.auth.security import AuditLogger
from common.shared.logging import BaseLogger, Loggers, LogActions, LogFields
from common.shared.constants.api_responses import APIResponseDescriptions
from common.shared.constants.http_status import HTTPStatus
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from constants import MSG_SUCCESS_LOGOUT
from .dependencies import get_current_user

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=[ApiTags.AUTHENTICATION.value])


@router.post(
    ApiPaths.LOGOUT.value,
    response_model=Union[LogoutSuccessResponse, LogoutErrorResponse],
    responses={
        HTTPStatus.OK: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_LOGOUT,
            ApiResponseKeys.MODEL.value: LogoutSuccessResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
            ApiResponseKeys.MODEL.value: LogoutErrorResponse
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_VALIDATION,
            ApiResponseKeys.MODEL.value: ErrorResponse
        }
    }
)

def logout_user(
    logout_data: LogoutRequest,
    current_user = Depends(get_current_user)
) -> LogoutSuccessResponse:
    """Logout user (stateless JWT approach)"""
    # Initialize security managers
    audit_logger = AuditLogger()

    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Logout request for user: {current_user.email}")

        # For stateless JWT, logout is primarily client-side
        # The server just acknowledges the logout request
        # In production, you might want to implement token blacklisting

        logger.info(action=LogActions.REQUEST_END, message=f"User logged out successfully: {current_user.email}")

        # Audit log successful logout
        audit_logger.log_logout(current_user.username)

        return LogoutSuccessResponse(
            message="Logged out successfully",
            timestamp=datetime.now(timezone.utc)
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Logout failed for user: {str(e)}")

        # Audit log failed logout
        audit_logger.log_security_event(
            LogActions.SECURITY_EVENT,
            current_user.username,
            {LogFields.ERROR: str(e)}
        )

        return LogoutErrorResponse(
            success=False,
            error="LOGOUT_FAILED",
            message="Logout failed. Please try again.",
            timestamp=datetime.now(timezone.utc)
        )
