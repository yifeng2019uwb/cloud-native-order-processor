"""
Common exception handling package for all services
Path: services/common/src/exceptions/__init__.py
"""

from .internal_exceptions import (
    # Common package exceptions for detailed logging
    CommonError,
    DatabaseConnectionError,
    DatabaseOperationError,
    ConfigurationError,
    EntityValidationError,
    AWSError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    BusinessRuleError
)

__all__ = [
    # Common package exceptions only
    "CommonError",
    "DatabaseConnectionError",
    "DatabaseOperationError",
    "ConfigurationError",
    "EntityValidationError",
    "AWSError",
    "EntityAlreadyExistsError",
    "EntityNotFoundError",
    "BusinessRuleError"
]