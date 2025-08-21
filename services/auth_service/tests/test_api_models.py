"""
Test cases for API models.
"""

import pytest
from src.api_models.validate import ValidateTokenRequest, ValidateTokenResponse, ValidateTokenErrorResponse


class TestValidateTokenRequest:
    """Test cases for ValidateTokenRequest model."""

    def test_valid_request(self):
        """Test valid request creation."""
        request = ValidateTokenRequest(token="test.token.here")
        assert request.token == "test.token.here"
        assert request.request_id is None

    def test_request_with_request_id(self):
        """Test request with custom request ID."""
        request = ValidateTokenRequest(token="test.token.here", request_id="req-123")
        assert request.token == "test.token.here"
        assert request.request_id == "req-123"


class TestValidateTokenResponse:
    """Test cases for ValidateTokenResponse model."""

    def test_valid_response(self):
        """Test valid response creation."""
        response = ValidateTokenResponse(
            valid=True,
            user="testuser",
            expires_at="2025-12-31T23:59:59Z",
            metadata={"algorithm": "HS256"}
        )
        assert response.valid is True
        assert response.user == "testuser"
        assert response.expires_at == "2025-12-31T23:59:59Z"


class TestValidateTokenErrorResponse:
    """Test cases for ValidateTokenErrorResponse model."""

    def test_error_response(self):
        """Test error response creation."""
        error_response = ValidateTokenErrorResponse(
            valid=False,
            error="token_expired",
            message="Token has expired"
        )
        assert error_response.valid is False
        assert error_response.error == "token_expired"
        assert error_response.message == "Token has expired"
