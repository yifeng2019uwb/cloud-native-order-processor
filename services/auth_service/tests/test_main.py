"""
Test cases for Auth Service main application.
"""

import pytest
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
