"""
Unit tests for health controller
"""
import pytest
from src.controllers.health import health_check, router
from common.shared.health.health_checks import HealthCheckResponse, HealthChecks
from common.shared.constants.service_names import ServiceNames, ServiceVersions
from src.api_info_enum import ApiTags
from src.constants import RESPONSE_FIELD_STATUS

# Test constants
TEST_STATUS_HEALTHY = "healthy"
TEST_CHECK_OK = "ok"
TEST_CHECK_RUNNING = "running"


class TestHealthFunctions:
    """Test individual health functions"""

    def test_health_check_success(self):
        """Test successful health check"""
        result = health_check()

        assert isinstance(result, HealthCheckResponse)
        assert result.status == TEST_STATUS_HEALTHY
        assert result.service == ServiceNames.INSIGHTS_SERVICE.value
        assert result.version == ServiceVersions.DEFAULT_VERSION
        assert result.timestamp is not None
        assert result.environment is not None
        assert isinstance(result.checks, HealthChecks)
        assert result.checks.api == TEST_CHECK_OK
        assert result.checks.service == TEST_CHECK_RUNNING


class TestHealthRouter:
    """Test health router configuration"""

    def test_router_configuration(self):
        """Test that router is properly configured"""
        expected_tags = [ApiTags.HEALTH.value]
        assert router.tags == expected_tags
        expected_route_count = 1
        assert len(router.routes) == expected_route_count
