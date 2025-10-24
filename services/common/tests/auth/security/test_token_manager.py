"""
Unit tests for TokenManager class.
"""
# Standard library imports
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest
from jose import jwt

# Local imports
from src.auth.security.token_manager import TokenManager
from src.data.entities.user import DEFAULT_USER_ROLE
from src.exceptions.shared_exceptions import (CNOPTokenExpiredException,
                                              CNOPTokenInvalidException)
from src.shared.logging import LogAction, LogField

# Test constants
TEST_JWT_SECRET = "test-secret-key-for-unit-tests-at-least-32-chars-long"
TEST_USERNAME = "testuser"
TEST_ROLE = "customer"
TEST_TOKEN_TYPE = "bearer"
TEST_ACCESS_TOKEN_TYPE = "access_token"


class TestTokenManager:
    """Test cases for TokenManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Set JWT_SECRET_KEY for tests
        os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET
        self.token_manager = TokenManager()
        self.test_username = TEST_USERNAME
        self.test_role = TEST_ROLE

    def test_create_access_token_success(self):
        """Test successful access token creation."""
        from src.auth.security.token_manager import AccessTokenResponse

        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        # Verify response is Pydantic model
        assert isinstance(result, AccessTokenResponse)
        assert result.token_type == TEST_TOKEN_TYPE
        assert isinstance(result.access_token, str)
        assert len(result.access_token) > 0
        assert result.expires_in > 0
        assert result.expires_at is not None

    def test_create_access_token_with_default_role(self):
        """Test access token creation with default role."""
        from src.auth.security.token_manager import AccessTokenResponse

        result = self.token_manager.create_access_token(TEST_USERNAME)

        # Verify default role is used
        assert isinstance(result, AccessTokenResponse)
        assert result.token_type == TEST_TOKEN_TYPE

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        from src.auth.security.token_manager import AccessTokenResponse

        custom_expiry = timedelta(hours=2)
        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE, custom_expiry)

        # Verify token data structure
        assert isinstance(result, AccessTokenResponse)
        assert result.access_token is not None
        assert result.expires_at is not None

    @patch('src.auth.security.token_manager.jwt.encode')
    def test_create_access_token_encoding_error(self, mock_encode):
        """Test access token creation with encoding error."""
        mock_encode.side_effect = Exception("Encoding failed")

        with pytest.raises(CNOPTokenInvalidException, match="Token creation failed"):
            self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

    def test_verify_access_token_success(self):
        """Test successful access token verification."""
        # Create a token first
        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        # Verify the token
        username = self.token_manager.verify_access_token(result.access_token)
        assert username == TEST_USERNAME

    def test_verify_access_token_invalid_token(self):
        """Test access token verification with invalid token."""
        with pytest.raises(CNOPTokenInvalidException, match="Invalid token"):
            self.token_manager.verify_access_token("invalid_token")

    def test_verify_access_token_wrong_secret(self):
        """Test access token verification with wrong secret."""
        # Create token with different secret
        with patch.object(self.token_manager, 'jwt_secret', 'wrong_secret'):
            result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        # Try to verify with correct secret
        with pytest.raises(CNOPTokenInvalidException, match="Invalid token"):
            self.token_manager.verify_access_token(result.access_token)

    def test_verify_access_token_missing_subject(self):
        """Test access token verification with missing subject."""
        # Create payload without subject
        payload = {
            "role": self.test_role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        }
        token = jwt.encode(payload, self.token_manager.jwt_secret, algorithm=self.token_manager.jwt_algorithm)

        with pytest.raises(CNOPTokenInvalidException, match="Token missing subject"):
            self.token_manager.verify_access_token(token)

    def test_verify_access_token_wrong_type(self):
        """Test access token verification with wrong token type."""
        # Create payload with wrong type
        payload = {
            "sub": self.test_username,
            "role": self.test_role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "type": "refresh_token"  # Wrong type
        }
        token = jwt.encode(payload, self.token_manager.jwt_secret, algorithm=self.token_manager.jwt_algorithm)

        with pytest.raises(CNOPTokenInvalidException, match="Invalid token type"):
            self.token_manager.verify_access_token(token)

    def test_verify_access_token_expired(self):
        """Test access token verification with expired token."""
        # Create payload with expired time
        payload = {
            "sub": self.test_username,
            "role": self.test_role,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "type": "access_token"
        }
        token = jwt.encode(payload, self.token_manager.jwt_secret, algorithm=self.token_manager.jwt_algorithm)

        with pytest.raises(CNOPTokenExpiredException, match="Token has expired"):
            self.token_manager.verify_access_token(token)

    def test_decode_token_payload_success(self):
        """Test successful token payload decoding."""
        # Create a token first
        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        # Decode payload
        payload = self.token_manager.decode_token_payload(result.access_token)

        # Verify payload structure
        assert "sub" in payload
        assert "role" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload

        # Verify payload values
        assert payload["sub"] == TEST_USERNAME
        assert payload["role"] == TEST_ROLE
        assert payload["type"] == TEST_ACCESS_TOKEN_TYPE

    def test_decode_token_payload_invalid_token(self):
        """Test token payload decoding with invalid token."""
        with pytest.raises(CNOPTokenInvalidException, match="Token decode failed"):
            self.token_manager.decode_token_payload("invalid_token")

    def test_is_token_expired_true(self):
        """Test token expiration check with expired token."""
        # Create payload with expired time
        payload = {
            "sub": self.test_username,
            "role": self.test_role,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "type": "access_token"
        }
        token = jwt.encode(payload, self.token_manager.jwt_secret, algorithm=self.token_manager.jwt_algorithm)

        assert self.token_manager.is_token_expired(token) is True

    def test_is_token_expired_false(self):
        """Test token expiration check with valid token."""
        # Create a valid token
        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        assert self.token_manager.is_token_expired(result.access_token) is False

    def test_is_token_expired_missing_exp(self):
        """Test token expiration check with missing expiration."""
        # Create payload without expiration
        payload = {
            "sub": self.test_username,
            "role": self.test_role,
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        }
        token = jwt.encode(payload, self.token_manager.jwt_secret, algorithm=self.token_manager.jwt_algorithm)

        assert self.token_manager.is_token_expired(token) is True

    def test_is_token_expired_invalid_token(self):
        """Test token expiration check with invalid token."""
        assert self.token_manager.is_token_expired("invalid_token") is True

    def test_integration_create_verify_decode(self):
        """Test integration of create, verify, and decode methods."""
        # Create token
        result = self.token_manager.create_access_token(TEST_USERNAME, TEST_ROLE)

        # Verify token
        username = self.token_manager.verify_access_token(result.access_token)
        assert username == TEST_USERNAME

        # Decode payload
        payload = self.token_manager.decode_token_payload(result.access_token)
        assert payload["sub"] == TEST_USERNAME
        assert payload["role"] == TEST_ROLE

        # Check expiration
        assert self.token_manager.is_token_expired(result.access_token) is False