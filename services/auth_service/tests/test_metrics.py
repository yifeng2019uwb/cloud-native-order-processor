"""
Unit tests for Auth Service Metrics functionality - Simplified
"""

import pytest
import time

# Import enums and constants for testing
from src.api_info_enum import ServiceMetadata, ApiPaths


class TestMetricsConstants:
    """Test cases for metrics constants definitions"""

    def test_service_metadata(self):
        """Test that service metadata constants are defined correctly"""
        assert ServiceMetadata.NAME.value == "auth-service"
        assert ServiceMetadata.VERSION.value == "1.0.0"
        assert ServiceMetadata.DESCRIPTION.value == "Independent JWT validation service"
        assert ApiPaths.METRICS.value == "/internal/metrics"