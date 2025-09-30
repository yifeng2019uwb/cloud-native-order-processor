"""
Unit tests for Auth Service Metrics functionality - Simplified
"""

import pytest
import time

# Import constants directly for testing
from src.constants import SERVICE_NAME, SERVICE_VERSION, SERVICE_DESCRIPTION, METRICS_ENDPOINT


class TestMetricsConstants:
    """Test cases for metrics constants definitions"""

    def test_service_metadata(self):
        """Test that service metadata constants are defined correctly"""
        assert SERVICE_NAME == "auth-service"
        assert SERVICE_VERSION == "1.0.0"
        assert SERVICE_DESCRIPTION == "JWT validation service"
        assert METRICS_ENDPOINT == "/internal/metrics"