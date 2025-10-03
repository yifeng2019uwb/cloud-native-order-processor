"""
Test cases for Auth Service main application.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import Request
from src.main import app
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.exceptions import CNOPInternalServerException


class TestMainApp:
    """Test cases for main FastAPI application."""

    def test_app_exists(self):
        """Test that FastAPI app exists."""
        assert app is not None
        assert hasattr(app, 'routes')

    def test_app_has_health_router(self):
        """Test that health router is included."""
        # Check if any route contains /health
        health_routes = [route for route in app.routes if hasattr(route, 'path') and '/health' in str(route.path)]
        assert len(health_routes) > 0

    def test_app_has_validate_router(self):
        """Test that validate router is included."""
        # Check if any route contains /internal/auth/validate
        validate_routes = [route for route in app.routes if hasattr(route, 'path') and '/internal/auth/validate' in str(route.path)]
        assert len(validate_routes) > 0

    def test_app_title(self):
        """Test that app has correct title."""
        assert app.title == "Auth Service"

    def test_app_version(self):
        """Test that app has correct version."""
        assert app.version == "1.0.0"


class TestRootEndpoint:
    """Test cases for the root endpoint to achieve full coverage."""

    def test_root_endpoint_response(self):
        """Test root endpoint returns correct response structure."""
        from src.main import root

        response = root()

        # Verify response structure
        assert response["service"] == "auth-service"
        assert response["version"] == "1.0.0"
        assert response["status"] == "running"
        assert "timestamp" in response

        # Verify endpoints information
        assert response["endpoints"]["docs"] == "/docs"
        assert response["endpoints"]["health"] == "/health"
        assert response["endpoints"]["validate"] == "/internal/auth/validate"

    def test_root_endpoint_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        from src.main import root

        response = root()

        # Verify timestamp is in ISO format
        timestamp = response["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format contains 'T'
        # Check if it's a valid datetime string
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} is not a valid ISO format")


class TestMetricsEndpoint:
    """Test cases for the internal metrics endpoint."""

    @patch('src.main.get_metrics_response')
    def test_internal_metrics_endpoint(self, mock_get_metrics_response):
        """Test that internal metrics endpoint calls get_metrics_response."""
        # Mock the metrics response
        mock_response = {"auth_requests_total": 10, "jwt_validations_total": 5}
        mock_get_metrics_response.return_value = mock_response

        # Test the endpoint function directly
        from src.main import internal_metrics
        response = internal_metrics()

        # Verify the response and that get_metrics_response was called
        assert response == mock_response
        mock_get_metrics_response.assert_called_once()


class TestExceptionHandlers:
    """Test cases for custom exception handlers."""

    def test_token_expired_exception_handler(self):
        """Test token expired exception handler."""
        from src.main import token_expired_exception_handler

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_exception = CNOPAuthTokenExpiredException("Token has expired")

        # Call the handler
        response = token_expired_exception_handler(mock_request, mock_exception)

        # Verify response
        assert response.status_code == 401
        assert response.body.decode() == '{"detail":"CNOPAuthTokenExpiredException: Token has expired"}'

    def test_token_invalid_exception_handler(self):
        """Test token invalid exception handler."""
        from src.main import token_invalid_exception_handler

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_exception = CNOPAuthTokenInvalidException("Invalid token format")

        # Call the handler
        response = token_invalid_exception_handler(mock_request, mock_exception)

        # Verify response
        assert response.status_code == 401
        assert response.body.decode() == '{"detail":"CNOPAuthTokenInvalidException: Invalid token format"}'

    def test_internal_server_exception_handler(self):
        """Test internal server exception handler."""
        from src.main import internal_server_exception_handler

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_exception = CNOPInternalServerException("Database connection failed")

        # Call the handler
        response = internal_server_exception_handler(mock_request, mock_exception)

        # Verify response
        assert response.status_code == 500
        assert response.body.decode() == '{"detail":"CNOPInternalServerException: Database connection failed"}'

    def test_general_exception_handler(self):
        """Test general exception handler."""
        from src.main import general_exception_handler

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_exception = ValueError("Unexpected error occurred")

        # Call the handler
        response = general_exception_handler(mock_request, mock_exception)

        # Verify response
        assert response.status_code == 500
        assert response.body.decode() == '{"detail":"An internal server error occurred. Please try again later."}'
