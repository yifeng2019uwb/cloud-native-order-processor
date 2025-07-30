"""
Standardized error codes for all services
Path: services/common/src/exceptions/error_codes.py
"""

from enum import Enum
from typing import Dict


class CommonErrorCode(str, Enum):
    """Standard error codes used across all services"""

    # Authentication & Authorization
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"

    # Validation & Input
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Resources
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_EXISTS = "RESOURCE_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"

    # Service & System
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"

    # Rate Limiting & Throttling
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"

    # Business Logic
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INVALID_STATE = "INVALID_STATE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"


# HTTP Status Code Mapping
HTTP_STATUS_MAPPING: Dict[CommonErrorCode, int] = {
    # 4xx Client Errors
    CommonErrorCode.AUTHENTICATION_FAILED: 401,
    CommonErrorCode.INVALID_CREDENTIALS: 401,
    CommonErrorCode.TOKEN_EXPIRED: 401,
    CommonErrorCode.TOKEN_INVALID: 401,
    CommonErrorCode.INSUFFICIENT_PERMISSIONS: 403,
    CommonErrorCode.ACCESS_DENIED: 403,
    CommonErrorCode.VALIDATION_ERROR: 422,
    CommonErrorCode.INVALID_INPUT: 422,
    CommonErrorCode.MISSING_REQUIRED_FIELD: 422,
    CommonErrorCode.INVALID_FORMAT: 422,
    CommonErrorCode.RESOURCE_NOT_FOUND: 404,
    CommonErrorCode.RESOURCE_EXISTS: 409,
    CommonErrorCode.RESOURCE_CONFLICT: 409,
    CommonErrorCode.BUSINESS_RULE_VIOLATION: 400,
    CommonErrorCode.INVALID_STATE: 400,
    CommonErrorCode.OPERATION_NOT_ALLOWED: 400,
    CommonErrorCode.RATE_LIMIT_EXCEEDED: 429,
    CommonErrorCode.TOO_MANY_REQUESTS: 429,

    # 5xx Server Errors
    CommonErrorCode.SERVICE_UNAVAILABLE: 503,
    CommonErrorCode.INTERNAL_ERROR: 500,
    CommonErrorCode.DATABASE_ERROR: 503,
    CommonErrorCode.EXTERNAL_SERVICE_ERROR: 502,
}


def get_http_status_code(error_code: CommonErrorCode) -> int:
    """Get HTTP status code for a given error code"""
    return HTTP_STATUS_MAPPING.get(error_code, 500)


# Service-specific error code mappings
# These map service-specific errors to common error codes
SERVICE_ERROR_MAPPING = {
    # User Service specific errors
    "USER_EXISTS": CommonErrorCode.RESOURCE_EXISTS,
    "USER_NOT_FOUND": CommonErrorCode.RESOURCE_NOT_FOUND,
    "EMAIL_EXISTS": CommonErrorCode.RESOURCE_EXISTS,
    "USERNAME_EXISTS": CommonErrorCode.RESOURCE_EXISTS,

    # Inventory Service specific errors
    "ASSET_NOT_FOUND": CommonErrorCode.RESOURCE_NOT_FOUND,
    "ASSET_EXISTS": CommonErrorCode.RESOURCE_EXISTS,

    # Gateway specific errors
    "AUTH_001": CommonErrorCode.TOKEN_INVALID,
    "AUTH_002": CommonErrorCode.TOKEN_EXPIRED,
    "AUTH_003": CommonErrorCode.TOKEN_INVALID,
    "PERM_001": CommonErrorCode.INSUFFICIENT_PERMISSIONS,
    "PERM_002": CommonErrorCode.ACCESS_DENIED,
    "SVC_001": CommonErrorCode.SERVICE_UNAVAILABLE,
    "SVC_002": CommonErrorCode.SERVICE_UNAVAILABLE,
    "SVC_003": CommonErrorCode.SERVICE_UNAVAILABLE,
    "RATE_001": CommonErrorCode.RATE_LIMIT_EXCEEDED,
}


def map_service_error_to_common(service_error_code: str) -> CommonErrorCode:
    """Map service-specific error codes to common error codes"""
    return SERVICE_ERROR_MAPPING.get(service_error_code, CommonErrorCode.INTERNAL_ERROR)