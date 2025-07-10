"""
Pydantic models package for user authentication service
Path: cloud-native-order-processor/services/user-service/src/models/__init__.py
"""

# Import shared models
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

# Import login models
from .login_models import (
    UserLoginRequest,
    LoginSuccessResponse,
    LoginErrorResponse
)

# Import logout models
from .logout_models import (
    LogoutRequest,
    LogoutSuccessResponse,
    LogoutErrorResponse
)

# Import profile models
from .profile_models import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
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
    "RegistrationErrorResponse",

    # Login models
    "UserLoginRequest",
    "LoginSuccessResponse",
    "LoginErrorResponse",

    # Logout models
    "LogoutRequest",
    "LogoutSuccessResponse",
    "LogoutErrorResponse",

    # Profile models
    "UserProfileResponse",
    "UserProfileUpdateRequest",
    "ProfileUpdateSuccessResponse",
    "ProfileUpdateErrorResponse"
]