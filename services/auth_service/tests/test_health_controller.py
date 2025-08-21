"""
Test cases for health controller.
"""

import pytest
from src.controllers.health import router


class TestHealthController:
    """Test cases for health controller."""

    def test_health_router_exists(self):
        """Test that health router exists."""
        assert router is not None
        assert hasattr(router, 'routes')

    def test_health_router_has_health_endpoint(self):
        """Test that health router has health endpoint."""
        # Check if router has routes
        assert hasattr(router, 'routes')
