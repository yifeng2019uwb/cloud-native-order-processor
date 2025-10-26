"""
Test cases for custom exceptions.
"""

import pytest
from src.auth_exceptions import TokenExpiredException, TokenInvalidException

# Test constants
TEST_TOKEN_EXPIRED_MESSAGE = "Token has expired"
TEST_TOKEN_EXPIRED_MESSAGE_SHORT = "Token expired"
TEST_TOKEN_INVALID_MESSAGE = "Invalid token format"


class TestTokenExpiredException:
    """Test cases for TokenExpiredException."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = TokenExpiredException(TEST_TOKEN_EXPIRED_MESSAGE)
        assert str(exception) == f"TokenExpiredException: {TEST_TOKEN_EXPIRED_MESSAGE}"
        assert exception.message == TEST_TOKEN_EXPIRED_MESSAGE

    def test_exception_context(self):
        """Test exception with message only."""
        exception = TokenExpiredException(TEST_TOKEN_EXPIRED_MESSAGE_SHORT)
        assert str(exception) == f"TokenExpiredException: {TEST_TOKEN_EXPIRED_MESSAGE_SHORT}"
        assert exception.message == TEST_TOKEN_EXPIRED_MESSAGE_SHORT


class TestTokenInvalidException:
    """Test cases for TokenInvalidException."""

    def test_exception_creation(self):
        """Test exception creation with message."""
        exception = TokenInvalidException(TEST_TOKEN_INVALID_MESSAGE)
        assert str(exception) == f"TokenInvalidException: {TEST_TOKEN_INVALID_MESSAGE}"
        assert exception.message == TEST_TOKEN_INVALID_MESSAGE
