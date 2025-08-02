"""
Common exceptions package

This package provides two types of exceptions:
1. Shared exceptions - for business logic across all services
2. Common exceptions - for common package/component only
"""

from .base_exception import BaseInternalException

# Import shared exceptions (mapped to external error codes)
from .shared_exceptions import (
    SharedException,
    # Authentication exceptions
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    # Authorization exceptions
    AuthorizationException,
    AccessDeniedException,
    InsufficientPermissionsException,
    # Resource exceptions
    EntityNotFoundException,
    EntityAlreadyExistsException,
    UserNotFoundException,
    OrderNotFoundException,
    AssetNotFoundException,
    # Validation exceptions
    EntityValidationException,
    UserValidationException,
    OrderValidationException,
    AssetValidationException,
    # Internal server exception
    InternalServerException,
)

# Import common exceptions (handled internally, NOT mapped)
from .exceptions import (
    CommonException,
    # Database exceptions
    DatabaseConnectionException,
    DatabaseOperationException,
    # Configuration exceptions
    ConfigurationException,
    # External service exceptions
    AWSServiceException,
    ExternalServiceException,
    # Locking exceptions
    LockAcquisitionException,
    LockTimeoutException,
    # Generic common server exception
    CommonServerException,
)

__all__ = [
    # Base exception
    "BaseInternalException",

    # Shared exceptions (mapped to external error codes)
    "SharedException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "AuthorizationException",
    "AccessDeniedException",
    "InsufficientPermissionsException",
    "EntityNotFoundException",
    "EntityAlreadyExistsException",
    "UserNotFoundException",
    "OrderNotFoundException",
    "AssetNotFoundException",
    "EntityValidationException",
    "UserValidationException",
    "OrderValidationException",
    "AssetValidationException",
    "InternalServerException",

    # Common exceptions (handled internally, NOT mapped)
    "CommonException",
    "DatabaseConnectionException",
    "DatabaseOperationException",
    "ConfigurationException",
    "AWSServiceException",
    "ExternalServiceException",
    "LockAcquisitionException",
    "LockTimeoutException",
    "CommonServerException",
]