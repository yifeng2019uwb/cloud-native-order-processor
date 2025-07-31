"""
Error Codes for RFC 7807 Problem Details

Defines standard error codes and their HTTP status mappings
for consistent error handling across all services.
"""

from enum import Enum
from typing import Dict


class ErrorCode(str, Enum):
    """Standard error codes for the Order Processor system"""

    # Authentication Errors (401)
    AUTHENTICATION_FAILED = "authentication_failed"

    # Authorization Errors (403)
    ACCESS_DENIED = "access_denied"

    # Resource Errors (404, 409)
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_ALREADY_EXISTS = "resource_already_exists"

    # Validation Errors (422)
    VALIDATION_ERROR = "validation_error"

    # Server Errors (500, 503)
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


# HTTP Status Code Mapping - Simplified for external consumption
HTTP_STATUS_MAPPING: Dict[ErrorCode, int] = {
    # Authentication Errors
    ErrorCode.AUTHENTICATION_FAILED: 401,

    # Authorization Errors
    ErrorCode.ACCESS_DENIED: 403,

    # Resource Errors
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.RESOURCE_ALREADY_EXISTS: 409,

    # Validation Errors
    ErrorCode.VALIDATION_ERROR: 422,

    # Server Errors
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}


def get_http_status_code(error_code: ErrorCode) -> int:
    """Get HTTP status code for an error code"""
    return HTTP_STATUS_MAPPING.get(error_code, 500)


def get_error_title(error_code: ErrorCode) -> str:
    """Get human-readable title for an error code"""
    title_mapping = {
        ErrorCode.AUTHENTICATION_FAILED: "Authentication Error",
        ErrorCode.ACCESS_DENIED: "Access Denied",
        ErrorCode.RESOURCE_NOT_FOUND: "Resource Not Found",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource Already Exists",
        ErrorCode.VALIDATION_ERROR: "Validation Error",
        ErrorCode.INTERNAL_SERVER_ERROR: "Internal Server Error",
        ErrorCode.SERVICE_UNAVAILABLE: "Service Unavailable",
    }
    return title_mapping.get(error_code, "Unknown Error")


def get_error_detail(error_code: ErrorCode) -> str:
    """Get human-readable detail message for an error code"""
    detail_mapping = {
        ErrorCode.AUTHENTICATION_FAILED: "Authentication failed. Please check your credentials and try again.",
        ErrorCode.ACCESS_DENIED: "Access denied. You don't have permission to perform this action.",
        ErrorCode.RESOURCE_NOT_FOUND: "The requested resource was not found.",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "The resource already exists.",
        ErrorCode.VALIDATION_ERROR: "The request contains invalid data. Please check your input and try again.",
        ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred. Please try again later.",
        ErrorCode.SERVICE_UNAVAILABLE: "The service is temporarily unavailable. Please try again later.",
    }
    return detail_mapping.get(error_code, "An unexpected error occurred.")