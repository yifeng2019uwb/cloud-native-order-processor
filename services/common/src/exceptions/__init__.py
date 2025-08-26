"""
Common exceptions package

This package provides two types of exceptions:
1. Shared exceptions - for business logic across all services
2. Common exceptions - for common package/component only

NEW: CNOP prefixed exceptions for gradual migration
EXISTING: Current exceptions (to be deprecated after migration)
"""

from .base_exception import BaseInternalException, CNOPException, CNOPInternalException, CNOPClientException

# Import shared exceptions (mapped to external error codes)
from .shared_exceptions import (
    SharedException,
    # Authentication exceptions
    InvalidCredentialsException,
    CNOPInvalidCredentialsException,
    TokenExpiredException,
    CNOPTokenExpiredException,
    TokenInvalidException,
    CNOPTokenInvalidException,
    # Authorization exceptions
    AuthorizationException,
    CNOPAuthorizationException,
    AccessDeniedException,
    CNOPAccessDeniedException,
    InsufficientPermissionsException,
    CNOPInsufficientPermissionsException,
    # Resource exceptions
    EntityNotFoundException,
    CNOPEntityNotFoundException,
    EntityAlreadyExistsException,
    CNOPEntityAlreadyExistsException,
    UserNotFoundException,
    CNOPUserNotFoundException,
    OrderNotFoundException,
    CNOPOrderNotFoundException,
    AssetNotFoundException,
    CNOPAssetNotFoundException,
    BalanceNotFoundException,
    CNOPBalanceNotFoundException,
    AssetBalanceNotFoundException,
    CNOPAssetBalanceNotFoundException,
    TransactionNotFoundException,
    CNOPTransactionNotFoundException,
    # Validation exceptions
    EntityValidationException,
    CNOPEntityValidationException,
    UserValidationException,
    CNOPUserValidationException,
    OrderValidationException,
    CNOPOrderValidationException,
    AssetValidationException,
    CNOPAssetValidationException,
    # Internal server exception
    InternalServerException,
    CNOPInternalServerException,
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
    # Business logic exceptions
    InsufficientBalanceException,
    # Generic common server exception
    CommonServerException,
)

__all__ = [
    # Base exceptions
    "BaseInternalException",
    "CNOPException",
    "CNOPInternalException",
    "CNOPClientException",

    # Shared exceptions (mapped to external error codes)
    "SharedException",
    "InvalidCredentialsException",
    "CNOPInvalidCredentialsException",
    "TokenExpiredException",
    "CNOPTokenExpiredException",
    "TokenInvalidException",
    "CNOPTokenInvalidException",
    "AuthorizationException",
    "CNOPAuthorizationException",
    "AccessDeniedException",
    "CNOPAccessDeniedException",
    "InsufficientPermissionsException",
    "CNOPInsufficientPermissionsException",
    "EntityNotFoundException",
    "CNOPEntityNotFoundException",
    "EntityAlreadyExistsException",
    "CNOPEntityAlreadyExistsException",
    "UserNotFoundException",
    "CNOPUserNotFoundException",
    "OrderNotFoundException",
    "CNOPOrderNotFoundException",
    "AssetNotFoundException",
    "CNOPAssetNotFoundException",
    "BalanceNotFoundException",
    "CNOPBalanceNotFoundException",
    "AssetBalanceNotFoundException",
    "CNOPAssetBalanceNotFoundException",
    "TransactionNotFoundException",
    "CNOPTransactionNotFoundException",
    "EntityValidationException",
    "CNOPEntityValidationException",
    "UserValidationException",
    "CNOPUserValidationException",
    "OrderValidationException",
    "CNOPOrderValidationException",
    "AssetValidationException",
    "CNOPAssetValidationException",
    "InternalServerException",
    "CNOPInternalServerException",

    # Common exceptions (handled internally, NOT mapped)
    "CommonException",
    "DatabaseConnectionException",
    "DatabaseOperationException",
    "ConfigurationException",
    "AWSServiceException",
    "ExternalServiceException",
    "LockAcquisitionException",
    "LockTimeoutException",
    "InsufficientBalanceException",
    "CommonServerException",
]