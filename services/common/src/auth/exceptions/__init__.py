"""
Auth Exceptions Package

This package contains authentication-specific exceptions for the CNOP system.
These exceptions are exposed to clients via the gateway and mapped to appropriate HTTP status codes.
"""

from .exceptions import (
    CNOPAuthInvalidCredentialsException,
    CNOPAuthTokenExpiredException,
    CNOPAuthTokenInvalidException,
    CNOPAuthAuthorizationException,
    CNOPAuthAccessDeniedException,
    CNOPAuthInsufficientPermissionsException,
)

__all__ = [
    "CNOPAuthInvalidCredentialsException",
    "CNOPAuthTokenExpiredException",
    "CNOPAuthTokenInvalidException",
    "CNOPAuthAuthorizationException",
    "CNOPAuthAccessDeniedException",
    "CNOPAuthInsufficientPermissionsException",
]
