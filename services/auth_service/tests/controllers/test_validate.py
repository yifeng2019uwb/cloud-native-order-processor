"""
Test cases for JWT validation controller.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.controllers.validate import router, validate_jwt_token, _determine_token_type
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.auth.security.token_manager import TokenContext, TokenManager, TokenMetadata
from common.auth.security.jwt_constants import TokenTypes, TokenErrorTypes, JwtFields
from tests.utils.dependency_constants import AUTH_SERVICE_TOKEN_MANAGER

# Test constants
TEST_USERNAME = "testuser"
TEST_ROLE = "customer"
TEST_EXPIRATION = datetime.fromisoformat("2025-12-31T23:59:59+00:00")
TEST_ISSUED_AT = datetime.fromisoformat("2025-01-01T00:00:00+00:00")
TEST_ALGORITHM = "HS256"
TEST_ISSUED_BY = "test-service"
TEST_METADATA = {"algorithm": TEST_ALGORITHM}
TEST_REQUEST_ID_PREFIX = "req-"

# Test tokens
TEST_VALID_TOKEN = "valid.jwt.token"
TEST_EXPIRED_TOKEN = "expired.jwt.token"
TEST_INVALID_TOKEN = "invalid.jwt.token"
TEST_PROBLEMATIC_TOKEN = "problematic.jwt.token"

# Test request IDs
TEST_REQ_EXPIRED = "test-req-expired"
TEST_REQ_INVALID = "test-req-invalid"
TEST_REQ_ERROR = "test-req-error"

# Error constants
TEST_TOKEN_EXPIRED_ERROR = TokenErrorTypes.TOKEN_EXPIRED
TEST_TOKEN_EXPIRED_MESSAGE = "JWT token has expired"
TEST_TOKEN_INVALID_ERROR = TokenErrorTypes.TOKEN_INVALID
TEST_TOKEN_INVALID_MESSAGE = "JWT token is invalid"
TEST_VALIDATION_ERROR = TokenErrorTypes.VALIDATION_ERROR
TEST_VALIDATION_FAILED_MESSAGE = "Token validation failed"

# Helper test constants
TEST_TOKEN_PAYLOAD_USERNAME = "testuser"
TEST_TOKEN_PAYLOAD_EXP = 1234567890
TEST_TOKEN_PAYLOAD_IAT = 1234567800
TEST_SCOPE_VALUE = "read write"
TEST_ACCESS_TOKEN_TYPE = "access"
TEST_REFRESH_TOKEN_TYPE = "refresh"

# Exception message constants
TEST_EXPIRED_MESSAGE = "Token has expired"
TEST_INVALID_TOKEN_MESSAGE = "Invalid token format"
TEST_UNEXPECTED_ERROR_MESSAGE = "Unexpected error"


class TestValidateJWTTokenEndpoint:
    """Test cases for validate_jwt_token endpoint function."""

    def test_successful_token_validation_without_request_id(self):
        """Test successful JWT token validation without request_id."""
        # Mock request data without request_id
        request = ValidateTokenRequest(token=TEST_VALID_TOKEN)

        # Mock JWT validator response
        mock_user_context = TokenContext(
            username=TEST_USERNAME,
            role=TEST_ROLE,
            expiration=TEST_EXPIRATION,
            issued_at=TEST_ISSUED_AT,
            token_type=TokenTypes.ACCESS,
            metadata=TokenMetadata(algorithm=TEST_ALGORITHM, issued_by=TEST_ISSUED_BY)
        )

        # Patch the TokenManager class where it's used
        with patch(AUTH_SERVICE_TOKEN_MANAGER) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify response has generated request_id
            assert response.valid is True
            assert response.request_id is not None
            assert response.request_id.startswith(TEST_REQUEST_ID_PREFIX)
            assert response.user == TEST_USERNAME

    def test_token_expired_exception(self):
        """Test handling of expired token exception."""
        # Mock request data
        request = ValidateTokenRequest(
            token=TEST_EXPIRED_TOKEN,
            request_id=TEST_REQ_EXPIRED
        )

        with patch(AUTH_SERVICE_TOKEN_MANAGER) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = CNOPAuthTokenExpiredException(TEST_EXPIRED_MESSAGE)
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == TEST_TOKEN_EXPIRED_ERROR
            assert response.message == TEST_TOKEN_EXPIRED_MESSAGE
            assert response.request_id == TEST_REQ_EXPIRED

    def test_token_invalid_exception(self):
        """Test handling of invalid token exception."""
        # Mock request data
        request = ValidateTokenRequest(
            token=TEST_INVALID_TOKEN,
            request_id=TEST_REQ_INVALID
        )

        with patch(AUTH_SERVICE_TOKEN_MANAGER) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = CNOPAuthTokenInvalidException(TEST_INVALID_TOKEN_MESSAGE)
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == TEST_TOKEN_INVALID_ERROR
            assert response.message == TEST_TOKEN_INVALID_MESSAGE
            assert response.request_id == TEST_REQ_INVALID

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        # Mock request data
        request = ValidateTokenRequest(
            token=TEST_PROBLEMATIC_TOKEN,
            request_id=TEST_REQ_ERROR
        )

        with patch(AUTH_SERVICE_TOKEN_MANAGER) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = ValueError(TEST_UNEXPECTED_ERROR_MESSAGE)
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == TEST_VALIDATION_ERROR
            assert response.message == TEST_VALIDATION_FAILED_MESSAGE
            assert response.request_id == TEST_REQ_ERROR


class TestDetermineTokenType:
    """Test cases for _determine_token_type helper function."""

    def test_determine_token_type_access_token(self):
        """Test determining token type for access token (line 34 coverage)."""
        # Test case where token_type is 'access'
        token_payload = {
            JwtFields.USERNAME: TEST_TOKEN_PAYLOAD_USERNAME,
            JwtFields.TOKEN_TYPE: TEST_ACCESS_TOKEN_TYPE,
            JwtFields.EXPIRATION: TEST_TOKEN_PAYLOAD_EXP
        }

        result = _determine_token_type(token_payload)
        assert result == TEST_ACCESS_TOKEN_TYPE

    def test_determine_token_type_refresh_token(self):
        """Test determining token type for refresh token (line 34 coverage)."""
        # Test case where token_type is 'refresh'
        token_payload = {
            JwtFields.USERNAME: TEST_TOKEN_PAYLOAD_USERNAME,
            JwtFields.TOKEN_TYPE: TEST_REFRESH_TOKEN_TYPE,
            JwtFields.EXPIRATION: TEST_TOKEN_PAYLOAD_EXP
        }

        result = _determine_token_type(token_payload)
        assert result == TEST_REFRESH_TOKEN_TYPE

    def test_determine_token_type_with_scope_claim(self):
        """Test determining token type when scope claim is present (line 40 coverage)."""
        # Test case where 'scope' is in payload (should return 'access')
        token_payload = {
            JwtFields.USERNAME: TEST_TOKEN_PAYLOAD_USERNAME,
            TokenTypes.SCOPE: TEST_SCOPE_VALUE,
            JwtFields.EXPIRATION: TEST_TOKEN_PAYLOAD_EXP
        }

        result = _determine_token_type(token_payload)
        assert result == TEST_ACCESS_TOKEN_TYPE

    def test_determine_token_type_default_case(self):
        """Test determining token type when no explicit type or scope (line 30 coverage)."""
        # Test case where neither token_type nor scope is present (should return 'access' by default)
        token_payload = {
            JwtFields.USERNAME: TEST_TOKEN_PAYLOAD_USERNAME,
            JwtFields.EXPIRATION: TEST_TOKEN_PAYLOAD_EXP,
            JwtFields.ISSUED_AT: TEST_TOKEN_PAYLOAD_IAT
        }

        result = _determine_token_type(token_payload)
        assert result == TEST_ACCESS_TOKEN_TYPE
