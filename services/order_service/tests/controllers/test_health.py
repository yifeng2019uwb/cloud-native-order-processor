"""
Unit tests for src/controllers/health.py - Health check controller
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from datetime import datetime, timezone
import os

from controllers.health import health_check, router
from common.shared.health.health_checks import HealthCheckResponse, HealthChecks
from common.shared.constants.service_names import ServiceNames, ServiceVersions

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
        assert result.service == ServiceNames.ORDER_SERVICE.value
        assert result.version == ServiceVersions.DEFAULT_VERSION
        assert result.timestamp is not None
        assert result.environment is not None
        assert isinstance(result.checks, HealthChecks)
        assert result.checks.api == TEST_CHECK_OK
        assert result.checks.service == TEST_CHECK_RUNNING


class TestHealthRouter:
    """Test router configuration"""

    def test_router_configuration(self):
        """Test that router is properly configured"""
        assert router.tags == ["health"]
        assert len(router.routes) == 1  # single /health endpoint
