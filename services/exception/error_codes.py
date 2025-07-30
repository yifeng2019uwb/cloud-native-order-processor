"""
Error Codes for RFC 7807 Problem Details

Defines standard error codes and their HTTP status mappings
for consistent error handling across all services.
"""

from enum import Enum
from typing import Dict


class ErrorCode(str, Enum):
    """Standard error codes for the Order Processor system"""

    # Validation Errors (422)
    VALIDATION_ERROR = "validation_error"
    INVALID_INPUT = "invalid_input"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_FORMAT = "invalid_format"

    # Authentication Errors (401)
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    MISSING_TOKEN = "missing_token"

    # Authorization Errors (403)
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    ACCESS_DENIED = "access_denied"

    # Resource Errors (404, 409)
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_ALREADY_EXISTS = "resource_already_exists"
    USER_NOT_FOUND = "user_not_found"
    ASSET_NOT_FOUND = "asset_not_found"
    USERNAME_TAKEN = "username_taken"
    EMAIL_TAKEN = "email_taken"

    # Server Errors (500) - Simplified to avoid internal details
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


# HTTP Status Code Mapping - Simplified for external consumption
HTTP_STATUS_MAPPING: Dict[ErrorCode, int] = {
    # Validation Errors
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.INVALID_INPUT: 422,
    ErrorCode.MISSING_REQUIRED_FIELD: 422,
    ErrorCode.INVALID_FORMAT: 422,

    # Authentication Errors
    ErrorCode.AUTHENTICATION_FAILED: 401,
    ErrorCode.INVALID_CREDENTIALS: 401,
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.TOKEN_INVALID: 401,
    ErrorCode.MISSING_TOKEN: 401,

    # Authorization Errors
    ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
    ErrorCode.ACCESS_DENIED: 403,

    # Resource Errors
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.USER_NOT_FOUND: 404,
    ErrorCode.ASSET_NOT_FOUND: 404,
    ErrorCode.RESOURCE_ALREADY_EXISTS: 409,
    ErrorCode.USERNAME_TAKEN: 409,
    ErrorCode.EMAIL_TAKEN: 409,

    # Server Errors - All internal errors map to 500
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}


def get_http_status_code(error_code: ErrorCode) -> int:
    """Get HTTP status code for an error code"""
    return HTTP_STATUS_MAPPING.get(error_code, 500)


def get_error_title(error_code: ErrorCode) -> str:
    """Get human-readable title for an error code"""
    title_mapping = {
        ErrorCode.VALIDATION_ERROR: "Validation Error",
        ErrorCode.INVALID_INPUT: "Invalid Input",
        ErrorCode.MISSING_REQUIRED_FIELD: "Missing Required Field",
        ErrorCode.INVALID_FORMAT: "Invalid Format",
        ErrorCode.AUTHENTICATION_FAILED: "Authentication Error",
        ErrorCode.INVALID_CREDENTIALS: "Invalid Credentials",
        ErrorCode.TOKEN_EXPIRED: "Token Expired",
        ErrorCode.TOKEN_INVALID: "Invalid Token",
        ErrorCode.MISSING_TOKEN: "Missing Token",
        ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient Permissions",
        ErrorCode.ACCESS_DENIED: "Access Denied",
        ErrorCode.RESOURCE_NOT_FOUND: "Resource Not Found",
        ErrorCode.USER_NOT_FOUND: "User Not Found",
        ErrorCode.ASSET_NOT_FOUND: "Asset Not Found",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource Already Exists",
        ErrorCode.USERNAME_TAKEN: "Username Already Taken",
        ErrorCode.EMAIL_TAKEN: "Email Already Taken",
        ErrorCode.INTERNAL_SERVER_ERROR: "Internal Server Error",
        ErrorCode.SERVICE_UNAVAILABLE: "Service Unavailable",
    }
    return title_mapping.get(error_code, "Unknown Error")


def get_error_detail(error_code: ErrorCode) -> str:
    """Get human-readable detail message for an error code"""
    detail_mapping = {
        ErrorCode.VALIDATION_ERROR: "The provided data is invalid",
        ErrorCode.INVALID_INPUT: "Invalid input provided",
        ErrorCode.MISSING_REQUIRED_FIELD: "Required field is missing",
        ErrorCode.INVALID_FORMAT: "Data format is invalid",
        ErrorCode.AUTHENTICATION_FAILED: "Authentication failed",
        ErrorCode.INVALID_CREDENTIALS: "Invalid username or password",
        ErrorCode.TOKEN_EXPIRED: "Authentication token has expired",
        ErrorCode.TOKEN_INVALID: "Invalid authentication token",
        ErrorCode.MISSING_TOKEN: "Authentication token is required",
        ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions to access this resource",
        ErrorCode.ACCESS_DENIED: "Access to this resource is denied",
        ErrorCode.RESOURCE_NOT_FOUND: "The requested resource was not found",
        ErrorCode.USER_NOT_FOUND: "User not found",
        ErrorCode.ASSET_NOT_FOUND: "Asset not found",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "A resource with this identifier already exists",
        ErrorCode.USERNAME_TAKEN: "Username is already taken",
        ErrorCode.EMAIL_TAKEN: "Email address is already registered",
        ErrorCode.INTERNAL_SERVER_ERROR: "An unexpected error occurred",
        ErrorCode.SERVICE_UNAVAILABLE: "Service is temporarily unavailable",
    }
    return detail_mapping.get(error_code, "An unknown error occurred")