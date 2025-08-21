"""
Test cases for JWT Validator utility.
"""

import pytest
from unittest.mock import patch
from src.utils.jwt_validator import JWTValidator


class TestJWTValidator:
    """Test cases for JWT Validator utility."""

    def test_init(self):
        """Test JWT validator initialization."""
        validator = JWTValidator()
        assert validator.jwt_algorithm == "HS256"
        assert "dev-secret-key-change-in-production" in validator.jwt_secret

    def test_is_token_expired_with_invalid_token(self):
        """Test token expiration check with invalid token."""
        validator = JWTValidator()
        result = validator.is_token_expired("invalid.token.here")
        assert result is True

    @patch('src.utils.jwt_validator.os.getenv')
    def test_init_with_custom_secret(self, mock_getenv):
        """Test initialization with custom JWT secret."""
        mock_getenv.return_value = "custom-secret-key"
        validator = JWTValidator()
        assert validator.jwt_secret == "custom-secret-key"
