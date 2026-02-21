"""
Unit tests for Auth Service Metrics functionality - 3 metrics: record_request only.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.shared.constants.api_constants import HTTPStatus
from src.api_info_enum import ServiceMetadata, ApiPaths
from tests.utils.dependency_constants import (
    PROMETHEUS_INFO,
    PROMETHEUS_COUNTER,
    PROMETHEUS_GAUGE,
    PROMETHEUS_HISTOGRAM,
)

mock_info_instance = MagicMock()
with patch(PROMETHEUS_INFO, return_value=mock_info_instance):
    with patch(PROMETHEUS_COUNTER):
        with patch(PROMETHEUS_GAUGE):
            with patch(PROMETHEUS_HISTOGRAM):
                import src.metrics as metrics

TEST_GET_METRICS = "get_metrics"
TEST_CACHE_CONTROL_HEADER = "Cache-Control"
TEST_NO_CACHE_VALUE = "no-cache"


def test_metrics_import():
    assert metrics is not None
    assert hasattr(metrics, "metrics_collector")


def test_metrics_functions_exist():
    assert hasattr(metrics, "metrics_collector")
    assert hasattr(metrics, "get_metrics_response")
    assert callable(metrics.get_metrics_response)
    assert hasattr(metrics.metrics_collector, "record_request")
    assert callable(metrics.metrics_collector.record_request)
    assert hasattr(metrics.metrics_collector, "get_metrics")
    assert callable(metrics.metrics_collector.get_metrics)


def test_metrics_collector_methods():
    metrics.metrics_collector.record_request("/internal/auth/validate", "200", 0.5)
    metrics.metrics_collector.record_request("/internal/auth/validate", "401", 0.1)
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)


def test_get_metrics_response():
    response = metrics.get_metrics_response()
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
    assert TEST_CACHE_CONTROL_HEADER in response.headers
    assert response.headers[TEST_CACHE_CONTROL_HEADER] == TEST_NO_CACHE_VALUE


def test_get_metrics_method():
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)


def test_get_metrics_response_error_handling():
    with patch.object(metrics.metrics_collector, TEST_GET_METRICS, side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.body == b"# Error\n"


class TestMetricsConstants:
    def test_service_metadata(self):
        assert ServiceMetadata.NAME.value == "auth-service"
        assert ServiceMetadata.VERSION.value == "1.0.0"
        assert ApiPaths.METRICS.value == "/internal/metrics"
