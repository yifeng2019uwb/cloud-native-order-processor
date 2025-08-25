"""
Unit tests for src/controllers/health.py - Health check controller
"""
import pytest
from fastapi import status

from controllers.health import (
    health_check,
    readiness_check,
    liveness_check,
    router
)


class TestHealthFunctions:
    """Test individual health functions"""

    def test_health_check_success(self):
        """Test successful basic health check"""
        result = health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "inventory-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result
        assert "environment" in result
        assert "checks" in result
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "running"

    def test_liveness_check_success(self):
        """Test successful liveness check"""
        result = liveness_check()

        assert result["status"] == "alive"
        assert result["service"] == "inventory-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result
        assert "checks" in result
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "alive"

    def test_readiness_check_success(self):
        """Test successful readiness check"""
        result = readiness_check()

        assert result["status"] == "ready"
        assert result["service"] == "inventory-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "ready"


class TestHealthRouter:
    """Test health router configuration"""

    def test_router_configuration(self):
        """Test that router is properly configured"""
        assert router.tags == ["health"]
        assert len(router.routes) == 3  # health, ready, live (no db endpoint for inventory service)