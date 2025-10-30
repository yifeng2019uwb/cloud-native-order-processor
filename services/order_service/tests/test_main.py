"""
Tests for main.py - Order Service FastAPI Application
"""
import os
import sys
import pytest
from unittest.mock import patch

# Ensure src is on path for clean imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import dependency constants
sys.path.insert(0, os.path.dirname(__file__))
from dependency_constants import PATCH_MAIN_GET_METRICS_RESPONSE


class TestMainApplication:
    """Test the main FastAPI application"""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly"""
        from fastapi import FastAPI
        from src.main import app
        assert isinstance(app, FastAPI)
        assert app.docs_url is not None
        assert app.redoc_url is not None

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured"""
        from src.main import app
        middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_found = True
                break
        assert middleware_found, "CORS middleware should be configured"

    def test_required_routers_included(self):
        """Test that required routers are included"""
        from src.main import app
        # Check if health router is included
        health_routes = [route for route in app.routes if hasattr(route, 'path') and '/health' in str(route.path)]
        assert len(health_routes) > 0

        # Check if orders router is included
        orders_routes = [route for route in app.routes if hasattr(route, 'path') and '/orders' in str(route.path)]
        assert len(orders_routes) > 0

        # Check if asset transaction router is included
        asset_transaction_routes = [route for route in app.routes if hasattr(route, 'path') and 'transactions' in str(route.path)]
        assert len(asset_transaction_routes) > 0


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_endpoint_response(self):
        """Test the root endpoint returns correct information"""
        from src.main import root
        response = root()

        assert response["service"] == "order-service"
        assert response["version"] == "1.0.0"
        assert response["status"] == "running"
        assert "timestamp" in response
        assert "endpoints" in response


class TestMetricsEndpoint:
    """Test cases for the internal metrics endpoint."""

    @patch(PATCH_MAIN_GET_METRICS_RESPONSE)
    def test_internal_metrics_endpoint(self, mock_get_metrics_response):
        """Test that internal metrics endpoint calls get_metrics_response."""
        from fastapi import Response
        mock_response = Response(content=b"# metrics data", status_code=200)
        mock_get_metrics_response.return_value = mock_response

        from src.main import internal_metrics
        response = internal_metrics()

        assert response == mock_response
        mock_get_metrics_response.assert_called_once()

    def test_root_endpoint_timestamp_format(self):
        """Test that timestamp is in correct ISO format"""
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


class TestExceptionHandler:
    """Test the general exception handler"""

    def test_general_exception_handler_exists(self):
        """Test that the general exception handler is registered"""
        from src.main import app
        # Check if the exception handler is registered
        exception_handlers = app.exception_handlers
        assert Exception in exception_handlers, "General exception handler should be registered"
