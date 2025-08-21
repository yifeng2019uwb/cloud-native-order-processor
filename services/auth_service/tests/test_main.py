"""
Test cases for Auth Service main application.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app


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


@pytest.mark.asyncio
class TestRootEndpoint:
    """Test cases for the root endpoint to achieve full coverage."""

    async def test_root_endpoint_response(self):
        """Test root endpoint returns correct response structure."""
        from src.main import root

        response = await root()

        # Verify response structure
        assert response["service"] == "Auth Service"
        assert response["version"] == "1.0.0"
        assert response["status"] == "running"
        assert "timestamp" in response

        # Verify endpoints information
        assert response["endpoints"]["docs"] == "/docs"
        assert response["endpoints"]["health"] == "/health"
        assert response["endpoints"]["validate"] == "/internal/auth/validate"

        # Verify environment information
        assert response["environment"]["service"] == "auth-service"
        assert response["environment"]["environment"] == "development"

    async def test_root_endpoint_logging(self):
        """Test that root endpoint logs correctly."""
        from src.main import root

        with patch('src.main.logger') as mock_logger:
            response = await root()

            assert response is not None
            mock_logger.info.assert_called_once_with("Root endpoint accessed")

    async def test_root_endpoint_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        from src.main import root

        response = await root()

        # Verify timestamp is in ISO format
        timestamp = response["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format contains 'T'
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp[-6:]  # UTC format
