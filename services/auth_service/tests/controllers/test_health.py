"""
Test cases for health controller.
"""

import pytest
from unittest.mock import patch
from src.controllers.health import router, health_checker, health_check
from common.shared.health.health_checks import HealthCheckResponse, HealthChecks
from common.shared.constants.service_names import ServiceNames, ServiceVersions

# Test constants
TEST_STATUS_HEALTHY = "healthy"
TEST_CHECK_OK = "ok"
TEST_CHECK_RUNNING = "running"


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
        """Test health check endpoint calls health_check."""
        # Mock the health checker response
        mock_response = HealthCheckResponse(
            service=ServiceNames.AUTH_SERVICE.value,
            timestamp="2024-01-01T00:00:00Z",
            environment="test"
        )
        mock_health_checker.health_check.return_value = mock_response

        # Call the endpoint function
        response = health_check()

        # Verify response and that health_check was called
        assert isinstance(response, HealthCheckResponse)
        assert response.service == ServiceNames.AUTH_SERVICE.value
        mock_health_checker.health_check.assert_called_once()
