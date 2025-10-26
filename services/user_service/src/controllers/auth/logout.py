"""
User Logout API Endpoint
Path: cloud-native-order-processor/services/user-service/src/controllers/auth/logout.py
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from api_models.auth.logout import (
    LogoutRequest,
    LogoutResponse
)
from common.auth.security.audit_logger import AuditLogger
from common.shared.logging import BaseLogger, LogAction, LogField, LoggerName
from api_info_enum import ApiTags, ApiPaths
from .dependencies import get_current_user

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)
router = APIRouter(tags=[ApiTags.AUTHENTICATION.value])


@router.post(
    ApiPaths.LOGOUT.value,
    response_model=LogoutResponse
)

def logout_user(
    logout_data: LogoutRequest,
    current_user = Depends(get_current_user)
) -> LogoutResponse:
    """Logout user (stateless JWT approach)"""
    # Initialize security managers
    audit_logger = AuditLogger()

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Logout request for user: {current_user.email}")

        # For stateless JWT, logout is primarily client-side
        # The server just acknowledges the logout request
        # In production, you might want to implement token blacklisting

        logger.info(action=LogAction.REQUEST_END, message=f"User logged out successfully: {current_user.email}")

        # Audit log successful logout
        audit_logger.log_logout(current_user.username)

        return LogoutResponse()

    except Exception as e:
        logger.error(action=LogAction.ERROR, message=f"Logout failed for user: {str(e)}")

        # Audit log failed logout
        audit_logger.log_security_event(
            LogAction.SECURITY_EVENT,
            current_user.username,
            {LogField.ERROR: str(e)}
        )

        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
