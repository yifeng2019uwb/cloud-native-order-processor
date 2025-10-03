"""
Unit tests for TokenManager class.
"""
# Standard library imports
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


class TestTokenManager:
    """Test cases for TokenManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.token_manager = TokenManager()
        self.test_username = "testuser"
        self.test_role = "customer"

    def test_create_access_token_success(self):
        """Test successful access token creation."""
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role)

        # Verify token data structure
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        assert "expires_at" in token_data

        # Verify token type
        assert token_data["token_type"] == "bearer"

        # Verify token is a string
        assert isinstance(token_data["access_token"], str)
        assert len(token_data["access_token"]) > 0

    def test_create_access_token_with_default_role(self):
        """Test access token creation with default role."""
        token_data = self.token_manager.create_access_token(self.test_username)

        # Verify default role is used
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        custom_expiry = timedelta(hours=2)
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role, custom_expiry)

        # Verify token data structure
        assert "access_token" in token_data
        assert "expires_at" in token_data

    @patch('src.auth.security.token_manager.jwt.encode')
    def test_create_access_token_encoding_error(self, mock_encode):
        """Test access token creation with encoding error."""
        mock_encode.side_effect = Exception("Encoding failed")

        with pytest.raises(CNOPTokenInvalidException, match="Token creation failed"):
            self.token_manager.create_access_token(self.test_username, self.test_role)

    def test_verify_access_token_success(self):
        """Test successful access token verification."""
        # Create a token first
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role)
        token = token_data["access_token"]

        # Verify the token
        username = self.token_manager.verify_access_token(token)
        assert username == self.test_username

    def test_verify_access_token_invalid_token(self):
        """Test access token verification with invalid token."""
        with pytest.raises(CNOPTokenInvalidException, match="Invalid token"):
            self.token_manager.verify_access_token("invalid_token")

    def test_verify_access_token_wrong_secret(self):
        """Test access token verification with wrong secret."""
        # Create token with different secret
        with patch.object(self.token_manager, 'jwt_secret', 'wrong_secret'):
            token_data = self.token_manager.create_access_token(self.test_username, self.test_role)
            token = token_data["access_token"]

        # Try to verify with correct secret
        with pytest.raises(CNOPTokenInvalidException, match="Invalid token"):
            self.token_manager.verify_access_token(token)

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
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role)
        token = token_data["access_token"]

        # Decode payload
        payload = self.token_manager.decode_token_payload(token)

        # Verify payload structure
        assert "sub" in payload
        assert "role" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload

        # Verify payload values
        assert payload["sub"] == self.test_username
        assert payload["role"] == self.test_role
        assert payload["type"] == "access_token"

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
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role)
        token = token_data["access_token"]

        assert self.token_manager.is_token_expired(token) is False

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
        token_data = self.token_manager.create_access_token(self.test_username, self.test_role)
        token = token_data["access_token"]

        # Verify token
        username = self.token_manager.verify_access_token(token)
        assert username == self.test_username

        # Decode payload
        payload = self.token_manager.decode_token_payload(token)
        assert payload["sub"] == self.test_username
        assert payload["role"] == self.test_role

        # Check expiration
        assert self.token_manager.is_token_expired(token) is False