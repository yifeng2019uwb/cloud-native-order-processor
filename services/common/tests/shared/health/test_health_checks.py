"""
Tests for Health Checks
"""

# Standard library imports
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local imports
from src.shared.health import health_checks
from src.shared.health.health_checks import (HealthChecker,
                                             HealthCheckResponse,
                                             create_health_checker)

# Test constants
TEST_SERVICE = "test-service"
TEST_VERSION = "1.0.0"
TEST_VERSION_2 = "2.0.0"
TEST_ENVIRONMENT = "test"
TEST_TIMESTAMP = "2024-01-01T00:00:00Z"
TEST_STATUS_HEALTHY = "healthy"
TEST_CHECK_OK = "ok"
TEST_CHECK_RUNNING = "running"


class TestHealthCheckResponse:
    """Test HealthCheckResponse class"""

    def test_health_check_response_creation(self):
        """Test creating a HealthCheckResponse"""
        response = HealthCheckResponse(
            service=TEST_SERVICE,
            version=TEST_VERSION,
            timestamp=TEST_TIMESTAMP,
            environment=TEST_ENVIRONMENT
        )

        assert response.service == TEST_SERVICE
        assert response.version == TEST_VERSION
        assert response.environment == TEST_ENVIRONMENT
        assert response.timestamp is not None

    def test_health_check_response_with_checks(self):
        """Test HealthCheckResponse with checks object"""
        from src.shared.health.health_checks import HealthChecks

        checks = HealthChecks(api=TEST_CHECK_OK, service=TEST_CHECK_RUNNING)
        response = HealthCheckResponse(
            service=TEST_SERVICE,
            timestamp=TEST_TIMESTAMP,
            environment=TEST_ENVIRONMENT,
            checks=checks
        )

        # Test object attributes directly
        assert response.status == TEST_STATUS_HEALTHY
        assert response.service == TEST_SERVICE
        assert response.version == TEST_VERSION
        assert response.timestamp == TEST_TIMESTAMP
        assert response.environment == TEST_ENVIRONMENT
        assert isinstance(response.checks, HealthChecks)
        assert response.checks.api == TEST_CHECK_OK
        assert response.checks.service == TEST_CHECK_RUNNING


class TestHealthChecker:
    """Test HealthChecker class"""

    @pytest.fixture
    def health_checker(self):
        """Create a HealthChecker instance"""
        return HealthChecker(TEST_SERVICE, TEST_VERSION, TEST_ENVIRONMENT)

    def test_health_check(self, health_checker):
        """Test health check"""
        from src.shared.health.health_checks import HealthChecks

        result = health_checker.health_check()

        assert isinstance(result, HealthCheckResponse)
        assert result.status == TEST_STATUS_HEALTHY
        assert result.service == TEST_SERVICE
        assert result.version == TEST_VERSION
        assert isinstance(result.checks, HealthChecks)
        assert result.checks.api == TEST_CHECK_OK
        assert result.checks.service == TEST_CHECK_RUNNING

    def test_backward_compatibility_basic_health_check(self, health_checker):
        """Test backward compatibility for basic_health_check"""
        result = health_checker.basic_health_check()

        assert isinstance(result, HealthCheckResponse)
        assert result.status == TEST_STATUS_HEALTHY
        assert result.service == TEST_SERVICE

    def test_backward_compatibility_readiness_check(self, health_checker):
        """Test backward compatibility for readiness_check"""
        result = health_checker.readiness_check()

        assert isinstance(result, HealthCheckResponse)
        assert result.status == TEST_STATUS_HEALTHY
        assert result.service == TEST_SERVICE

    def test_backward_compatibility_liveness_check(self, health_checker):
        """Test backward compatibility for liveness_check"""
        result = health_checker.liveness_check()

        assert isinstance(result, HealthCheckResponse)
        assert result.status == TEST_STATUS_HEALTHY
        assert result.service == TEST_SERVICE


class TestCreateHealthChecker:
    """Test create_health_checker function"""

    def test_create_health_checker(self):
        """Test creating a health checker via factory function"""
        checker = create_health_checker(TEST_SERVICE, TEST_VERSION_2)

        assert isinstance(checker, HealthChecker)
        assert checker.service_name == TEST_SERVICE
        assert checker.version == TEST_VERSION_2
