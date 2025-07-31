"""
Simple tests for basic sanitization utilities
"""

import pytest
from common.utils.sanitizer import (
    sanitize_string, sanitize_username, sanitize_email,
    sanitize_phone, is_suspicious
)


class TestSimpleSanitizer:
    """Test basic sanitization functions"""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        # Normal string
        assert sanitize_string("Hello World") == "Hello World"

        # String with HTML tags - removes tags but keeps content
        assert sanitize_string("<script>alert('xss')</script>Hello") == "alert('xss')Hello"

        # String with extra whitespace - only trims, doesn't normalize internal spaces
        assert sanitize_string("  Hello   World  ") == "Hello   World"

        # String with max length
        assert sanitize_string("Hello World", max_length=5) == "Hello"

    def test_sanitize_username(self):
        """Test username sanitization"""
        # Valid username
        assert sanitize_username("john_doe123") == "john_doe123"

        # Username with special chars - removes < and >
        assert sanitize_username("john<doe>123") == "john123"

        # Username with XSS - removes script tags but keeps content
        assert sanitize_username("<script>alert('xss')</script>john") == "alertxssjohn"

        # Too short
        with pytest.raises(ValueError, match="at least 3 characters"):
            sanitize_username("ab")

    def test_sanitize_email(self):
        """Test email sanitization"""
        # Valid email
        assert sanitize_email("user@example.com") == "user@example.com"

        # Email with HTML tags - should fail validation after sanitization
        with pytest.raises(ValueError, match="Invalid email format"):
            sanitize_email("<script>alert('xss')</script>user@example.com")

        # Invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            sanitize_email("invalid-email")

    def test_sanitize_phone(self):
        """Test phone sanitization"""
        # Valid phone
        assert sanitize_phone("+1-555-123-4567") == "15551234567"

        # Phone with letters - should fail validation
        with pytest.raises(ValueError, match="at least 10 digits"):
            sanitize_phone("555-ABC-1234")

        # Too short
        with pytest.raises(ValueError, match="at least 10 digits"):
            sanitize_phone("123")

    def test_is_suspicious(self):
        """Test suspicious input detection"""
        # Suspicious inputs
        assert is_suspicious("<script>alert('xss')</script>") is True
        assert is_suspicious("<iframe src='malicious.com'></iframe>") is True
        assert is_suspicious("javascript:alert('xss')") is True

        # Clean inputs
        assert is_suspicious("Hello World") is False
        assert is_suspicious("user@example.com") is False
        assert is_suspicious("john_doe123") is False