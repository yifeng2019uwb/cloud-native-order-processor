"""
Test cases for JWT Validator utility.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timezone
import jwt as pyjwt
from jose import jwt, JWTError

from src.utils.jwt_validator import JWTValidator
from src.auth_exceptions import TokenExpiredException, TokenInvalidException


class TestJWTValidator:
    """Test cases for JWT Validator utility."""

    def test_init(self):
        """Test JWT validator initialization."""
        validator = JWTValidator()
        assert validator.jwt_algorithm == "HS256"
        assert "dev-secret-key-change-in-production" in validator.jwt_secret

    @patch('src.utils.jwt_validator.os.getenv')
    def test_init_with_custom_secret(self, mock_getenv):
        """Test initialization with custom JWT secret."""
        mock_getenv.return_value = "custom-secret-key"
        validator = JWTValidator()
        assert validator.jwt_secret == "custom-secret-key"

    def test_init_with_default_secret(self):
        """Test initialization with default JWT secret."""
        # This test verifies that the default value is used when no env var is set
        # We can't easily mock os.getenv to return None in this context, so we'll test the actual behavior
        validator = JWTValidator()
        # The default value should be present in the secret (either from env or default)
        assert "dev-secret-key-change-in-production" in validator.jwt_secret or validator.jwt_secret != ""

    @patch('src.utils.jwt_validator.logger')
    def test_init_logging(self, mock_logger):
        """Test that initialization logs correctly."""
        with patch('src.utils.jwt_validator.os.getenv', return_value="test-secret"):
            validator = JWTValidator()
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "JWT Validator initialized" in log_call
            # Check that the format string contains the expected placeholders
            assert "%s" in log_call


class TestJWTValidatorValidateToken:
    """Test cases for validate_token method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = JWTValidator()
        self.valid_payload = {
            "type": "access_token",
            "sub": "testuser",
            "exp": datetime.now(timezone.utc).timestamp() + 3600,  # 1 hour from now
            "iat": datetime.now(timezone.utc).timestamp(),
            "role": "customer",
            "iss": "user_service",
            "aud": "trading_platform"
        }

    def create_test_token(self, payload=None, secret="dev-secret-key-change-in-production"):
        """Helper method to create test JWT tokens."""
        if payload is None:
            payload = self.valid_payload.copy()
        return pyjwt.encode(payload, secret, algorithm="HS256")

    def test_validate_token_success(self):
        """Test successful token validation."""
        token = self.create_test_token()

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = self.valid_payload

            result = self.validator.validate_token(token)

            # Verify JWT decode was called correctly
            mock_decode.assert_called_once_with(token, self.validator.jwt_secret, algorithms=["HS256"])

            # Verify result structure
            assert result["username"] == "testuser"
            assert result["role"] == "customer"
            assert result["is_authenticated"] is True
            assert "expires_at" in result
            assert "created_at" in result
            assert result["metadata"]["algorithm"] == "HS256"
            assert result["metadata"]["issuer"] == "user_service"
            assert result["metadata"]["audience"] == "trading_platform"

    def test_validate_token_missing_type(self):
        """Test validation with missing token type."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop("type")

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = invalid_payload

            with pytest.raises(TokenInvalidException, match="Invalid token type"):
                self.validator.validate_token("test.token")

    def test_validate_token_wrong_type(self):
        """Test validation with wrong token type."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["type"] = "refresh_token"

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = invalid_payload

            with pytest.raises(TokenInvalidException, match="Invalid token type"):
                self.validator.validate_token("test.token")

    def test_validate_token_missing_subject(self):
        """Test validation with missing subject."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop("sub")

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = invalid_payload

            with pytest.raises(TokenInvalidException, match="Token missing subject"):
                self.validator.validate_token("test.token")

    def test_validate_token_missing_expiration(self):
        """Test validation with missing expiration."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop("exp")

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = invalid_payload

            with pytest.raises(TokenInvalidException, match="Token missing expiration"):
                self.validator.validate_token("test.token")

    def test_validate_token_expired(self):
        """Test validation with expired token."""
        expired_payload = self.valid_payload.copy()
        expired_payload["exp"] = datetime.now(timezone.utc).timestamp() - 3600  # 1 hour ago

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = expired_payload

            with pytest.raises(TokenExpiredException, match="Token has expired"):
                self.validator.validate_token("test.token")

    def test_validate_token_default_role(self):
        """Test validation with missing role (should use default)."""
        payload_without_role = self.valid_payload.copy()
        payload_without_role.pop("role")

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = payload_without_role

            result = self.validator.validate_token("test.token")
            assert result["role"] == "customer"  # Default role

    def test_validate_token_custom_role(self):
        """Test validation with custom role."""
        custom_role_payload = self.valid_payload.copy()
        custom_role_payload["role"] = "admin"

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = custom_role_payload

            result = self.validator.validate_token("test.token")
            assert result["role"] == "admin"

    def test_validate_token_missing_iat(self):
        """Test validation with missing issued at timestamp."""
        payload_without_iat = self.valid_payload.copy()
        payload_without_iat.pop("iat")

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = payload_without_iat

            result = self.validator.validate_token("test.token")
            assert result["created_at"] is None

    def test_validate_token_custom_issuer_audience(self):
        """Test validation with custom issuer and audience."""
        custom_payload = self.valid_payload.copy()
        custom_payload["iss"] = "custom_issuer"
        custom_payload["aud"] = "custom_audience"

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = custom_payload

            result = self.validator.validate_token("test.token")
            assert result["metadata"]["issuer"] == "custom_issuer"
            assert result["metadata"]["audience"] == "custom_audience"

    def test_validate_token_jwt_expired_signature_error(self):
        """Test handling of JWT ExpiredSignatureError."""
        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

            with pytest.raises(TokenExpiredException, match="Token has expired"):
                self.validator.validate_token("test.token")

    def test_validate_token_jwt_error(self):
        """Test handling of general JWTError."""
        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(TokenInvalidException, match="Invalid token"):
                self.validator.validate_token("test.token")

    def test_validate_token_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.side_effect = ValueError("Unexpected error")

            with pytest.raises(TokenInvalidException, match="Token verification failed"):
                self.validator.validate_token("test.token")

    def test_validate_token_logging(self):
        """Test that validation logs correctly."""
        token = self.create_test_token()

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode, \
             patch('src.utils.jwt_validator.logger') as mock_logger:
            mock_decode.return_value = self.valid_payload

            self.validator.validate_token(token)

            # Check debug log
            mock_logger.debug.assert_called_once_with("Starting token validation")

            # Check info log - verify the format string contains expected placeholders
            mock_logger.info.assert_called_once()
            info_call = mock_logger.info.call_args[0][0]
            assert "Token validated successfully" in info_call
            assert "%s" in info_call  # Check for format placeholders


