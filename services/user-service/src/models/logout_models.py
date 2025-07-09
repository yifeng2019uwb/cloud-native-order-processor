"""
Pydantic models specific to user logout API (Simple JWT stateless approach)
Path: cloud-native-order-processor/services/user-service/src/models/logout_models.py
"""
from pydantic import BaseModel, Field
from .shared_models import SuccessResponse, ErrorResponse


class LogoutRequest(BaseModel):
    """Request model for POST /auth/logout - Empty for JWT stateless approach"""

    # JWT is stateless, so no data needed
    # Token comes from Authorization header

    class Config:
        json_schema_extra = {
            "example": {}
        }


class LogoutSuccessResponse(SuccessResponse):
    """Success response for logout"""

    message: str = Field(
        default="Logged out successfully",
        description="Logout success message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Logged out successfully",
                "data": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }


class LogoutErrorResponse(ErrorResponse):
    """Error response for logout failures (rare with JWT)"""

    error: str = Field(
        default="LOGOUT_FAILED",
        description="Logout error code"
    )

    message: str = Field(
        default="Logout failed. Please try again.",
        description="Generic logout error message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "LOGOUT_FAILED",
                "message": "Logout failed. Please try again.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }