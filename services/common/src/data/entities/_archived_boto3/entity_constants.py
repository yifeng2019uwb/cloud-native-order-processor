"""
Entity Constants

Centralized constants for all entity field names, values, and database schema definitions.
This file contains all hardcoded string values used across entity classes to avoid
magic strings and improve maintainability.
"""

# Database Field Names
class DatabaseFields:
    """DynamoDB field names"""
    PK = "Pk"
    SK = "Sk"
    GSI_PK = "GSI-PK"
    GSI_SK = "GSI-SK"

# Timestamp Field Names
class TimestampFields:
    """Timestamp field names"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

# User Entity Constants
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

# Field Length Constraints
class FieldConstraints:
    """Field length and validation constraints"""
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
