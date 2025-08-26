"""
Common exceptions package

This package provides CNOP prefixed exceptions for the common package.
All exceptions use the CNOP prefix to avoid naming conflicts and provide clear ownership.

IMPORTANT: Only truly cross-service exceptions and internal data exceptions are provided here.
Service-specific validation exceptions should be imported from their respective services.

⚠️  DEPRECATION WARNING ⚠️
Authentication exceptions are now provided via the auth package:
    from common.auth.exceptions import CNOPAuthTokenExpiredException  # ✅ NEW
    from common.exceptions import CNOPTokenExpiredException          # ❌ DEPRECATED

The old authentication exceptions are provided as aliases for backward compatibility
but will be removed once all services are migrated to the new package structure.
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
# BACKWARD COMPATIBILITY ALIASES - DEPRECATED - USE NEW AUTH PACKAGE INSTEAD
# =============================================================================
#
# IMPORTANT: These aliases are provided for backward compatibility during migration.
# DO NOT use these in new code. Import from the appropriate package instead:
#
# ✅ CORRECT (new code):
#   from common.auth.exceptions import CNOPAuthTokenExpiredException
#   from common.auth.exceptions import CNOPAuthTokenInvalidException
#
# ❌ DEPRECATED (old code - will be removed):
#   from common.exceptions import CNOPTokenExpiredException
#   from common.exceptions import CNOPTokenInvalidException
#
# Migration Plan:
# 1. Update all services to use new package paths (common.auth.exceptions.*)
# 2. Remove these aliases once all services are migrated
# 3. Keep only the new auth package exceptions going forward
# =============================================================================

# Authentication exceptions - DEPRECATED ALIASES
from ..auth.exceptions import (
    CNOPAuthTokenExpiredException as CNOPTokenExpiredException,
    CNOPAuthTokenInvalidException as CNOPTokenInvalidException,
    CNOPAuthInvalidCredentialsException as CNOPInvalidCredentialsException,
    CNOPAuthAuthorizationException as CNOPAuthorizationException,
    CNOPAuthAccessDeniedException as CNOPAccessDeniedException,
    CNOPAuthInsufficientPermissionsException as CNOPInsufficientPermissionsException,
)

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
    # BACKWARD COMPATIBILITY ALIASES - DEPRECATED - USE NEW AUTH PACKAGE INSTEAD
    # =============================================================================
    # These aliases are provided for backward compatibility during migration.
    # DO NOT use these in new code. Import from common.auth.exceptions instead.
    # =============================================================================

    # Authentication exceptions - DEPRECATED ALIASES
    "CNOPInvalidCredentialsException",      # Use CNOPAuthInvalidCredentialsException instead
    "CNOPTokenExpiredException",           # Use CNOPAuthTokenExpiredException instead
    "CNOPTokenInvalidException",           # Use CNOPAuthTokenInvalidException instead
    "CNOPAuthorizationException",          # Use CNOPAuthAuthorizationException instead
    "CNOPAccessDeniedException",           # Use CNOPAuthAccessDeniedException instead
    "CNOPInsufficientPermissionsException", # Use CNOPAuthInsufficientPermissionsException instead
]