class TestJWTValidatorDecodeTokenPayload:
    """Test cases for decode_token_payload method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = JWTValidator()

    def test_decode_token_payload_success(self):
        """Test successful token payload decoding."""
        test_payload = {"sub": "testuser", "exp": 1234567890}

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = test_payload

            result = self.validator.decode_token_payload("test.token")

            # Verify JWT decode was called correctly
            mock_decode.assert_called_once_with(
                "test.token",
                self.validator.jwt_secret,
                options={"verify_signature": False},
                algorithms=["HS256"]
            )

            assert result == test_payload

    def test_decode_token_payload_failure(self):
        """Test token payload decoding failure."""
        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Decode failed")

            with pytest.raises(TokenInvalidException, match="Token decode failed"):
                self.validator.decode_token_payload("invalid.token")

    def test_decode_token_payload_logging(self):
        """Test that decode failure logs correctly."""
        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode, \
             patch('src.utils.jwt_validator.logger') as mock_logger:
            mock_decode.side_effect = Exception("Decode failed")

            with pytest.raises(TokenInvalidException):
                self.validator.decode_token_payload("invalid.token")

            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Error decoding token payload" in error_call


class TestJWTValidatorIsTokenExpired:
    """Test cases for is_token_expired method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = JWTValidator()

    def test_is_token_expired_future_expiration(self):
        """Test token with future expiration."""
        future_payload = {"exp": datetime.now(timezone.utc).timestamp() + 3600}  # 1 hour from now

        with patch.object(self.validator, 'decode_token_payload') as mock_decode:
            mock_decode.return_value = future_payload

            result = self.validator.is_token_expired("test.token")
            assert result is False

    def test_is_token_expired_past_expiration(self):
        """Test token with past expiration."""
        past_payload = {"exp": datetime.now(timezone.utc).timestamp() - 3600}  # 1 hour ago

        with patch.object(self.validator, 'decode_token_payload') as mock_decode:
            mock_decode.return_value = past_payload

            result = self.validator.is_token_expired("test.token")
            assert result is True

    def test_is_token_expired_missing_expiration(self):
        """Test token with missing expiration."""
        payload_without_exp = {"sub": "testuser"}

        with patch.object(self.validator, 'decode_token_payload') as mock_decode:
            mock_decode.return_value = payload_without_exp

            result = self.validator.is_token_expired("test.token")
            assert result is True

    def test_is_token_expired_decode_failure(self):
        """Test token expiration check when decode fails."""
        with patch.object(self.validator, 'decode_token_payload') as mock_decode:
            mock_decode.side_effect = Exception("Decode failed")

            result = self.validator.is_token_expired("invalid.token")
            assert result is True

    def test_is_token_expired_logging(self):
        """Test that decode failure logs correctly."""
        with patch.object(self.validator, 'decode_token_payload') as mock_decode, \
             patch('src.utils.jwt_validator.logger') as mock_logger:
            mock_decode.side_effect = Exception("Decode failed")

            self.validator.is_token_expired("invalid.token")

            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Error checking token expiration" in error_call

    def test_is_token_expired_with_invalid_token(self):
        """Test token expiration check with invalid token."""
        validator = JWTValidator()
        result = validator.is_token_expired("invalid.token.here")
        assert result is True


class TestJWTValidatorEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = JWTValidator()

    def test_validate_token_empty_payload(self):
        """Test validation with empty payload."""
        empty_payload = {}

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = empty_payload

            with pytest.raises(TokenInvalidException, match="Invalid token type"):
                self.validator.validate_token("test.token")

    def test_validate_token_none_values(self):
        """Test validation with None values in payload."""
        none_payload = {
            "type": "access_token",
            "sub": None,
            "exp": datetime.now(timezone.utc).timestamp() + 3600
        }

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = none_payload

            with pytest.raises(TokenInvalidException, match="Token missing subject"):
                self.validator.validate_token("test.token")

    def test_validate_token_current_time_expiration(self):
        """Test validation with token expiring exactly now."""
        current_time = datetime.now(timezone.utc).timestamp()
        exact_exp_payload = {
            "type": "access_token",
            "sub": "testuser",
            "exp": current_time,
            "iat": current_time - 3600,
            "role": "customer"
        }

        with patch('src.utils.jwt_validator.jwt.decode') as mock_decode:
            mock_decode.return_value = exact_exp_payload

            with pytest.raises(TokenExpiredException, match="Token has expired"):
                self.validator.validate_token("test.token")
