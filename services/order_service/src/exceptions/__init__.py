"""
Order service exceptions package
Path: services/order_service/src/exceptions/__init__.py
"""

# Internal exceptions for detailed logging
from .internal_exceptions import (
    InternalOrderError,
    InternalOrderNotFoundError,
    InternalOrderExistsError,
    InternalOrderValidationError,
    InternalOrderStatusError,
    InternalDatabaseError,
    # Helper functions
    raise_order_not_found,
    raise_order_exists,
    raise_order_validation_error,
    raise_order_status_error,
    raise_database_error
)

# Secure exception handling
from .secure_exceptions import (
    StandardErrorResponse,
    SecureExceptionMapper,
    # Exception handlers
    secure_internal_exception_handler,
    secure_common_exception_handler,
    secure_validation_exception_handler,
    secure_general_exception_handler
)

__all__ = [
    # Internal exceptions
    "InternalOrderError",
    "InternalOrderNotFoundError",
    "InternalOrderExistsError",
    "InternalOrderValidationError",
    "InternalOrderStatusError",
    "InternalDatabaseError",
    # Helper functions
    "raise_order_not_found",
    "raise_order_exists",
    "raise_order_validation_error",
    "raise_order_status_error",
    "raise_database_error",
    # Secure exception handling
    "StandardErrorResponse",
    "SecureExceptionMapper",
    # Exception handlers
    "secure_internal_exception_handler",
    "secure_common_exception_handler",
    "secure_validation_exception_handler",
    "secure_general_exception_handler"
]
