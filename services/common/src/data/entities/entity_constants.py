"""
Entity Constants - Minimal Version

Only contains truly shared constants that cannot live in entity models.
All field-specific constants have been moved into their respective PynamoDB models.
"""

# ==================== SHARED DATABASE CONSTANTS ====================
# These are used across ALL entities and cannot be in individual models

class DatabaseFields:
    """DynamoDB field names - shared across all entities"""
    PK = "Pk"
    SK = "Sk"
    GSI_PK = "GSI-PK"
    GSI_SK = "GSI-SK"


class TimestampFields:
    """Timestamp field names - shared across all entities"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


# ==================== FIELD CONSTRAINTS ====================
# Validation constraints used across multiple entities
# Keep these here as they might be used in API validation too

class LockFields:
    """Lock-related field constants"""
    PK_PREFIX = "USER#"
    SK_VALUE = "LOCK"
    ENTITY_TYPE = "user_lock"


class FieldConstraints:
    """Field validation constraints"""
    USERNAME_MAX_LENGTH = 30
    EMAIL_MAX_LENGTH = 255
    PASSWORD_MAX_LENGTH = 128
    FIRST_NAME_MAX_LENGTH = 50
    LAST_NAME_MAX_LENGTH = 50
    PHONE_MAX_LENGTH = 15
    ROLE_MAX_LENGTH = 20

    # Asset field constraints
    ASSET_ID_MAX_LENGTH = 20
    ASSET_NAME_MAX_LENGTH = 100
    ASSET_DESCRIPTION_MAX_LENGTH = 500
    ASSET_CATEGORY_MAX_LENGTH = 50
    ASSET_SYMBOL_MAX_LENGTH = 20
    ASSET_IMAGE_MAX_LENGTH = 500
    ASSET_DATE_MAX_LENGTH = 50
    ASSET_LAST_UPDATED_MAX_LENGTH = 50

    # Order field constraints
    ORDER_ID_MAX_LENGTH = 50


# ==================== ENTITY-SPECIFIC CONSTANTS ====================
# These are used by specific entities but need to be shared

class UserFields:
    """User entity field names and values"""
    USERNAME = "username"
    EMAIL = "email"
    PASSWORD = "password"
    PASSWORD_HASH = "password_hash"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    PHONE = "phone"
    DATE_OF_BIRTH = "date_of_birth"
    MARKETING_EMAILS_CONSENT = "marketing_emails_consent"
    ROLE = "role"

    # Sort Key Values
    SK_VALUE = "USER"

    # Entity Type
    ENTITY_TYPE = "user"

    # Password Markers
    HASHED_PASSWORD_MARKER = "[HASHED]"


class UserConstants:
    """User entity specific constants"""
    EMAIL_INDEX_NAME = "EmailIndex"
    USERS_TABLE_ENV_VAR = "USERS_TABLE"
    INVENTORY_TABLE_ENV_VAR = "INVENTORY_TABLE"


# Balance Entity Constants
class BalanceFields:
    """Balance entity field names and values"""
    USERNAME = "username"
    CURRENT_BALANCE = "current_balance"
    ENTITY_TYPE = "entity_type"

    # Sort Key Values
    SK_VALUE = "BALANCE"

    # Entity Type Values
    DEFAULT_ENTITY_TYPE = "balance"

# Balance Transaction Entity Constants
class TransactionFields:
    """Balance transaction entity field names and values"""
    USERNAME = "username"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_TYPE = "transaction_type"
    AMOUNT = "amount"
    DESCRIPTION = "description"
    STATUS = "status"
    REFERENCE_ID = "reference_id"
    ENTITY_TYPE = "entity_type"

    # Primary Key Prefix
    PK_PREFIX = "TRANS#"

    # Entity Type Values
    DEFAULT_ENTITY_TYPE = "balance_transaction"

# Asset Entity Constants
class AssetFields:
    """Asset entity field names and values"""
    ASSET_ID = "asset_id"
    PRODUCT_ID = "product_id"  # Database primary key
    NAME = "name"
    DESCRIPTION = "description"
    CATEGORY = "category"
    AMOUNT = "amount"
    PRICE_USD = "price_usd"
    IS_ACTIVE = "is_active"

    # Additional asset fields
    SYMBOL = "symbol"
    IMAGE = "image"

    # Default values
    DEFAULT_CATEGORY = "unknown"
    DEFAULT_AMOUNT = "0"

    # CoinGecko API fields
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

    # Sort Key Values
    SK_VALUE = "ASSET"

# Asset Balance Entity Constants
class AssetBalanceFields:
    """Asset balance entity field names and values"""
    USERNAME = "username"
    ASSET_ID = "asset_id"
    QUANTITY = "quantity"

    # Sort Key Prefix
    SK_PREFIX = "ASSET#"
    SK_VALUE = "ASSET#"

    # Entity Type
    DEFAULT_ENTITY_TYPE = "asset_balance"

# Asset Transaction Entity Constants
class AssetTransactionFields:
    """Asset transaction entity field names and values"""
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

    # Primary Key Prefix
    PK_PREFIX = "ASSET_TRANS#"

    # Sort Key Prefix
    SK_PREFIX = "ASSET#"

# Order Entity Constants
class OrderFields:
    """Order entity field names and values"""
    ORDER_ID = "order_id"
    USERNAME = "username"
    ORDER_TYPE = "order_type"
    STATUS = "status"
    ASSET_ID = "asset_id"
    QUANTITY = "quantity"
    PRICE = "price"
    TOTAL_AMOUNT = "total_amount"

    # Sort Key Values
    SK_VALUE = "ORDER"

    # Environment Variables
    ORDERS_TABLE_ENV_VAR = "ORDERS_TABLE"

    # Currency constants (USD only)
    DEFAULT_CURRENCY = "USD"
