"""
Auth Exceptions Package

This package contains authentication-specific exceptions for the CNOP system.
These exceptions are exposed to clients via the gateway and mapped to appropriate HTTP status codes.
"""

from .exceptions import (CNOPAuthAccessDeniedException,
                         CNOPAuthAuthorizationException,
                         CNOPAuthInsufficientPermissionsException,
                         CNOPAuthInvalidCredentialsException,
                         CNOPAuthTokenExpiredException,
                         CNOPAuthTokenInvalidException)

__all__ = [
    "CNOPAuthInvalidCredentialsException",
    "CNOPAuthTokenExpiredException",
    "CNOPAuthTokenInvalidException",
    "CNOPAuthAuthorizationException",
    "CNOPAuthAccessDeniedException",
    "CNOPAuthInsufficientPermissionsException",
]
