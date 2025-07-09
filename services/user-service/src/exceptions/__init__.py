"""
Exception handling package for user authentication service
Path: cloud-native-order-processor/services/user-service/src/exceptions/__init__.py
"""

# Import internal exceptions
from .internal_exceptions import (
    InternalAuthError,
    InternalUserExistsError,
    InternalDatabaseError,
    InternalValidationError,
    raise_user_exists,
    raise_database_error,
    raise_validation_error
)

# Import secure exception handlers
from .secure_exceptions import (
    secure_internal_exception_handler,
    secure_validation_exception_handler,
    secure_general_exception_handler,
    StandardErrorResponse,
    SecureExceptionMapper
)

__all__ = [
    # Internal exceptions
    "InternalAuthError",
    "InternalUserExistsError",
    "InternalDatabaseError",
    "InternalValidationError",
    "raise_user_exists",
    "raise_database_error",
    "raise_validation_error",

    # Secure exception handlers
    "secure_internal_exception_handler",
    "secure_validation_exception_handler",
    "secure_general_exception_handler",
    "StandardErrorResponse",
    "SecureExceptionMapper"
]