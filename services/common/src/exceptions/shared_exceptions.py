"""
Shared exceptions for all services
Path: services/common/src/exceptions/shared_exceptions.py

These exceptions are shared across all services and get mapped to external error codes.
They represent business logic exceptions that can be exposed to clients.

IMPORTANT: Only truly cross-service exceptions should be here.
Service-specific validation exceptions should be in their respective services.
"""

from .base_exception import CNOPClientException

# ========================================
# AUTHENTICATION EXCEPTIONS (401 scenarios)
# ========================================

class CNOPInvalidCredentialsException(CNOPClientException):
    """Invalid credentials exception - CNOP version"""
    pass


class CNOPTokenExpiredException(CNOPClientException):
    """Token expired exception - CNOP version"""
    pass


class CNOPTokenInvalidException(CNOPClientException):
    """Token invalid/malformed exception - CNOP version"""
    pass


# ========================================
# AUTHORIZATION EXCEPTIONS (403 scenarios)
# ========================================

class CNOPAuthorizationException(CNOPClientException):
    """Authorization/permission exception - CNOP version"""
    pass


class CNOPAccessDeniedException(CNOPClientException):
    """Access denied exception - CNOP version"""
    pass


class CNOPInsufficientPermissionsException(CNOPClientException):
    """Insufficient permissions exception - CNOP version"""
    pass


# ========================================
# RESOURCE EXCEPTIONS (404, 409 scenarios)
# ========================================

class CNOPEntityNotFoundException(CNOPClientException):
    """Generic entity not found exception - CNOP version"""
    pass


class CNOPEntityAlreadyExistsException(CNOPClientException):
    """Entity already exists exception - CNOP version"""
    pass


class CNOPUserNotFoundException(CNOPClientException):
    """User not found exception - CNOP version"""
    pass


class CNOPOrderNotFoundException(CNOPClientException):
    """Order not found exception - CNOP version"""
    pass


class CNOPAssetNotFoundException(CNOPClientException):
    """Asset not found exception - CNOP version"""
    pass


class CNOPBalanceNotFoundException(CNOPClientException):
    """Balance not found exception - CNOP version"""
    pass


class CNOPAssetBalanceNotFoundException(CNOPClientException):
    """Asset balance not found exception - CNOP version"""
    pass


class CNOPTransactionNotFoundException(CNOPClientException):
    """Transaction not found exception - CNOP version"""
    pass


# ========================================
# BUSINESS LOGIC EXCEPTIONS (400 scenarios)
# ========================================

class CNOPInsufficientBalanceException(CNOPClientException):
    """Insufficient balance exception - CNOP version"""
    pass


# ========================================
# INTERNAL SERVER EXCEPTIONS (500 scenarios)
# ========================================

class CNOPInternalServerException(CNOPClientException):
    """Internal server exception - CNOP version"""
    pass


__all__ = [
    # Authentication exceptions (401)
    "CNOPInvalidCredentialsException",
    "CNOPTokenExpiredException",
    "CNOPTokenInvalidException",

    # Authorization exceptions (403)
    "CNOPAuthorizationException",
    "CNOPAccessDeniedException",
    "CNOPInsufficientPermissionsException",

    # Resource exceptions (404, 409)
    "CNOPEntityNotFoundException",
    "CNOPEntityAlreadyExistsException",
    "CNOPUserNotFoundException",
    "CNOPOrderNotFoundException",
    "CNOPAssetNotFoundException",
    "CNOPBalanceNotFoundException",
    "CNOPAssetBalanceNotFoundException",
    "CNOPTransactionNotFoundException",

    # Business logic exceptions (400)
    "CNOPInsufficientBalanceException",

    # Internal server exceptions (500)
    "CNOPInternalServerException",
]