"""
User Logout API Endpoint
Path: cloud-native-order-processor/services/user-service/src/controllers/auth/logout.py
"""
from fastapi import APIRouter, Depends, status
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.auth.logout import (
    LogoutRequest,
    LogoutSuccessResponse,
    LogoutErrorResponse
)
from api_models.shared.common import ErrorResponse

# Import dependencies
from .dependencies import get_current_user

logger = logging.getLogger(__name__)
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
async def logout_user(
    logout_data: LogoutRequest,
    current_user = Depends(get_current_user)
) -> LogoutSuccessResponse:
    """Logout user (stateless JWT approach)"""
    try:
        logger.info(f"Logout request for user: {current_user.email}")

        # For stateless JWT, logout is primarily client-side
        # The server just acknowledges the logout request
        # In production, you might want to implement token blacklisting

        logger.info(f"User logged out successfully: {current_user.email}")

        return LogoutSuccessResponse(
            message="Logged out successfully",
            timestamp=datetime.now(timezone.utc)
        )

    except Exception as e:
        logger.error(f"Logout failed for user: {str(e)}", exc_info=True)
        raise LogoutErrorResponse(
            success=False,
            error="LOGOUT_FAILED",
            message="Logout failed. Please try again.",
            timestamp=datetime.now(timezone.utc)
        )


@router.get("/logout/health", status_code=status.HTTP_200_OK)
async def logout_health():
    """Health check for logout service"""
    return {
        "service": "user-logout",
        "status": "healthy",
        "endpoints": [
            "POST /auth/logout",
            "GET /auth/logout/health"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/logout/debug", status_code=status.HTTP_200_OK)
async def logout_debug(
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
