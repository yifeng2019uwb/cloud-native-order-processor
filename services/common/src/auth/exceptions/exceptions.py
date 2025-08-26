"""
Auth-specific exceptions for the CNOP system.

This module contains authentication-specific exceptions that are exposed to clients
via the gateway and mapped to appropriate HTTP status codes.
"""

from ...exceptions.base_exception import CNOPClientException


class CNOPAuthInvalidCredentialsException(CNOPClientException):
    """Invalid credentials exception - authentication failures"""
    pass


class CNOPAuthTokenExpiredException(CNOPClientException):
    """Token expired exception - expired authentication tokens"""
    pass


class CNOPAuthTokenInvalidException(CNOPClientException):
    """Token invalid/malformed exception - invalid authentication tokens"""
    pass


class CNOPAuthAuthorizationException(CNOPClientException):
    """Authorization/permission exception - general authorization failures"""
    pass


class CNOPAuthAccessDeniedException(CNOPClientException):
    """Access denied exception - access permission denied"""
    pass


class CNOPAuthInsufficientPermissionsException(CNOPClientException):
    """Insufficient permissions exception - insufficient user permissions"""
    pass
