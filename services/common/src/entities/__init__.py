"""
Common models package for all services
"""

# Import user enums
from .user_enums import UserRole, DEFAULT_USER_ROLE, VALID_ROLES

# Import user models
from .user import User, UserCreate, UserLogin, UserResponse
from .auth import LoginRequest, TokenResponse

# Import asset models
from .asset import Asset, AssetCreate, AssetResponse, AssetUpdate, AssetListResponse

# Import order models
from .order import (
    OrderType,
    OrderStatus,
    Order,
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderListResponse
)

__all__ = [
    # User enums
    "UserRole",
    "DEFAULT_USER_ROLE",
    "VALID_ROLES",

    # User models
    "User",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "LoginRequest",

    # Asset models
    "Asset",
    "AssetCreate",
    "AssetResponse",
    "AssetUpdate",
    "AssetListResponse",

    # Order enums
    "OrderType",
    "OrderStatus",

    # Order models
    "Order",
    "OrderCreate",
    "OrderResponse",
    "OrderUpdate",
    "OrderListResponse"
]
