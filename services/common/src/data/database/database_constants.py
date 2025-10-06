"""
Database and Data-Related Constants

This file consolidates all database, Redis, and data-related constants
to eliminate hardcoded values throughout the data layer.
"""

import os
from typing import Optional


# ==================== ENVIRONMENT VARIABLES ====================

class EnvironmentVariables:
    """Environment variable names for database configuration"""

    # AWS/DynamoDB
    AWS_REGION = "AWS_REGION"
    USERS_TABLE = "USERS_TABLE"
    ORDERS_TABLE = "ORDERS_TABLE"
    INVENTORY_TABLE = "INVENTORY_TABLE"
    AWS_WEB_IDENTITY_TOKEN_FILE = "AWS_WEB_IDENTITY_TOKEN_FILE"
    AWS_ROLE_ARN = "AWS_ROLE_ARN"

    # Redis
    REDIS_HOST = "REDIS_HOST"
    REDIS_PORT = "REDIS_PORT"
    REDIS_DB = "REDIS_DB"
    REDIS_PASSWORD = "REDIS_PASSWORD"
    REDIS_ENDPOINT = "REDIS_ENDPOINT"
    REDIS_MAX_CONNECTIONS = "REDIS_MAX_CONNECTIONS"
    ENVIRONMENT = "ENVIRONMENT"


# ==================== DEFAULT VALUES ====================

class DefaultValues:
    """Default values for database configuration"""

    # AWS/DynamoDB
    DEFAULT_AWS_REGION = "us-west-2"
    DEFAULT_USERS_TABLE = "users"
    DEFAULT_ORDERS_TABLE = "orders"
    DEFAULT_INVENTORY_TABLE = "inventory"

    # Redis
    DEFAULT_REDIS_HOST = "redis.order-processor.svc.cluster.local"
    DEFAULT_REDIS_PORT = 6379
    DEFAULT_REDIS_DB = 0
    DEFAULT_REDIS_MAX_CONNECTIONS = 10
    DEFAULT_ENVIRONMENT = "dev"


# ==================== DATABASE CONFIGURATION ====================

class DatabaseConfig:
    """Database configuration constants"""

    # DynamoDB
    BILLING_MODE_PAY_PER_REQUEST = "PAY_PER_REQUEST"
    BILLING_MODE_PROVISIONED = "PROVISIONED"
    DYNAMODB_SERVICE_NAME = "dynamodb"
    STS_SERVICE_NAME = "sts"

    # Connection settings
    CONNECTION_TIMEOUT = 30
    READ_TIMEOUT = 30
    MAX_RETRIES = 3

    # Session settings
    ROLE_SESSION_NAME = "order-processor-session"

    # AWS credential field names
    ACCESS_KEY_ID = "AccessKeyId"
    SECRET_ACCESS_KEY = "SecretAccessKey"
    SESSION_TOKEN = "SessionToken"
    CREDENTIALS = "Credentials"

    # DynamoDB response field names
    ITEM = "Item"
    ITEMS = "Items"
    ATTRIBUTES = "Attributes"
    KEY = "Key"
    UPDATE_EXPRESSION = "UpdateExpression"
    EXPRESSION_ATTRIBUTE_VALUES = "ExpressionAttributeValues"
    EXPRESSION_ATTRIBUTE_NAMES = "ExpressionAttributeNames"
    RETURN_VALUES = "ReturnValues"
    KEY_CONDITION_EXPRESSION = "KeyConditionExpression"
    FILTER_EXPRESSION = "FilterExpression"
    INDEX_NAME = "IndexName"
    LIMIT = "Limit"
    ALL_NEW = "ALL_NEW"
    ALL_OLD = "ALL_OLD"





class AWSConfig:
    """AWS configuration constants"""
    DEFAULT_REGION = "us-west-2"
    BILLING_MODE_PAY_PER_REQUEST = "PAY_PER_REQUEST"
    BILLING_MODE_PROVISIONED = "PROVISIONED"
    AWS_REGION_ENV_VAR = "AWS_REGION"


# ==================== REDIS CONFIGURATION ====================

class RedisConfig:
    """Redis configuration constants"""

    # Connection settings
    CONNECTION_TIMEOUT = 5
    SOCKET_TIMEOUT = 5
    SOCKET_CONNECT_TIMEOUT = 5
    RETRY_ON_TIMEOUT = True
    HEALTH_CHECK_INTERVAL = 30
    PRODUCTION_SOCKET_TIMEOUT = 10
    PRODUCTION_SOCKET_CONNECT_TIMEOUT = 10

    # Pool settings
    MAX_CONNECTIONS = 10
    MIN_CONNECTIONS = 1

    # Key patterns
    SESSION_KEY_PREFIX = "session:"
    LOCK_KEY_PREFIX = "lock:"
    CACHE_KEY_PREFIX = "cache:"

    # Environment values
    PRODUCTION_ENV = "prod"
    DEVELOPMENT_ENV = "dev"

    # SSL settings
    SSL_CERT_REQUIRED = "required"

    # URL schemes
    REDIS_SCHEME = "redis"
    REDISS_SCHEME = "rediss"

    # Configuration keys (for dictionary keys)
    HOST_KEY = "host"
    PORT_KEY = "port"
    DB_KEY = "db"
    PASSWORD_KEY = "password"
    DECODE_RESPONSES_KEY = "decode_responses"
    SOCKET_CONNECT_TIMEOUT_KEY = "socket_connect_timeout"
    SOCKET_TIMEOUT_KEY = "socket_timeout"
    RETRY_ON_TIMEOUT_KEY = "retry_on_timeout"
    HEALTH_CHECK_INTERVAL_KEY = "health_check_interval"
    SSL_KEY = "ssl"
    SSL_CERT_REQS_KEY = "ssl_cert_reqs"

    MAX_CONNECTIONS_KEY = "max_connections"
    RETRY_ON_TIMEOUT_KEY = "retry_on_timeout"



