"""
Common exception handling package for all services
Path: services/common/src/exceptions/__init__.py
"""

from .internal_exceptions import (
    # Internal exceptions for detailed logging
    InternalCommonError,
    InternalDatabaseConnectionError,
    InternalDatabaseOperationError,
    InternalConfigurationError,
    InternalEntityValidationError,
    InternalAWSError,
    InternalEntityAlreadyExistsError,
    InternalEntityNotFoundError,
    InternalBusinessRuleError
)

__all__ = [
    # Internal exceptions only
    "InternalCommonError",
    "InternalDatabaseConnectionError",
    "InternalDatabaseOperationError",
    "InternalConfigurationError",
    "InternalEntityValidationError",
    "InternalAWSError",
    "InternalEntityAlreadyExistsError",
    "InternalEntityNotFoundError",
    "InternalBusinessRuleError"
]