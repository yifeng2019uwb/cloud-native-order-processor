"""
Centralized Error Messages and Default Values for all services
"""


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
