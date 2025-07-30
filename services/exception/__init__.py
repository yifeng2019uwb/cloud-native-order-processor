"""
Standardized Exception Handling Package

This package provides RFC 7807 Problem Details compliant error handling
for all services in the Order Processor system.

RFC 7807: https://tools.ietf.org/html/rfc7807
"""

from .error_codes import ErrorCode, HTTP_STATUS_MAPPING
from .error_models import (
    ProblemDetails,
    ValidationError,
    ErrorDetails,
    create_validation_error,
    create_problem_details
)
from .exception_handlers import (
    ExceptionHandler,
    handle_validation_error,
    handle_authentication_error,
    handle_resource_not_found,
    handle_resource_exists,
    handle_internal_error
)
from .exception_mapping import (
    ExceptionMapper,
    exception_mapper,
    map_service_exception,
    map_database_exception
)

__all__ = [
    # Error codes
    'ErrorCode',
    'HTTP_STATUS_MAPPING',

    # Error models
    'ProblemDetails',
    'ValidationError',
    'ErrorDetails',
    'create_validation_error',
    'create_problem_details',

    # Exception handlers
    'ExceptionHandler',
    'handle_validation_error',
    'handle_authentication_error',
    'handle_resource_not_found',
    'handle_resource_exists',
    'handle_internal_error',

    # Exception mapping
    'ExceptionMapper',
    'exception_mapper',
    'map_service_exception',
    'map_database_exception'
]

__version__ = "1.0.0"