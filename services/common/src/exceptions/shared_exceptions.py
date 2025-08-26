"""
Shared exceptions for all services
Path: services/common/src/exceptions/shared_exceptions.py

These exceptions are shared across all services and get mapped to external error codes.
They represent business logic exceptions that can be exposed to clients.

NEW: CNOP prefixed exceptions for gradual migration
EXISTING: Current exceptions (to be deprecated after migration)
"""

from .base_exception import BaseInternalException, CNOPClientException


class SharedException(BaseInternalException):
    """Base class for shared exceptions that get mapped to external error codes"""
    pass


# ========================================
# AUTHENTICATION EXCEPTIONS (401 scenarios)
# ========================================

class InvalidCredentialsException(SharedException):
    """Invalid credentials exception"""
    pass


class CNOPInvalidCredentialsException(CNOPClientException):
    """Invalid credentials exception - CNOP version"""
    pass


class TokenExpiredException(SharedException):
    """Token expired exception"""
    pass


class CNOPTokenExpiredException(CNOPClientException):
    """Token expired exception - CNOP version"""
    pass


class TokenInvalidException(SharedException):
    """Token invalid/malformed exception"""
    pass


class CNOPTokenInvalidException(CNOPClientException):
    """Token invalid/malformed exception - CNOP version"""
    pass


# ========================================
# AUTHORIZATION EXCEPTIONS (403 scenarios)
# ========================================

class AuthorizationException(SharedException):
    """Authorization/permission exception"""
    pass


class CNOPAuthorizationException(CNOPClientException):
    """Authorization/permission exception - CNOP version"""
    pass


class AccessDeniedException(SharedException):
    """Access denied exception"""
    pass


class CNOPAccessDeniedException(CNOPClientException):
    """Access denied exception - CNOP version"""
    pass


class InsufficientPermissionsException(SharedException):
    """Insufficient permissions exception"""
    pass


class CNOPInsufficientPermissionsException(CNOPClientException):
    """Insufficient permissions exception - CNOP version"""
    pass


# ========================================
# RESOURCE EXCEPTIONS (404, 409 scenarios)
# ========================================

class EntityNotFoundException(SharedException):
    """Generic entity not found exception"""
    pass


class CNOPEntityNotFoundException(CNOPClientException):
    """Generic entity not found exception - CNOP version"""
    pass


class EntityAlreadyExistsException(SharedException):
    """Generic entity already exists exception"""
    pass


class CNOPEntityAlreadyExistsException(CNOPClientException):
    """Generic entity already exists exception - CNOP version"""
    pass


class UserNotFoundException(SharedException):
    """User not found exception"""
    pass


class CNOPUserNotFoundException(CNOPClientException):
    """User not found exception - CNOP version"""
    pass


class OrderNotFoundException(SharedException):
    """Order not found exception"""
    pass


class CNOPOrderNotFoundException(CNOPClientException):
    """Order not found exception - CNOP version"""
    pass


class AssetNotFoundException(SharedException):
    """Asset not found exception"""
    pass


class CNOPAssetNotFoundException(CNOPClientException):
    """Asset not found exception - CNOP version"""
    pass


class BalanceNotFoundException(SharedException):
    """Balance not found exception"""
    pass


class CNOPBalanceNotFoundException(CNOPClientException):
    """Balance not found exception - CNOP version"""
    pass


class AssetBalanceNotFoundException(SharedException):
    """Asset balance not found exception"""
    pass


class CNOPAssetBalanceNotFoundException(CNOPClientException):
    """Asset balance not found exception - CNOP version"""
    pass


class TransactionNotFoundException(SharedException):
    """Transaction not found exception"""
    pass


class CNOPTransactionNotFoundException(CNOPClientException):
    """Transaction not found exception - CNOP version"""
    pass


# ========================================
# VALIDATION EXCEPTIONS (422 scenarios)
# ========================================

class EntityValidationException(SharedException):
    """Generic entity validation exception"""
    pass


class CNOPEntityValidationException(CNOPClientException):
    """Generic entity validation exception - CNOP version"""
    pass


class UserValidationException(SharedException):
    """User-specific validation exception"""
    pass


class CNOPUserValidationException(CNOPClientException):
    """User-specific validation exception - CNOP version"""
    pass


class OrderValidationException(SharedException):
    """Order-specific validation exception"""
    pass


class CNOPOrderValidationException(CNOPClientException):
    """Order-specific validation exception - CNOP version"""
    pass


class AssetValidationException(SharedException):
    """Asset-specific validation exception"""
    pass


class CNOPAssetValidationException(CNOPClientException):
    """Asset-specific validation exception - CNOP version"""
    pass


class CNOPInsufficientBalanceException(CNOPClientException):
    """Insufficient balance/funds exception - business logic validation - CNOP version"""
    pass


# ========================================
# INTERNAL SERVER EXCEPTION (500 scenarios)
# ========================================

class InternalServerException(SharedException):
    """Generic internal server exception for general use by services"""
    pass


class CNOPInternalServerException(CNOPClientException):
    """Generic internal server exception for general use by services - CNOP version"""
    pass