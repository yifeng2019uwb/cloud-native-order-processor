"""
Common exceptions package

This package provides CNOP prefixed exceptions for the common package.
All exceptions use the CNOP prefix to avoid naming conflicts and provide clear ownership.

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

# =============================================================================
# JWT EXCEPTIONS REMOVED - NO LONGER NEEDED IN BACKEND SERVICES
# =============================================================================
#
# These JWT-related exceptions have been removed to complete SEC-005 Phase 3.
# Backend services no longer need JWT validation and should use appropriate
# non-JWT exceptions instead.
#
# If JWT exceptions are needed, import directly from common.auth.exceptions:
#   from common.auth.exceptions import CNOPAuthTokenExpiredException
#   from common.auth.exceptions import CNOPAuthTokenInvalidException
# =============================================================================

__all__ = [
    # Base exceptions
    "CNOPException",
    "CNOPInternalException",
    "CNOPClientException",

    # Shared exceptions (mapped to external error codes)
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

    # =============================================================================
    # JWT EXCEPTIONS REMOVED - NO LONGER NEEDED IN BACKEND SERVICES
    # =============================================================================
    # These JWT-related exceptions have been removed to complete SEC-005 Phase 3.
    # Backend services no longer need JWT validation and should use appropriate
    # non-JWT exceptions instead.
    # =============================================================================
]