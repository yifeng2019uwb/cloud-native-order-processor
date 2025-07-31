"""
Exception handling package for RFC 7807 Problem Details

This package provides standardized exception handling for all services,
mapping internal exceptions to external RFC 7807 Problem Details responses.
"""

from .error_codes import ErrorCode, get_http_status_code, get_error_title, get_error_detail
from .error_models import ProblemDetails, create_problem_details
from .exception_mapping import (
    exception_mapper,
    configure_service_exceptions,
    map_validation_error,
    map_service_exception
)
from .exception_handlers import (
    handle_validation_error,
    handle_http_exception,
    handle_general_exception,
    register_exception_handlers
)

__all__ = [
    # Error codes
    "ErrorCode",
    "get_http_status_code",
    "get_error_title",
    "get_error_detail",

    # Problem details models
    "ProblemDetails",
    "create_problem_details",

    # Exception mapping
    "exception_mapper",
    "configure_service_exceptions",
    "map_validation_error",
    "map_service_exception",

    # Exception handlers
    "handle_validation_error",
    "handle_http_exception",
    "handle_general_exception",
    "register_exception_handlers",
]

__version__ = "1.0.0"