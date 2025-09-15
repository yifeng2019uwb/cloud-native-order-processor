"""
Common models package for all services
"""

# Import entity constants
from .entity_constants import (
    DatabaseFields,
    TimestampFields,
    UserFields,
    BalanceFields,
    TransactionFields,
    AssetFields,
    AssetBalanceFields,
    AssetTransactionFields,
    OrderFields,
    FieldConstraints
)

# Import user entities (including balance entities)
from .user import (
    User, UserItem, UserRole, DEFAULT_USER_ROLE, VALID_ROLES,
    Balance, BalanceTransaction, BalanceItem, BalanceTransactionItem
)

# Import asset entities
from .inventory import Asset, AssetItem

# Import asset entities (balance and transaction)
from .asset import (
    AssetBalance,
    AssetBalanceItem,
    AssetTransaction,
    AssetTransactionItem,
    AssetTransactionType,
    AssetTransactionStatus
)

# Import order entities
from .order import (
    OrderType,
    OrderStatus,
    Order,
    OrderItem
)

__all__ = [
    # Entity Constants
    "DatabaseFields",
    "TimestampFields",
    "UserFields",
    "BalanceFields",
    "TransactionFields",
    "AssetFields",
    "AssetBalanceFields",
    "AssetTransactionFields",
    "OrderFields",
    "FieldConstraints",

    # User enums
    "UserRole",
    "DEFAULT_USER_ROLE",
    "VALID_ROLES",

    # User models
    "User",
    "UserItem",

    # Balance models
    "Balance",
    "BalanceTransaction",
    "BalanceItem",
    "BalanceTransactionItem",

    # Asset models
    "Asset",
    "AssetItem",

    # Asset Balance enums
    "AssetTransactionType",
    "AssetTransactionStatus",

    # Asset Balance models
    "AssetBalance",
    "AssetBalanceItem",

    # Asset Transaction models
    "AssetTransaction",
    "AssetTransactionItem",

    # Order enums
    "OrderType",
    "OrderStatus",

    # Order models
    "Order",
    "OrderItem"
]
