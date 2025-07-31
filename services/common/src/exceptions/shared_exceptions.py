"""
Shared exceptions for all services
Path: services/common/src/exceptions/shared_exceptions.py

These exceptions are shared across all services and get mapped to external error codes.
They represent business logic exceptions that can be exposed to clients.
"""

from .base_exception import BaseInternalException


class SharedException(BaseInternalException):
    """Base class for shared exceptions that get mapped to external error codes"""
    pass


# ========================================
# AUTHENTICATION EXCEPTIONS (401 scenarios)
# ========================================

class InvalidCredentialsException(SharedException):
    """Invalid credentials exception"""
    pass


class TokenExpiredException(SharedException):
    """Token expired exception"""
    pass


class TokenInvalidException(SharedException):
    """Token invalid/malformed exception"""
    pass


# ========================================
# AUTHORIZATION EXCEPTIONS (403 scenarios)
# ========================================

class AuthorizationException(SharedException):
    """Authorization/permission exception"""
    pass


class AccessDeniedException(SharedException):
    """Access denied exception"""
    pass


class InsufficientPermissionsException(SharedException):
    """Insufficient permissions exception"""
    pass


# ========================================
# RESOURCE EXCEPTIONS (404, 409 scenarios)
# ========================================

class EntityNotFoundException(SharedException):
    """Generic entity not found exception"""
    pass


class EntityAlreadyExistsException(SharedException):
    """Generic entity already exists exception"""
    pass


class UserNotFoundException(SharedException):
    """User not found exception"""
    pass


class OrderNotFoundException(SharedException):
    """Order not found exception"""
    pass


class AssetNotFoundException(SharedException):
    """Asset not found exception"""
    pass


# ========================================
# VALIDATION EXCEPTIONS (422 scenarios)
# ========================================

class EntityValidationException(SharedException):
    """Generic entity validation exception"""
    pass


class UserValidationException(SharedException):
    """User-specific validation exception"""
    pass


class OrderValidationException(SharedException):
    """Order-specific validation exception"""
    pass


class AssetValidationException(SharedException):
    """Asset-specific validation exception"""
    pass


# ========================================
# INTERNAL SERVER EXCEPTION (500 scenarios)
# ========================================

class InternalServerException(SharedException):
    """Generic internal server exception for general use by services"""
    pass