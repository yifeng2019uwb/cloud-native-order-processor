"""
Unit tests for main.py - FastAPI application entry point
"""
import pytest
from fastapi.testclient import TestClient

from main import app, root


class TestMainApplication:
    """Test the main FastAPI application"""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly"""
        assert app.title == "User Authentication Service"
        assert app.description == "A cloud-native user authentication service"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured"""
        middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_found = True
                break
        assert middleware_found, "CORS middleware should be configured"

    def test_required_routers_included(self):
        """Test that required routers are included"""
        # Check if auth router is included
        auth_routes = [route for route in app.routes if hasattr(route, 'path') and '/auth/' in str(route.path)]
        assert len(auth_routes) > 0

        # Check if balance router is included
        balance_routes = [route for route in app.routes if hasattr(route, 'path') and '/balance' in str(route.path)]
        assert len(balance_routes) > 0

        # Check if health router is included
        health_routes = [route for route in app.routes if hasattr(route, 'path') and '/health' in str(route.path)]
        assert len(health_routes) > 0


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_endpoint_response(self):
        """Test the root endpoint returns correct information"""
        response = root()

        assert response["service"] == "User Authentication Service"
        assert response["version"] == "1.0.0"
        assert response["status"] == "running"
        assert "timestamp" in response
        assert "endpoints" in response

        # Check endpoints
        endpoints = response["endpoints"]
        assert endpoints["docs"] == "/docs"
        assert endpoints["health"] == "/health"
        assert endpoints["register"] == "/auth/register"
        assert endpoints["login"] == "/auth/login"
        assert endpoints["profile"] == "/auth/profile"
        assert endpoints["logout"] == "/auth/logout"
        assert endpoints["balance"] == "/balance"
        assert endpoints["deposit"] == "/balance/deposit"
        assert endpoints["withdraw"] == "/balance/withdraw"
        assert endpoints["transactions"] == "/balance/transactions"

    def test_root_endpoint_timestamp_format(self):
        """Test that timestamp is in correct ISO format"""
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
        # Check if the exception handler is registered
        exception_handlers = app.exception_handlers
        assert Exception in exception_handlers, "General exception handler should be registered"


if __name__ == "__main__":
    pytest.main([__file__])