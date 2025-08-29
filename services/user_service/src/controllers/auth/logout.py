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
from common.shared.logging import BaseLogger, Loggers, LogActions
from .dependencies import get_current_user

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["authentication"])


@router.post(
    "/logout",
    response_model=Union[LogoutSuccessResponse, LogoutErrorResponse],
    responses={
        200: {
            "description": "Logout successful",
            "model": LogoutSuccessResponse
        },
        401: {
            "description": "Unauthorized",
            "model": LogoutErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
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
            {"error": str(e)}
        )

        return LogoutErrorResponse(
            success=False,
            error="LOGOUT_FAILED",
            message="Logout failed. Please try again.",
            timestamp=datetime.now(timezone.utc)
        )


@router.get("/logout/debug", status_code=status.HTTP_200_OK)
def logout_debug(
    current_user = Depends(get_current_user)
):
    """Debug endpoint to test token verification and user lookup"""
    return {
        "message": "Debug endpoint working!",
        "user_found": True,
        "user_email": current_user.email,
        "user_name": current_user.name,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
