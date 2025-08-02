"""
Pydantic models package for user authentication service
Path: cloud-native-order-processor/services/user-service/src/models/__init__.py
"""

# Import shared models
from .shared.common import (
    SuccessResponse,
    ErrorResponse,
    TokenResponse,
    UserBaseInfo
)

# Import registration models
from .auth.registration import (
    UserRegistrationRequest,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)

# Import login models
from .auth.login import (
    UserLoginRequest,
    LoginSuccessResponse,
    LoginErrorResponse
)

# Import logout models
from .auth.logout import (
    LogoutRequest,
    LogoutSuccessResponse,
    LogoutErrorResponse
)

# Import profile models
from .auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)

# Import balance models
from .balance import (
    BalanceResponse,
    DepositRequest,
    DepositResponse,
    WithdrawRequest,
    WithdrawResponse,
    TransactionResponse,
    TransactionListResponse
)

__all__ = [
    # Shared models
    "SuccessResponse",
    "ErrorResponse",
    "TokenResponse",
    "UserBaseInfo",

    # Registration models
    "UserRegistrationRequest",
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
    "ProfileUpdateErrorResponse",

    # Balance models
    "BalanceResponse",
    "DepositRequest",
    "DepositResponse",
    "WithdrawRequest",
    "WithdrawResponse",
    "TransactionResponse",
    "TransactionListResponse"
]