# ==================== TABLE NAMES ====================

class TableNames:
    """DynamoDB table names"""
    USERS = "users"
    ORDERS = "orders"
    INVENTORY = "inventory"


# ==================== CONFIGURATION FUNCTIONS ====================

def get_aws_region() -> str:
    """Get AWS region from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.AWS_REGION, DefaultValues.DEFAULT_AWS_REGION)


def get_users_table_name() -> str:
    """Get users table name from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.USERS_TABLE, DefaultValues.DEFAULT_USERS_TABLE)


def get_orders_table_name() -> str:
    """Get orders table name from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.ORDERS_TABLE, DefaultValues.DEFAULT_ORDERS_TABLE)


def get_inventory_table_name() -> str:
    """Get inventory table name from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.INVENTORY_TABLE, DefaultValues.DEFAULT_INVENTORY_TABLE)


def get_redis_host() -> str:
    """Get Redis host from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.REDIS_HOST, DefaultValues.DEFAULT_REDIS_HOST)


def get_redis_port() -> int:
    """Get Redis port from environment variable with fallback"""
    return int(os.getenv(EnvironmentVariables.REDIS_PORT, str(DefaultValues.DEFAULT_REDIS_PORT)))


def get_redis_db() -> int:
    """Get Redis database number from environment variable with fallback"""
    return int(os.getenv(EnvironmentVariables.REDIS_DB, str(DefaultValues.DEFAULT_REDIS_DB)))


def get_redis_password() -> Optional[str]:
    """Get Redis password from environment variable"""
    return os.getenv(EnvironmentVariables.REDIS_PASSWORD)


def get_redis_endpoint() -> Optional[str]:
    """Get Redis endpoint from environment variable"""
    return os.getenv(EnvironmentVariables.REDIS_ENDPOINT)


def get_redis_max_connections() -> int:
    """Get Redis max connections from environment variable with fallback"""
    return int(os.getenv(EnvironmentVariables.REDIS_MAX_CONNECTIONS, str(DefaultValues.DEFAULT_REDIS_MAX_CONNECTIONS)))


def get_aws_web_identity_token_file() -> Optional[str]:
    """Get AWS Web Identity Token File from environment variable"""
    return os.getenv(EnvironmentVariables.AWS_WEB_IDENTITY_TOKEN_FILE)


def get_aws_role_arn() -> Optional[str]:
    """Get AWS Role ARN from environment variable"""
    return os.getenv(EnvironmentVariables.AWS_ROLE_ARN)


def get_environment() -> str:
    """Get environment from environment variable with fallback"""
    return os.getenv(EnvironmentVariables.ENVIRONMENT, DefaultValues.DEFAULT_ENVIRONMENT).lower()


def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == RedisConfig.PRODUCTION_ENV


def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment() == RedisConfig.DEVELOPMENT_ENV


def get_redis_namespace() -> str:
    """Get Redis namespace for key prefixing"""
    return f"order-processor:{get_environment()}"


# ==================== REDIS CONFIGURATION BUILDER ====================

def build_redis_config() -> dict:
    """Build Redis configuration dictionary from environment variables"""
    environment = get_environment()

    # Base configuration
    config = {
        RedisConfig.HOST_KEY: get_redis_host(),
        RedisConfig.PORT_KEY: get_redis_port(),
        RedisConfig.DB_KEY: get_redis_db(),
        RedisConfig.PASSWORD_KEY: get_redis_password(),
        RedisConfig.DECODE_RESPONSES_KEY: True,
        RedisConfig.SOCKET_CONNECT_TIMEOUT_KEY: RedisConfig.SOCKET_CONNECT_TIMEOUT,
        RedisConfig.SOCKET_TIMEOUT_KEY: RedisConfig.SOCKET_TIMEOUT,
        RedisConfig.RETRY_ON_TIMEOUT_KEY: RedisConfig.RETRY_ON_TIMEOUT,
        RedisConfig.HEALTH_CHECK_INTERVAL_KEY: RedisConfig.HEALTH_CHECK_INTERVAL,
    }

    # Environment-specific overrides
    if is_production():
        # AWS ElastiCache configuration
        config.update({
            RedisConfig.SSL_KEY: True,
            RedisConfig.SSL_CERT_REQS_KEY: RedisConfig.SSL_CERT_REQUIRED,
            RedisConfig.SOCKET_CONNECT_TIMEOUT_KEY: RedisConfig.PRODUCTION_SOCKET_CONNECT_TIMEOUT,
            RedisConfig.SOCKET_TIMEOUT_KEY: RedisConfig.PRODUCTION_SOCKET_TIMEOUT,
        })

        # Use AWS ElastiCache endpoint if available
        aws_redis_endpoint = get_redis_endpoint()
        if aws_redis_endpoint:
            config[RedisConfig.HOST_KEY] = aws_redis_endpoint
    else:
        # Local K8s configuration
        config.update({
            RedisConfig.SSL_KEY: False,
            RedisConfig.SSL_CERT_REQS_KEY: None,
        })

    return config


def build_redis_pool_params() -> dict:
    """Build Redis connection pool parameters"""
    return {
        RedisConfig.MAX_CONNECTIONS_KEY: get_redis_max_connections(),
        RedisConfig.RETRY_ON_TIMEOUT_KEY: RedisConfig.RETRY_ON_TIMEOUT,
    }
