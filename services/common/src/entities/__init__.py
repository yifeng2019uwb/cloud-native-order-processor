"""
Common models package for all services
"""

# Import user entities
from .user import User, UserCreate, UserLogin, UserResponse, UserRole, DEFAULT_USER_ROLE, VALID_ROLES, LoginRequest, TokenResponse

# Import asset entities
from .inventory import Asset, AssetCreate, AssetResponse, AssetUpdate, AssetListResponse

# Import order entities
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
