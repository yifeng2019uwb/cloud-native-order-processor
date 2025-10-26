"""
Dependency path constants for unit tests.

This module provides centralized constants for dependency injection paths
used in unit tests, avoiding hardcoded dependency paths.
"""

# =============================================================================
# AUTH DEPENDENCIES
# =============================================================================

# User authentication dependencies
GET_CURRENT_USER = "src.controllers.auth.dependencies.get_current_user"
GET_CURRENT_USER_OPTIONAL = "src.controllers.auth.dependencies.get_current_user_optional"
VERIFY_TOKEN = "src.controllers.auth.dependencies.verify_token"

# =============================================================================
# DAO DEPENDENCIES
# =============================================================================

# User service DAOs
GET_USER_DAO_DEP = "src.controllers.dependencies.get_user_dao"
GET_BALANCE_DAO_DEP = "src.controllers.dependencies.get_balance_dao"

# Order service DAOs
GET_ORDER_DAO_DEP = "src.controllers.dependencies.get_order_dao"
GET_ASSET_TRANSACTION_DAO_DEP = "src.controllers.dependencies.get_asset_transaction_dao"

# Inventory service DAOs
GET_ASSET_DAO_DEP = "src.controllers.dependencies.get_asset_dao"
GET_ASSET_BALANCE_DAO_DEP = "src.controllers.dependencies.get_asset_balance_dao"

# =============================================================================
# SERVICE DEPENDENCIES
# =============================================================================

# External service dependencies
GET_COIN_GECKO_SERVICE = "src.services.fetch_coins.get_coin_gecko_service"
GET_TRANSACTION_MANAGER = "src.core.utils.transaction_manager.TransactionManager"

# =============================================================================
# VALIDATION DEPENDENCIES
# =============================================================================

# Business validation dependencies
GET_BUSINESS_VALIDATORS = "src.validation.business_validators.get_business_validators"

# =============================================================================
# DATABASE METHOD DEPENDENCIES
# =============================================================================

# PynamoDB Model methods
MODEL_SAVE = "save"
MODEL_GET = "get"
MODEL_QUERY = "query"
MODEL_SCAN = "scan"
MODEL_DELETE = "delete"
MODEL_UPDATE = "update"

# PynamoDB Query methods
QUERY_INDEX = "query_index"
SCAN_INDEX = "scan_index"

# PynamoDB Batch methods
BATCH_GET = "batch_get"
BATCH_WRITE = "batch_write"

# PynamoDB Exception classes
DOES_NOT_EXIST = "DoesNotExist"
QUERY_ERROR = "QueryError"
SCAN_ERROR = "ScanError"
PUT_ERROR = "PutError"
DELETE_ERROR = "DeleteError"
UPDATE_ERROR = "UpdateError"

# =============================================================================
# DAO METHOD DEPENDENCIES
# =============================================================================

# Balance DAO methods
BALANCE_DAO_GET_BALANCE = "get_balance"
BALANCE_DAO_UPDATE_BALANCE = "update_balance"
BALANCE_DAO_CREATE_BALANCE = "create_balance"
BALANCE_DAO_CREATE_TRANSACTION = "create_transaction"
BALANCE_DAO_GET_TRANSACTION = "get_transaction"
BALANCE_DAO_GET_USER_TRANSACTIONS = "get_user_transactions"
BALANCE_DAO_CLEANUP_FAILED_TRANSACTION = "cleanup_failed_transaction"

# Asset Balance DAO methods
ASSET_BALANCE_DAO_UPSERT_ASSET_BALANCE = "upsert_asset_balance"
ASSET_BALANCE_DAO_GET_ASSET_BALANCE = "get_asset_balance"
ASSET_BALANCE_DAO_GET_ALL_ASSET_BALANCES = "get_all_asset_balances"
ASSET_BALANCE_DAO_DELETE_ASSET_BALANCE = "delete_asset_balance"

# Asset Transaction DAO methods
ASSET_TRANSACTION_DAO_CREATE_ASSET_TRANSACTION = "create_asset_transaction"
ASSET_TRANSACTION_DAO_GET_ASSET_TRANSACTION = "get_asset_transaction"
ASSET_TRANSACTION_DAO_GET_USER_ASSET_TRANSACTIONS = "get_user_asset_transactions"
ASSET_TRANSACTION_DAO_GET_USER_TRANSACTIONS = "get_user_transactions"
ASSET_TRANSACTION_DAO_DELETE_ASSET_TRANSACTION = "delete_asset_transaction"

