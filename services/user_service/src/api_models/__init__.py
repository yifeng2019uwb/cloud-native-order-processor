"""
Pydantic models package for user authentication service
Path: cloud-native-order-processor/services/user-service/src/models/__init__.py
"""

# Import shared models
from .shared.common import (
    UserBaseInfo
)

# Import registration models
from .auth.registration import (
    UserRegistrationRequest,
    RegistrationResponse
)

# Import login models
from .auth.login import (
    UserLoginRequest,
    LoginResponse
)

# Import logout models
from .auth.logout import (
    LogoutRequest,
    LogoutResponse
)

# Import profile models
from .auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileResponse
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
    "UserBaseInfo",

    # Registration models
    "UserRegistrationRequest",
    "RegistrationResponse",

    # Login models
    "UserLoginRequest",
    "LoginResponse",

    # Logout models
    "LogoutRequest",
    "LogoutResponse",

    # Profile models
    "UserProfileResponse",
    "UserProfileUpdateRequest",
    "ProfileResponse",

    # Balance models
    "BalanceResponse",
    "DepositRequest",
    "DepositResponse",
    "WithdrawRequest",
    "WithdrawResponse",
    "TransactionResponse",
    "TransactionListResponse"
]