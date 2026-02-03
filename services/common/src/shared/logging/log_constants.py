"""
Log Constants

Centralized constants for log action names, field names, and default values across all services.
This ensures consistency and prevents hardcoding of log strings.
"""
from enum import Enum


# Logger Names - Use Enum since these are fixed choices
class LoggerName(str, Enum):
    """Service logger names."""
    AUTH = "auth"
    USER = "user"
    ORDER = "order"
    INVENTORY = "inventory"
    INSIGHTS = "insights"
    GATEWAY = "gateway"
    DATABASE = "database"
    CACHE = "cache"
    AUDIT = "audit"


# Log Levels - Use Enum since these are standard levels
class LogLevel(str, Enum):
    """Standard log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Log Actions - Simple constants since these are just strings
class LogAction:
    """Core log actions used across all services."""

    # Auth
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"

    # User
    USER_REGISTRATION_SUCCESS = "user_registration_success"
    USER_REGISTRATION_FAILED = "user_registration_failed"
    USER_LOGIN_SUCCESS = "user_login_success"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_LOGOUT = "user_logout"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_PASSWORD_CHANGE = "user_password_change"

    # System
    SERVICE_START = "service_start"
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    HEALTH_CHECK = "health_check"

    # Data
    DB_CONNECT = "db_connect"
    DB_OPERATION = "db_operation"
    CACHE_OPERATION = "cache_operation"

    # Financial
    DEPOSIT_SUCCESS = "deposit_success"
    DEPOSIT_FAILED = "deposit_failed"
    WITHDRAWAL_SUCCESS = "withdrawal_success"
    WITHDRAWAL_FAILED = "withdrawal_failed"
    ORDER_CREATED = "order_created"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_EXECUTED = "order_executed"
    PORTFOLIO_VIEWED = "portfolio_viewed"

    # Errors
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"

    # Security
    SECURITY_EVENT = "security_event"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


# Log Field Names - Simple constants for structured logging
class LogField:
    """Log field names for extra data in structured logging."""

    # Request
    USER_AGENT = "user_agent"
    CLIENT_IP = "client_ip"
    IP_ADDRESS = "ip_address"
    REQUEST_ID = "request_id"
    TIMESTAMP = "timestamp"

    # User
    USERNAME = "username"
    EMAIL = "email"
    USER_ID = "user_id"
    ROLE = "role"
    SESSION_ID = "session_id"

    # Business
    AMOUNT = "amount"
    ASSET_ID = "asset_id"
    ORDER_ID = "order_id"
    ORDER_TYPE = "order_type"
    QUANTITY = "quantity"
    PRICE = "price"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_TYPE = "transaction_type"
    BALANCE = "balance"

    # Error
    ERROR = "error"
    ERROR_TYPE = "error_type"
    FAILURE_REASON = "failure_reason"
    AUDIT_REASON = "audit_reason"

    # System
    SERVICE = "service"
    ENVIRONMENT = "environment"
    STATUS = "status"

    # Security
    TOKEN_TYPE = "token_type"
    RESOURCE = "resource"


# Defaults - Simple constants for configuration
class LogDefault:
    """Default values for logging configuration."""
    LOG_FILE_PATH = "logs"
    SERVICES_DIR = "services"
    TMP_PATH = "/tmp"
    UNKNOWN = "unknown"
    TIMESTAMP_SUFFIX = "Z"
    LOG_FILE_EXTENSION = ".log"
    LOG_FILE_PATH_ENV = "LOG_FILE_PATH"
    SECURITY_ACTION_PREFIX = "security_"
    FAILED_KEYWORD = "failed"
    DENIED_KEYWORD = "denied"
    FILE_APPEND_MODE = "a"
    FILE_ENCODING = "utf-8"
    NEWLINE = "\n"
    UUID_HEX_LENGTH = 8
    LOG_FILE_ATTR = "log_file"