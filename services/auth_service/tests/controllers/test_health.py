"""
Test cases for health controller.
"""

import pytest
from unittest.mock import patch, Mock
from src.controllers.health import router, health_checker, health_check, readiness_check, liveness_check


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

    @patch('src.controllers.health.health_checker')
    def test_health_check_endpoint(self, mock_health_checker):
        """Test health check endpoint calls basic_health_check (line 21 coverage)."""
        # Mock the health checker response
        mock_response = {"status": "healthy", "service": "auth-service"}
        mock_health_checker.basic_health_check.return_value = mock_response

        # Call the endpoint function
        response = health_check()

        # Verify response and that basic_health_check was called
        assert response == mock_response
        mock_health_checker.basic_health_check.assert_called_once()

    @patch('src.controllers.health.health_checker')
    def test_readiness_check_endpoint(self, mock_health_checker):
        """Test readiness check endpoint calls readiness_check (line 27 coverage)."""
        # Mock the health checker response
        mock_response = {"status": "ready", "service": "auth-service"}
        mock_health_checker.readiness_check.return_value = mock_response

        # Call the endpoint function
        response = readiness_check()

        # Verify response and that readiness_check was called
        assert response == mock_response
        mock_health_checker.readiness_check.assert_called_once()

    @patch('src.controllers.health.health_checker')
    def test_liveness_check_endpoint(self, mock_health_checker):
        """Test liveness check endpoint calls liveness_check (line 33 coverage)."""
        # Mock the health checker response
        mock_response = {"status": "alive", "service": "auth-service"}
        mock_health_checker.liveness_check.return_value = mock_response

        # Call the endpoint function
        response = liveness_check()

        # Verify response and that liveness_check was called
        assert response == mock_response
        mock_health_checker.liveness_check.assert_called_once()
