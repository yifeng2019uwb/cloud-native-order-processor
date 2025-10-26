"""
Unit tests for Auth Service Metrics functionality
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from common.shared.constants.api_constants import HTTPStatus
from src.api_info_enum import ServiceMetadata, ApiPaths
from tests.utils.dependency_constants import PROMETHEUS_INFO, PROMETHEUS_COUNTER, PROMETHEUS_GAUGE, PROMETHEUS_HISTOGRAM

# Patch Prometheus components before importing src.metrics
mock_info_instance = MagicMock()
with patch(PROMETHEUS_INFO, return_value=mock_info_instance):
    with patch(PROMETHEUS_COUNTER):
        with patch(PROMETHEUS_GAUGE):
            with patch(PROMETHEUS_HISTOGRAM):
                import src.metrics as metrics

# Test constants
TEST_GET_METRICS = 'get_metrics'
TEST_DURATION_SHORT = 0.1
TEST_DURATION_MEDIUM = 0.5
TEST_METRICS_COLLECTOR = 'metrics_collector'
TEST_CACHE_CONTROL_HEADER = "Cache-Control"
TEST_NO_CACHE_VALUE = "no-cache"
TEST_SUCCESS_STATUS = "success"


def test_metrics_import():
    """Test that metrics module was imported successfully"""
    assert metrics is not None
    assert hasattr(metrics, TEST_METRICS_COLLECTOR)


def test_metrics_functions_exist():
    """Test that metrics functions exist and are callable"""
    assert hasattr(metrics, TEST_METRICS_COLLECTOR)
    assert hasattr(metrics, 'get_metrics_response')
    assert callable(metrics.get_metrics_response)
    assert hasattr(metrics.metrics_collector, 'record_jwt_validation')
    assert hasattr(metrics.metrics_collector, 'record_request')
    assert callable(metrics.metrics_collector.record_jwt_validation)
    assert callable(metrics.metrics_collector.record_request)


def test_metrics_collector_methods():
    """Test that metrics collector methods work correctly"""
    metrics.metrics_collector.record_jwt_validation(TEST_SUCCESS_STATUS, 0.5)
    metrics.metrics_collector.record_request(TEST_SUCCESS_STATUS, 0.5)

    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)


def test_get_metrics_response():
    """Test get_metrics_response function"""
    response = metrics.get_metrics_response()
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
    assert TEST_CACHE_CONTROL_HEADER in response.headers
    assert response.headers[TEST_CACHE_CONTROL_HEADER] == TEST_NO_CACHE_VALUE


def test_duration_conditional_blocks():
    """Test the uncovered duration conditional blocks"""
    metrics.metrics_collector.record_jwt_validation(TEST_SUCCESS_STATUS, 0.1)
    metrics.metrics_collector.record_request(TEST_SUCCESS_STATUS, 0.1)


def test_get_metrics_method():
    """Test get_metrics method"""
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)


def test_get_metrics_response_error_handling():
    """Test get_metrics_response error handling"""
    with patch.object(metrics.metrics_collector, TEST_GET_METRICS, side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.body == b"# Error\n"


class TestMetricsConstants:
    """Test cases for metrics constants definitions"""

    def test_service_metadata(self):
        """Test that service metadata constants are defined correctly"""
        assert ServiceMetadata.NAME.value == "auth-service"
        assert ServiceMetadata.VERSION.value == "1.0.0"
        assert ServiceMetadata.DESCRIPTION.value == "Independent JWT validation service"
        assert ApiPaths.METRICS.value == "/internal/metrics"