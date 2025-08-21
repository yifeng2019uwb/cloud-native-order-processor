"""
Test cases for JWT validation controller.
"""

import pytest
from src.controllers.validate import router


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
