"""
Test cases for custom exceptions.
"""

import pytest
from src.exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException


class TestTokenExpiredException:
    """Test cases for TokenExpiredException."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = TokenExpiredException("Token has expired")
        assert str(exception) == "TokenExpiredException: Token has expired"
        assert exception.message == "Token has expired"

    def test_exception_context(self):
        """Test exception with context."""
        exception = TokenExpiredException("Token expired", user="testuser", token_id="123")
        assert exception.context["user"] == "testuser"
        assert exception.context["token_id"] == "123"


class TestTokenInvalidException:
    """Test cases for TokenInvalidException."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = TokenInvalidException("Invalid token format")
        assert str(exception) == "TokenInvalidException: Invalid token format"
        assert exception.message == "Invalid token format"

    def test_exception_has_error_id(self):
        """Test that exception has unique error ID."""
        exception = TokenInvalidException("Test error")
        assert hasattr(exception, 'error_id')
        assert len(exception.error_id) > 0