# =============================================================================
# LOGGER METHOD DEPENDENCIES
# =============================================================================

# BaseLogger methods
LOGGER_WRITE_TO_FILE = "_write_to_file"

# =============================================================================
# ENTITY METHOD DEPENDENCIES
# =============================================================================

# AssetTransactionItem methods
ASSET_TRANSACTION_ITEM_FROM_ASSET_TRANSACTION = "from_asset_transaction"
ASSET_TRANSACTION_ITEM_TO_ASSET_TRANSACTION = "to_asset_transaction"

# =============================================================================
# JWT METHOD DEPENDENCIES
# =============================================================================

# JWT methods
JWT_ENCODE = "src.auth.security.token_manager.jwt.encode"
JWT_DECODE = "src.auth.security.token_manager.jwt.decode"

# Auth dependencies mock paths
AUTH_DEPENDENCIES_TOKEN_MANAGER = "src.auth.security.auth_dependencies.TokenManager"
AUTH_DEPENDENCIES_GET_REQUEST_ID = "src.auth.security.auth_dependencies.get_request_id_from_request"

# =============================================================================
# REDIS METHOD DEPENDENCIES
# =============================================================================

# Redis client methods
REDIS_PING = "redis.Redis.ping"
REDIS_SET = "redis.Redis.set"
REDIS_GET = "redis.Redis.get"
REDIS_DELETE = "redis.Redis.delete"
REDIS_EXISTS = "redis.Redis.exists"
REDIS_SETEX = "redis.Redis.setex"

# Redis classes
REDIS_CONNECTION_POOL = "redis.ConnectionPool"
REDIS_CLIENT = "redis.Redis"

# Redis ConnectionPool methods
REDIS_CONNECTION_POOL_FROM_URL = "redis.ConnectionPool.from_url"

# Redis manager methods
REDIS_MANAGER_CREATE_POOL = "_create_pool"
REDIS_MANAGER_GET_CLIENT = "get_client"
REDIS_MANAGER_TEST_CONNECTION = "test_connection"

# =============================================================================
# DATABASE CONNECTION DEPENDENCIES
# =============================================================================

# Boto3 and AWS dependencies
BOTO3_SESSION = "boto3.Session"
BOTO3_CLIENT = "boto3.client"
BOTO3_RESOURCE = "boto3.resource"

# Full dependency paths for patching
DYNAMODB_BOTO3_SESSION = "src.data.database.dynamodb_connection.boto3.Session"
DYNAMODB_BOTO3_CLIENT = "src.data.database.dynamodb_connection.boto3.client"
DYNAMODB_BOTO3_RESOURCE = "src.data.database.dynamodb_connection.boto3.resource"

# Environment variable dependencies
OS_GETENV = "os.getenv"
OS_ENVIRON = "os.environ"

# Environment variable names
ENV_USERS_TABLE = "USERS_TABLE"
ENV_ORDERS_TABLE = "ORDERS_TABLE"
ENV_INVENTORY_TABLE = "INVENTORY_TABLE"
ENV_AWS_REGION = "AWS_REGION"

# Redis dependencies
REDIS_CONNECTION_PARAMS = "src.data.database.redis_connection.get_redis_connection_params"
REDIS_CONFIG = "src.data.database.redis_config.get_redis_config"

# Full dependency paths for patching
REDIS_CONFIG_OS_GETENV = "src.data.database.redis_config.os.getenv"
REDIS_CONFIG_GET_REDIS_CONFIG = "src.data.database.redis_config.get_redis_config"

# Redis connection dependencies
REDIS_CONNECTION_GET_PARAMS = "src.data.database.redis_connection.get_redis_connection_params"
REDIS_CONNECTION_MANAGER = "src.data.database.redis_connection.RedisConnectionManager"
REDIS_CONNECTION_GET_MANAGER = "src.data.database.redis_connection.get_redis_manager"
REDIS_CONNECTION_REDIS_MANAGER = "src.data.database.redis_connection._redis_manager"
REDIS_CONNECTION_GET_CONFIG = "src.data.database.redis_connection.get_redis_config"
REDIS_CONNECTION_OS_GETENV = "src.data.database.redis_connection.os.getenv"

# DynamoDB dependencies
DYNAMODB_CONNECTION = "src.data.database.dynamodb_connection.DynamoDBConnection"

# STS Client dependencies
STS_CLIENT = "src.aws.sts_client.STSClient"
