"""
Shared API Response Descriptions - Only truly shared across multiple services
"""
from enum import Enum


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
