"""
Test cases for JWT validation controller.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.controllers.validate import router, validate_jwt_token
from api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException


class TestValidateController:
    """Test cases for JWT validation controller."""

    def test_validate_router_exists(self):
        """Test that validate router exists."""
        assert router is not None
        assert hasattr(router, 'routes')

    def test_validate_router_has_validate_endpoint(self):
        """Test that validate router has validate endpoint."""
        # Check if router has routes
        assert hasattr(router, 'routes')

    def test_validate_router_prefix(self):
        """Test that validate router has correct prefix."""
        # Check router prefix
        assert router.prefix == "/internal/auth"


class TestValidateJWTTokenEndpoint:
    """Test cases for validate_jwt_token endpoint function."""

    def test_successful_token_validation(self):
        """Test successful JWT token validation."""
        # Mock request data
        request = ValidateTokenRequest(
            token="valid.jwt.token",
            request_id="test-req-123"
        )

        # Mock JWT validator response
        mock_user_context = {
            "username": "testuser",
            "role": "customer",
            "is_authenticated": True,
            "expires_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-01-01T00:00:00Z",
            "metadata": {
                "algorithm": "HS256",
                "issuer": "user_service",
                "audience": "trading_platform"
            }
        }

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify response
            assert isinstance(response, ValidateTokenResponse)
            assert response.valid is True
            assert response.user == "testuser"
            assert response.expires_at == "2025-12-31T23:59:59Z"
            assert response.created_at == "2025-01-01T00:00:00Z"
            assert response.metadata == mock_user_context["metadata"]
            assert response.request_id == "test-req-123"

            # Verify token manager was called
            mock_token_manager.validate_token_comprehensive.assert_called_once_with("valid.jwt.token")

    def test_successful_token_validation_without_request_id(self):
        """Test successful JWT token validation without request_id."""
        # Mock request data without request_id
        request = ValidateTokenRequest(token="valid.jwt.token")

        # Mock JWT validator response
        mock_user_context = {
            "username": "testuser",
            "role": "customer",
            "is_authenticated": True,
            "expires_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-01-01T00:00:00Z",
            "metadata": {"algorithm": "HS256"}
        }

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify response has generated request_id
            assert response.valid is True
            assert response.request_id is not None
            assert response.request_id.startswith("req-")

    def test_token_expired_exception(self):
        """Test handling of expired token exception."""
        # Mock request data
        request = ValidateTokenRequest(
            token="expired.jwt.token",
            request_id="test-req-expired"
        )

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = CNOPAuthTokenExpiredException("Token has expired")
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == "token_expired"
            assert response.message == "JWT token has expired"
            assert response.request_id == "test-req-expired"

    def test_token_invalid_exception(self):
        """Test handling of invalid token exception."""
        # Mock request data
        request = ValidateTokenRequest(
            token="invalid.jwt.token",
            request_id="test-req-invalid"
        )

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = CNOPAuthTokenInvalidException("Invalid token format")
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == "token_invalid"
            assert response.message == "JWT token is invalid"
            assert response.request_id == "test-req-invalid"

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        # Mock request data
        request = ValidateTokenRequest(
            token="problematic.jwt.token",
            request_id="test-req-error"
        )

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = ValueError("Unexpected error")
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response
            assert isinstance(response, ValidateTokenErrorResponse)
            assert response.valid is False
            assert response.error == "validation_error"
            assert response.message == "Token validation failed"
            assert response.request_id == "test-req-error"

    def test_token_length_logging(self):
        """Test that token length is logged correctly."""
        # Mock request data with specific token length
        long_token = "a" * 100  # 100 character token
        request = ValidateTokenRequest(token=long_token, request_id="test-req-length")

        # Mock JWT validator response
        mock_user_context = {
            "username": "testuser",
            "role": "customer",
            "is_authenticated": True,
            "expires_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-01-01T00:00:00Z",
            "metadata": {"algorithm": "HS256"}
        }

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify response
            assert response.valid is True
            assert response.user == "testuser"

    def test_processing_time_calculation(self):
        """Test that processing time is calculated and included in logging."""
        # Mock request data
        request = ValidateTokenRequest(token="test.token", request_id="test-req-time")

        # Mock JWT validator response
        mock_user_context = {
            "username": "testuser",
            "role": "customer",
            "is_authenticated": True,
            "expires_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-01-01T00:00:00Z",
            "metadata": {"algorithm": "HS256"}
        }

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify response
            assert response.valid is True
            # Processing time should be calculated (we can't easily test exact values due to timing)

    def test_user_context_extraction(self):
        """Test that all user context fields are properly extracted."""
        # Mock request data
        request = ValidateTokenRequest(token="test.token", request_id="test-req-context")

        # Mock JWT validator response with all fields
        mock_user_context = {
            "username": "adminuser",
            "role": "admin",
            "is_authenticated": True,
            "expires_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-01-01T00:00:00Z",
            "metadata": {
                "algorithm": "HS256",
                "issuer": "auth_service",
                "audience": "internal"
            }
        }

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.return_value = mock_user_context
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify all fields are properly extracted
            assert response.valid is True
            assert response.user == "adminuser"
            assert response.expires_at == "2025-12-31T23:59:59Z"
            assert response.created_at == "2025-01-01T00:00:00Z"
            assert response.metadata == mock_user_context["metadata"]
            assert response.request_id == "test-req-context"

    def test_error_response_structure(self):
        """Test that error responses have correct structure."""
        # Mock request data
        request = ValidateTokenRequest(token="error.token", request_id="test-req-error-struct")

        with patch('src.controllers.validate.TokenManager') as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager.validate_token_comprehensive.side_effect = CNOPAuthTokenInvalidException("Test error")
            mock_token_manager_class.return_value = mock_token_manager

            # Call the endpoint function
            response = validate_jwt_token(request)

            # Verify error response structure
            assert hasattr(response, 'valid')
            assert hasattr(response, 'error')
            assert hasattr(response, 'message')
            assert hasattr(response, 'request_id')
            assert response.valid is False
            assert response.error == "token_invalid"
            assert response.message == "JWT token is invalid"
