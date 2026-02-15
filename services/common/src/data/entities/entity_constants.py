"""
Entity Constants

Organized by domain (User, Balance, Asset, Order, Lock) with clear sections:
- Shared Database Fields (Pk, Sk, GSI, Timestamps)
- Domain-specific Field Names
- Domain-specific Validation Constraints
- Domain-specific Default Values

Each domain follows the pattern: *Fields, *Constraints, *Defaults
"""

# ==================== SHARED DATABASE FIELDS ====================
# Used across ALL entities - DynamoDB-specific


class DatabaseFields:
    """DynamoDB field names shared across all entities"""
    PK = "Pk"
    SK = "Sk"
    GSI_PK = "GSI-PK"
    GSI_SK = "GSI-SK"


class TimestampFields:
    """Timestamp field names shared across all entities"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    # Attribute name for extracting date from datetime (datetime.date() method)
    DATE_ATTR = "date"


# ==================== USER DOMAIN ====================


class UserFields:
    """User entity field names"""
    # Identity fields
    USERNAME = "username"
    EMAIL = "email"
    PASSWORD_HASH = "password_hash"
    PASSWORD = "password"  # DEPRECATED: Use PASSWORD_HASH instead (kept for backward compatibility)

    # Profile fields
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    PHONE = "phone"
    DATE_OF_BIRTH = "date_of_birth"
    ROLE = "role"
    MARKETING_EMAILS_CONSENT = "marketing_emails_consent"

    # DynamoDB-specific
    SK_VALUE = "USER"
    ENTITY_TYPE = "user"

    # Password markers
    HASHED_PASSWORD_MARKER = "[HASHED]"


class UserConstraints:
    """User field validation constraints"""
    USERNAME_MAX_LENGTH = 30
    EMAIL_MAX_LENGTH = 255
    PASSWORD_MAX_LENGTH = 128
    FIRST_NAME_MAX_LENGTH = 50
    LAST_NAME_MAX_LENGTH = 50
    PHONE_MAX_LENGTH = 15
    ROLE_MAX_LENGTH = 20


# For backward compatibility during migration - combined constraints
class FieldConstraints:
    """
    DEPRECATED: Use UserConstraints, AssetConstraints, or OrderConstraints instead
    Combined constraints for backward compatibility only
    """
    # User constraints
    USERNAME_MAX_LENGTH = 30
    EMAIL_MAX_LENGTH = 255
    PASSWORD_MAX_LENGTH = 128
    FIRST_NAME_MAX_LENGTH = 50
    LAST_NAME_MAX_LENGTH = 50
    PHONE_MAX_LENGTH = 15
    ROLE_MAX_LENGTH = 20

    # Asset constraints
    ASSET_ID_MAX_LENGTH = 20
    ASSET_NAME_MAX_LENGTH = 100
    ASSET_DESCRIPTION_MAX_LENGTH = 500
    ASSET_CATEGORY_MAX_LENGTH = 50
    ASSET_SYMBOL_MAX_LENGTH = 20
    ASSET_IMAGE_MAX_LENGTH = 500
    ASSET_DATE_MAX_LENGTH = 50
    ASSET_LAST_UPDATED_MAX_LENGTH = 50

    # Order constraints
    ORDER_ID_MAX_LENGTH = 50


# ==================== BALANCE DOMAIN ====================

class BalanceFields:
    """Balance entity field names"""
    USERNAME = "username"
    CURRENT_BALANCE = "current_balance"
    ENTITY_TYPE = "entity_type"

    # DynamoDB-specific
    SK_VALUE = "BALANCE"
    DEFAULT_ENTITY_TYPE = "balance"


class BalanceTransactionFields:
    """Balance transaction entity field names"""
    USERNAME = "username"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_TYPE = "transaction_type"
    AMOUNT = "amount"
    DESCRIPTION = "description"
    STATUS = "status"
    REFERENCE_ID = "reference_id"
    ENTITY_TYPE = "entity_type"

    # DynamoDB-specific
    PK_PREFIX = "TRANS#"
    DEFAULT_ENTITY_TYPE = "balance_transaction"


# For backward compatibility during migration
TransactionFields = BalanceTransactionFields


# ==================== ASSET DOMAIN ====================


class AssetFields:
    """Asset entity field names"""
    # Core asset fields
    ASSET_ID = "asset_id"
    PRODUCT_ID = "product_id"  # Database primary key
    NAME = "name"
    DESCRIPTION = "description"
    CATEGORY = "category"
    SYMBOL = "symbol"
    IMAGE = "image"
    AMOUNT = "amount"
    PRICE_USD = "price_usd"
    IS_ACTIVE = "is_active"

    # Market data fields (CoinGecko API)
    CURRENT_PRICE = "current_price"
    HIGH_24H = "high_24h"
    LOW_24H = "low_24h"
    CIRCULATING_SUPPLY = "circulating_supply"
    TOTAL_SUPPLY = "total_supply"
    MAX_SUPPLY = "max_supply"
    PRICE_CHANGE_24H = "price_change_24h"
    PRICE_CHANGE_PERCENTAGE_24H = "price_change_percentage_24h"
    PRICE_CHANGE_PERCENTAGE_7D = "price_change_percentage_7d"
    PRICE_CHANGE_PERCENTAGE_30D = "price_change_percentage_30d"
    MARKET_CAP = "market_cap"
    MARKET_CAP_CHANGE_24H = "market_cap_change_24h"
    MARKET_CAP_CHANGE_PERCENTAGE_24H = "market_cap_change_percentage_24h"
    TOTAL_VOLUME_24H = "total_volume_24h"
    VOLUME_CHANGE_24H = "volume_change_24h"
    ATH = "ath"
    ATH_CHANGE_PERCENTAGE = "ath_change_percentage"
    ATL = "atl"
    ATL_CHANGE_PERCENTAGE = "atl_change_percentage"

    # DynamoDB-specific
    SK_VALUE = "ASSET"


class AssetConstraints:
    """Asset field validation constraints"""
    ASSET_ID_MAX_LENGTH = 20
    ASSET_NAME_MAX_LENGTH = 100
    ASSET_DESCRIPTION_MAX_LENGTH = 500
    ASSET_CATEGORY_MAX_LENGTH = 50
    ASSET_SYMBOL_MAX_LENGTH = 20
    ASSET_IMAGE_MAX_LENGTH = 500
    ASSET_DATE_MAX_LENGTH = 50
    ASSET_LAST_UPDATED_MAX_LENGTH = 50


class AssetDefaults:
    """Asset default values"""
    DEFAULT_CATEGORY = "unknown"
    DEFAULT_AMOUNT = "0"


class AssetBalanceFields:
    """Asset balance entity field names"""
    USERNAME = "username"
    ASSET_ID = "asset_id"
    QUANTITY = "quantity"

    # DynamoDB-specific
    SK_PREFIX = "ASSET#"
    SK_VALUE = "ASSET#"
    DEFAULT_ENTITY_TYPE = "asset_balance"


class AssetTransactionFields:
    """Asset transaction entity field names"""
    USERNAME = "username"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_TYPE = "transaction_type"
    ASSET_ID = "asset_id"
    QUANTITY = "quantity"
    PRICE = "price"
    TOTAL_AMOUNT = "total_amount"
    DESCRIPTION = "description"
    STATUS = "status"
    REFERENCE_ID = "reference_id"
    ENTITY_TYPE = "entity_type"

    # DynamoDB-specific
    PK_PREFIX = "ASSET_TRANS#"
    SK_PREFIX = "ASSET#"


# ==================== ORDER DOMAIN ====================


class OrderFields:
    """Order entity field names"""
    ORDER_ID = "order_id"
    USERNAME = "username"
    ORDER_TYPE = "order_type"
    STATUS = "status"
    ASSET_ID = "asset_id"
    QUANTITY = "quantity"
    PRICE = "price"
    TOTAL_AMOUNT = "total_amount"

    # DynamoDB-specific
    SK_VALUE = "ORDER"

    # Environment Variables (DEPRECATED - should be in database_constants.py)
    ORDERS_TABLE_ENV_VAR = "ORDERS_TABLE"


class OrderConstraints:
    """Order field validation constraints"""
    ORDER_ID_MAX_LENGTH = 50


class OrderDefaults:
    """Order default values"""
    DEFAULT_CURRENCY = "USD"  # USD only


# ==================== LOCKING DOMAIN ====================


class LockFields:
    """User lock entity field names"""
    # DynamoDB-specific
    PK_PREFIX = "USER#"
    SK_VALUE = "LOCK"
    ENTITY_TYPE = "user_lock"


# ==================== DEPRECATED - FOR BACKWARD COMPATIBILITY ====================
# The following classes are deprecated and kept only for backward compatibility
# They will be removed in a future version after all references are updated


class UserConstants:
    """
    DEPRECATED: Use database_constants.py instead
    Kept for backward compatibility only
    """
    EMAIL_INDEX_NAME = "EmailIndex"
    USERS_TABLE_ENV_VAR = "USERS_TABLE"
    INVENTORY_TABLE_ENV_VAR = "INVENTORY_TABLE"
