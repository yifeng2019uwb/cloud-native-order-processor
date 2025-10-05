"""
Log Constants

Centralized constants for log action names, field names, and default values across all services.
This ensures consistency and prevents hardcoding of log strings.
"""

# Logger Names - Simplified logger naming for all services
class Loggers:
    """Service logger names."""
    AUTH = "auth"
    USER = "user"
    ORDER = "order"
    INVENTORY = "inventory"
    GATEWAY = "gateway"

    # Infrastructure
    DATABASE = "database"
    CACHE = "cache"
    AUDIT = "audit"


# Log Actions - Simple, essential actions we actually use
class LogActions:
    """Core log actions used across all services."""

    # Authentication & Authorization
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"

    # User Management
    USER_REGISTRATION_SUCCESS = "user_registration_success"
    USER_REGISTRATION_FAILED = "user_registration_failed"
    USER_LOGIN_SUCCESS = "user_login_success"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_LOGOUT = "user_logout"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_PASSWORD_CHANGE = "user_password_change"

    # System Operations
    SERVICE_START = "service_start"
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    HEALTH_CHECK = "health_check"

    # Data Operations
    DB_CONNECT = "db_connect"
    DB_OPERATION = "db_operation"
    CACHE_OPERATION = "cache_operation"

    # Financial Operations
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

    # Security & Audit
    SECURITY_EVENT = "security_event"
    AUDIT_LOGIN = "audit_login"
    AUDIT_LOGOUT = "audit_logout"
    AUDIT_ACCESS = "audit_access"
    AUDIT_ACTION = "audit_action"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


# Log Field Names - Constants for extra data field names
class LogFields:
    """Log field names used in extra data for structured logging."""

    # Request Information
    USER_AGENT = "user_agent"
    CLIENT_IP = "client_ip"
    REQUEST_ID = "request_id"
    TIMESTAMP = "timestamp"

    # User Information
    USERNAME = "username"
    EMAIL = "email"
    USER_ID = "user_id"
    ROLE = "role"

    # Business Data
    AMOUNT = "amount"
    ASSET_ID = "asset_id"
    ORDER_ID = "order_id"
    ORDER_TYPE = "order_type"
    QUANTITY = "quantity"
    PRICE = "price"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_TYPE = "transaction_type"
    BALANCE = "balance"

    # Request Parameters
    LIMIT = "limit"
    OFFSET = "offset"

    # Error Information
    ERROR = "error"
    ERROR_TYPE = "error_type"
    ERROR_ID = "error_id"

    # Token Information
    TOKEN_TYPE = "token_type"
    EXPIRES_IN_HOURS = "expires_in_hours"

    # System Information
    SERVICE = "service"
    VERSION = "version"
    ENVIRONMENT = "environment"
    STATUS = "status"

    # Database Information
    DATABASE = "database"
    CHECK_INTERVAL = "check_interval"
    LAST_CHECK = "last_check"

    # Security Information
    IP_ADDRESS = "ip_address"

    # Audit Information
    AUDIT_REASON = "audit_reason"
    AUDIT_DETAILS = "audit_details"
    SESSION_ID = "session_id"
    TOKEN_ID = "token_id"
    FAILURE_REASON = "failure_reason"
    SUCCESS_REASON = "success_reason"
    RESOURCE = "resource"


# Log Extra Defaults - Default values for log extra fields
class LogExtraDefaults:
    """Default values for log extra fields when not available."""

    UNKNOWN = "unknown"
    UNKNOWN_VALUE = "unknown"
    UNKNOWN_IP = "unknown"
    UNKNOWN_USER_AGENT = "unknown"
