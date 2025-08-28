"""
Log Action Constants

Centralized constants for log action names across all services.
This ensures consistency and prevents hardcoding of log action strings.
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

    # System Operations
    SERVICE_START = "service_start"
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    HEALTH_CHECK = "health_check"

    # Data Operations
    DB_CONNECT = "db_connect"
    DB_OPERATION = "db_operation"
    CACHE_OPERATION = "cache_operation"

    # Errors
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"

    # Security
    SECURITY_EVENT = "security_event"
