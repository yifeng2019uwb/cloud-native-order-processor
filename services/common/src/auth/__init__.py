"""
Auth Package

This package contains all authentication functionality for the CNOP system.
Includes security (JWT, passwords, tokens), gateway validation, and auth-specific exceptions.
"""

from .security import (
    # Security classes
    PasswordManager,
    TokenManager,
    AuditLogger,
)

from .gateway import (
    # Gateway validation class
    HeaderValidator,
)

from .exceptions import (
    # Auth-specific exceptions
    CNOPAuthInvalidCredentialsException,
    CNOPAuthTokenExpiredException,
    CNOPAuthTokenInvalidException,
    CNOPAuthAuthorizationException,
    CNOPAuthAccessDeniedException,
    CNOPAuthInsufficientPermissionsException,
)

__all__ = [
    # Security classes
    "PasswordManager",
    "TokenManager",
    "AuditLogger",

    # Gateway validation class
    "HeaderValidator",

    # Auth-specific exceptions
    "CNOPAuthInvalidCredentialsException",
    "CNOPAuthTokenExpiredException",
    "CNOPAuthTokenInvalidException",
    "CNOPAuthAuthorizationException",
    "CNOPAuthAccessDeniedException",
    "CNOPAuthInsufficientPermissionsException",
]
