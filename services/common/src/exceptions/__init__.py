"""
Common exception handling package for all services
Path: services/common/src/exceptions/__init__.py
"""

from .error_codes import (
    CommonErrorCode,
    HTTP_STATUS_MAPPING,
    get_http_status_code
)

from .error_models import (
    ErrorResponse,
    ValidationError,
    ErrorDetails,
    create_error_response,
    create_validation_error_response
)

from .exception_handlers import (
    CommonExceptionHandler,
    handle_validation_error,
    handle_internal_error,
    handle_http_error
)

__all__ = [
    # Error codes
    "CommonErrorCode",
    "HTTP_STATUS_MAPPING",
    "get_http_status_code",

    # Error models
    "ErrorResponse",
    "ValidationError",
    "ErrorDetails",
    "create_error_response",
    "create_validation_error_response",

    # Exception handlers
    "CommonExceptionHandler",
    "handle_validation_error",
    "handle_internal_error",
    "handle_http_error"
]