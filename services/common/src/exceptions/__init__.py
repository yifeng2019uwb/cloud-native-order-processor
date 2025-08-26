"""
Common exceptions package

This package provides CNOP prefixed exceptions for the common package.
All exceptions use the CNOP prefix to avoid naming conflicts and provide clear ownership.

IMPORTANT: Only truly cross-service exceptions and internal data exceptions are provided here.
Service-specific validation exceptions should be imported from their respective services.
"""

from .base_exception import CNOPException, CNOPInternalException, CNOPClientException

# Import shared exceptions (mapped to external error codes)
from .shared_exceptions import (
    # Authentication exceptions
    CNOPInvalidCredentialsException,
    CNOPTokenExpiredException,
    CNOPTokenInvalidException,
    # Authorization exceptions
    CNOPAuthorizationException,
    CNOPAccessDeniedException,
    CNOPInsufficientPermissionsException,
    # Resource exceptions
    CNOPEntityNotFoundException,
    CNOPEntityAlreadyExistsException,
    CNOPUserNotFoundException,
    CNOPOrderNotFoundException,
    CNOPAssetNotFoundException,
    CNOPBalanceNotFoundException,
    CNOPAssetBalanceNotFoundException,
    CNOPTransactionNotFoundException,
    # Business logic exceptions
    CNOPInsufficientBalanceException,
    # Internal server exception
    CNOPInternalServerException,
)

# Import data exceptions (internal infrastructure only)
from .exceptions import (
    # Database exceptions
    CNOPDatabaseConnectionException,
    CNOPDatabaseOperationException,
    # Configuration exceptions
    CNOPConfigurationException,
    # External service exceptions
    CNOPAWSServiceException,
    CNOPExternalServiceException,
    # Locking exceptions
    CNOPLockAcquisitionException,
    CNOPLockTimeoutException,
    # Generic validation exception (internal data validation only)
    CNOPEntityValidationException,
    # Generic common server exception
    CNOPCommonServerException,
)

__all__ = [
    # Base exceptions
    "CNOPException",
    "CNOPInternalException",
    "CNOPClientException",

    # Shared exceptions (mapped to external error codes)
    "CNOPInvalidCredentialsException",
    "CNOPTokenExpiredException",
    "CNOPTokenInvalidException",
    "CNOPAuthorizationException",
    "CNOPAccessDeniedException",
    "CNOPInsufficientPermissionsException",
    "CNOPEntityNotFoundException",
    "CNOPEntityAlreadyExistsException",
    "CNOPUserNotFoundException",
    "CNOPOrderNotFoundException",
    "CNOPAssetNotFoundException",
    "CNOPBalanceNotFoundException",
    "CNOPAssetBalanceNotFoundException",
    "CNOPTransactionNotFoundException",
    "CNOPInsufficientBalanceException",
    "CNOPInternalServerException",

    # Data exceptions (internal infrastructure only)
    "CNOPDatabaseConnectionException",
    "CNOPDatabaseOperationException",
    "CNOPConfigurationException",
    "CNOPAWSServiceException",
    "CNOPExternalServiceException",
    "CNOPLockAcquisitionException",
    "CNOPLockTimeoutException",
    "CNOPEntityValidationException",
    "CNOPCommonServerException",
]