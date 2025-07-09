"""
Pydantic models package for user authentication service
Path: cloud-native-order-processor/services/user-service/src/models/__init__.py
"""

# Import shared models for easy access
from .shared_models import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
    TokenResponse,
    UserBaseInfo
)

# Import registration models
from .register_models import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)

__all__ = [
    # Shared models
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "TokenResponse",
    "UserBaseInfo",

    # Registration models
    "UserRegistrationRequest",
    "UserRegistrationResponse",
    "RegistrationSuccessResponse",
    "RegistrationErrorResponse"

    # Login models
    "UserLoginRequest",
    "LoginSuccessResponse",
    "LoginErrorResponse",

    # Logout models
    "LogoutRequest",
    "LogoutSuccessResponse",
    "LogoutErrorResponse",

    "UserProfileResponse",
    "UserProfileUpdateRequest",
    "ProfileUpdateSuccessResponse",
    "ProfileUpdateErrorResponse"

]