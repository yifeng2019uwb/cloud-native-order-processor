"""
Unit tests for auth exceptions

Tests the authentication-specific exceptions used across the CNOP system.
"""

import os
import sys

import pytest

# Add the common module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import the actual exceptions from source files
from src.auth.exceptions.exceptions import (
    CNOPAuthAccessDeniedException, CNOPAuthAuthorizationException,
    CNOPAuthInsufficientPermissionsException,
    CNOPAuthInvalidCredentialsException, CNOPAuthTokenExpiredException,
    CNOPAuthTokenInvalidException)
# Import base exception
from src.exceptions.base_exception import CNOPClientException


class TestAuthExceptions:
    """Test authentication-specific exceptions"""

    def test_invalid_credentials_exception(self):
        """Test CNOPAuthInvalidCredentialsException"""
        exc = CNOPAuthInvalidCredentialsException("Invalid username or password")

        assert isinstance(exc, CNOPClientException)
        assert "Invalid username or password" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthInvalidCredentialsException"

    def test_token_expired_exception(self):
        """Test CNOPAuthTokenExpiredException"""
        exc = CNOPAuthTokenExpiredException("Token has expired")

        assert isinstance(exc, CNOPClientException)
        assert "Token has expired" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthTokenExpiredException"

    def test_token_invalid_exception(self):
        """Test CNOPAuthTokenInvalidException"""
        exc = CNOPAuthTokenInvalidException("Malformed token")

        assert isinstance(exc, CNOPClientException)
        assert "Malformed token" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthTokenInvalidException"

    def test_authorization_exception(self):
        """Test CNOPAuthAuthorizationException"""
        exc = CNOPAuthAuthorizationException("Authorization failed")

        assert isinstance(exc, CNOPClientException)
        assert "Authorization failed" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthAuthorizationException"

    def test_access_denied_exception(self):
        """Test CNOPAuthAccessDeniedException"""
        exc = CNOPAuthAccessDeniedException("Access denied to resource")

        assert isinstance(exc, CNOPClientException)
        assert "Access denied to resource" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthAccessDeniedException"

    def test_insufficient_permissions_exception(self):
        """Test CNOPAuthInsufficientPermissionsException"""
        exc = CNOPAuthInsufficientPermissionsException("Insufficient permissions")

        assert isinstance(exc, CNOPClientException)
        assert "Insufficient permissions" in str(exc)
        assert exc.__class__.__name__ == "CNOPAuthInsufficientPermissionsException"

    def test_exception_inheritance(self):
        """Test that all auth exceptions inherit from CNOPClientException"""
        exceptions = [
            CNOPAuthInvalidCredentialsException,
            CNOPAuthTokenExpiredException,
            CNOPAuthTokenInvalidException,
            CNOPAuthAuthorizationException,
            CNOPAuthAccessDeniedException,
            CNOPAuthInsufficientPermissionsException,
        ]

        for exc_class in exceptions:
            exc = exc_class("Test message")
            assert isinstance(exc, CNOPClientException)
            assert issubclass(exc_class, CNOPClientException)

    def test_exception_without_message(self):
        """Test exceptions can be created without a message"""
        exc = CNOPAuthInvalidCredentialsException("")
        assert isinstance(exc, CNOPClientException)
        assert "" in str(exc)  # Empty string for no message
