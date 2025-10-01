"""
Unit tests for shared validation functions

Tests the common validation utilities used across all microservices.
"""

import pytest
import sys
import os

# Add the common module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.core.validation.shared_validators import (
    sanitize_string,
    is_suspicious,
    validate_username
)


class TestSanitizeString:
    """Test the sanitize_string function"""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        # Test with normal string
        result = sanitize_string("Hello World")
        assert result == "Hello World"

        # Test with string containing HTML
        result = sanitize_string("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

        # Test with string containing special characters
        result = sanitize_string("Hello & World")
        assert result == "Hello & World"  # & is not HTML, so it's preserved

        # Test with max length
        result = sanitize_string("Hello World", max_length=5)
        assert result == "Hello"

    def test_sanitize_string_edge_cases(self):
        """Test sanitize_string edge cases"""
        # Test with non-string input
        result = sanitize_string(123)
        assert result == "123"

        # Test with None
        result = sanitize_string(None)
        assert result == "None"

        # Test with empty string
        result = sanitize_string("")
        assert result == ""

        # Test with whitespace only
        result = sanitize_string("   ")
        assert result == ""

    def test_sanitize_string_html_removal(self):
        """Test HTML tag removal"""
        html_string = "<script>alert('xss')</script>Hello World"
        result = sanitize_string(html_string)
        assert "Hello World" in result
        assert "<script>" not in result

        # Test multiple HTML tags
        html_string = "<div><p>Hello</p><span>World</span></div>"
        result = sanitize_string(html_string)
        assert result == "HelloWorld"


class TestIsSuspicious:
    """Test the is_suspicious function"""

    def test_is_suspicious_non_string_input(self):
        """Test is_suspicious with non-string input"""
        assert is_suspicious(123) is False
        assert is_suspicious(45.67) is False
        assert is_suspicious(None) is False
        assert is_suspicious(["list"]) is False

    def test_is_suspicious_suspicious_patterns(self):
        """Test is_suspicious detects various attack patterns"""
        suspicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "<iframe src='malicious.com'></iframe>",
            "<object data='malicious.swf'></object>",
            "<form action='malicious.com'></form>",
            "<input type='hidden' value='malicious'>",
            "<textarea>malicious content</textarea>",
            "<select><option>malicious</option></select>",
            "<button onclick='malicious()'>Click me</button>",
            "<link rel='stylesheet' href='malicious.css'>",
            "<meta http-equiv='refresh' content='0;url=malicious.com'>",
            "<style>body{background:url('malicious.jpg')}</style>",
            "<base href='malicious.com'>",
            "<bgsound src='malicious.wav'>",
            "<xmp>malicious content</xmp>",
            "<plaintext>malicious content</plaintext>",
            "<listing>malicious content</listing>",
            "<marquee>malicious content</marquee>",
            "<applet code='malicious.class'></applet>",
            "<isindex prompt='malicious'>",
            "<dir><li>malicious</li></dir>",
            "<menu><li>malicious</li></menu>",
            "<nobr>malicious content</nobr>",
            "<noembed>malicious content</noembed>",
            "<noframes>malicious content</noframes>",
            "<noscript>malicious content</noscript>",
            "<wbr>malicious content</wbr>"
        ]

        for suspicious_input in suspicious_inputs:
            assert is_suspicious(suspicious_input) is True, f"Failed to detect suspicious content: {suspicious_input}"

    def test_is_suspicious_clean_input(self):
        """Test is_suspicious with clean input"""
        clean_inputs = [
            "Hello World",
            "user123",
            "john.doe@example.com",
            "123-456-7890",
            "normal_text_with_underscores",
            "ValidUsername123"
        ]

        for clean_input in clean_inputs:
            assert is_suspicious(clean_input) is False, f"False positive for clean input: {clean_input}"


class TestValidateUsername:
    """Test the validate_username function"""

    def test_valid_usernames(self):
        """Test valid username formats"""
        valid_usernames = [
            "john_doe123",
            "user123",
            "test_user",
            "admin_2024",
            "john123doe",
            "a" * 6,  # Minimum length
            "a" * 30,  # Maximum length
            "User123",  # Should be converted to lowercase
            "USER_NAME"  # Should be converted to lowercase
        ]

        for username in valid_usernames:
            result = validate_username(username)
            assert result == username.lower()
            assert len(result) >= 6
            assert len(result) <= 30

    def test_empty_username(self):
        """Test empty username"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            validate_username("")

    def test_whitespace_only_username(self):
        """Test whitespace-only username"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            validate_username("   ")

    def test_invalid_characters(self):
        """Test usernames with invalid characters"""
        invalid_usernames = [
            "john-doe",      # Contains hyphen
            "user@name",     # Contains special char
            "user name",     # Contains space
            "user#name",     # Contains special char
            "user.name",     # Contains dot
            "user+name",     # Contains plus
            "user=name",     # Contains equals
        ]

        for username in invalid_usernames:
            with pytest.raises(ValueError, match="Username must be 6-30 alphanumeric characters and underscores only"):
                validate_username(username)

    def test_too_short_username(self):
        """Test username that's too short"""
        with pytest.raises(ValueError, match="Username must be 6-30 alphanumeric characters and underscores only"):
            validate_username("abc")

        with pytest.raises(ValueError, match="Username must be 6-30 alphanumeric characters and underscores only"):
            validate_username("a" * 5)

    def test_too_long_username(self):
        """Test username that's too long"""
        with pytest.raises(ValueError, match="Username must be 6-30 alphanumeric characters and underscores only"):
            validate_username("a" * 31)

    def test_suspicious_content(self):
        """Test usernames with suspicious content"""
        # These should still be detected as suspicious after sanitization
        suspicious_usernames = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]

        for username in suspicious_usernames:
            with pytest.raises(ValueError, match="Username contains potentially malicious content"):
                validate_username(username)

    def test_html_removal_handles_suspicious(self):
        """Test that HTML removal works but suspicious content is still caught"""
        # This should pass after HTML removal (becomes "user123")
        result = validate_username("<script>user123</script>")
        assert result == "user123"

        # This should fail because after HTML removal, it's still suspicious
        with pytest.raises(ValueError, match="Username contains potentially malicious content"):
            validate_username("<script>javascript:alert('xss')</script>")


    def test_case_conversion(self):
        """Test that usernames are converted to lowercase"""
        assert validate_username("User123") == "user123"
        assert validate_username("ADMIN_USER") == "admin_user"
        assert validate_username("Test_User_123") == "test_user_123"
