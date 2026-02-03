"""
API Constants - Consolidated

Combines all API-related constants from multiple files:
- HTTP Status Codes (from http_status.py)
- API Response Descriptions (from api_responses.py)
- Error Messages (from error_messages.py)
- Request Headers (from request_headers.py)

This file provides a single source of truth for all API-related constants.
"""
from enum import IntEnum, Enum


# ==================== HTTP STATUS CODES ====================


class HTTPStatus(IntEnum):
    """HTTP Status Codes - Only what we actually use in the codebase"""

    # Success responses
    OK = 200
    CREATED = 201

    # Client error responses
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server error responses
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# ==================== API RESPONSE DESCRIPTIONS ====================


class APIResponseDescriptions(str, Enum):
    """API response descriptions that are actually shared across multiple services"""

    # Generic success (used across services)
    SUCCESS = "Operation completed successfully"

    # Common error responses (used across user, order, and other services)
    ERROR_UNAUTHORIZED = "Unauthorized"
    ERROR_AUTHENTICATION_FAILED = "Authentication failed"
    ERROR_VALIDATION = "Invalid input data"
    ERROR_SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    ERROR_INTERNAL_SERVER = "Internal server error"
    ERROR_CONFLICT = "Resource conflict"
    ERROR_FORBIDDEN = "Access denied"
    ERROR_NOT_FOUND = "Resource not found"
    ERROR_UNPROCESSABLE_ENTITY = "Invalid request data"


class APIResponseKeys(str, Enum):
    """Standard keys used in FastAPI response definitions"""
    DESCRIPTION = "description"
    MODEL = "model"


# ==================== ERROR MESSAGES ====================


class ErrorMessages:
    """Error Messages - Only what we actually use in the codebase"""

    # Server Errors
    INTERNAL_SERVER_ERROR = "An internal server error occurred. Please try again later."
    SERVICE_UNAVAILABLE = "The service is temporarily unavailable. Please try again later."

    # Authentication & Authorization
    AUTHENTICATION_FAILED = "Authentication failed. Please check your credentials and try again."
    ACCESS_DENIED = "Access denied. You don't have permission to perform this action."

    # Resource Errors
    RESOURCE_NOT_FOUND = "The requested resource was not found."
    USER_NOT_FOUND = "User not found."

    # Validation Errors
    VALIDATION_ERROR = "The request contains invalid data. Please check your input and try again."
    INSUFFICIENT_BALANCE = "Insufficient balance for this operation."


# ==================== REQUEST HEADERS ====================


class RequestHeaders(str, Enum):
    """Request headers used across all services - standardized from Gateway"""

    # Standard HTTP headers
    CONTENT_TYPE = "Content-Type"
    AUTHORIZATION = "Authorization"
    USER_AGENT = "User-Agent"

    # Custom headers from Gateway
    REQUEST_ID = "X-Request-ID"
    USER_NAME = "X-User-Name"
    USER_ID = "X-User-ID"
    USER_ROLE = "X-User-Role"
    AUTHENTICATED = "X-Authenticated"
    SOURCE = "X-Source"
    AUTH_SERVICE = "X-Auth-Service"
    SOURCE_SERVICE = "X-Source-Service"
    SESSION_ID = "X-Session-ID"


class RequestHeaderDefaults:
    """Default values for request headers when not provided"""

    # Header default values
    REQUEST_ID_DEFAULT = "no-request-id"
    USERNAME_DEFAULT = "testuser"
    USER_ID_DEFAULT = "1"
    USER_ROLE_DEFAULT = "customer"
    USER_AGENT_DEFAULT = "unknown"


class ExtractedUserFields:
    """Field names for extracted user information from headers"""

    USER_ID_KEY = "user_id"
    USER_ROLE_KEY = "user_role"
    REQUEST_ID_KEY = "request_id"
    SOURCE_SERVICE_KEY = "source_service"
