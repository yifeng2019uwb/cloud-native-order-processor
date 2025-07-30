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
    UserNotFoundException,
    InvalidCredentialsException,
    TokenExpiredException,
    raise_user_exists,
    raise_database_error,
    raise_validation_error,
    # Common package exception wrappers
    wrap_common_database_connection_error,
    wrap_common_database_operation_error,
    wrap_common_entity_already_exists_error,
    wrap_common_entity_validation_error,
    wrap_common_configuration_error,
    wrap_common_aws_error
)

# Import secure exception handlers
from .secure_exceptions import (
    secure_internal_exception_handler,
    secure_validation_exception_handler,
    secure_general_exception_handler,
    StandardErrorResponse,
    SecureExceptionMapper,
    # Single generic handler for all common package exceptions
    secure_common_exception_handler
)

__all__ = [
    # Internal exceptions
    "InternalAuthError",
    "InternalUserExistsError",
    "InternalDatabaseError",
    "InternalValidationError",
    "UserNotFoundException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "raise_user_exists",
    "raise_database_error",
    "raise_validation_error",

    # Common package exception wrappers
    "wrap_common_database_connection_error",
    "wrap_common_database_operation_error",
    "wrap_common_entity_already_exists_error",
    "wrap_common_entity_validation_error",
    "wrap_common_configuration_error",
    "wrap_common_aws_error",

    # Secure exception handlers
    "secure_internal_exception_handler",
    "secure_validation_exception_handler",
    "secure_general_exception_handler",
    "StandardErrorResponse",
    "SecureExceptionMapper",

    # Single generic handler for all common package exceptions
    "secure_common_exception_handler"
]