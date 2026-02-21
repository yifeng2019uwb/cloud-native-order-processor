"""
Unit tests for Order Service Metrics functionality - 3 metrics: record_request only.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from common.shared.constants.api_constants import HTTPStatus

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from dependency_constants import (
    PATCH_PROMETHEUS_INFO, PATCH_PROMETHEUS_COUNTER,
    PATCH_PROMETHEUS_GAUGE, PATCH_PROMETHEUS_HISTOGRAM,
    PATCH_METRICS_GET_METRICS,
)

@patch(PATCH_PROMETHEUS_INFO)
@patch(PATCH_PROMETHEUS_COUNTER)
@patch(PATCH_PROMETHEUS_GAUGE)
@patch(PATCH_PROMETHEUS_HISTOGRAM)
def test_metrics_import(mock_histogram, mock_gauge, mock_counter, mock_info):
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics  # noqa: F401

@patch(PATCH_PROMETHEUS_INFO)
@patch(PATCH_PROMETHEUS_COUNTER)
@patch(PATCH_PROMETHEUS_GAUGE)
@patch(PATCH_PROMETHEUS_HISTOGRAM)
def test_metrics_functions_exist(mock_histogram, mock_gauge, mock_counter, mock_info):
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics as metrics

    assert hasattr(metrics, 'metrics_collector')
    assert hasattr(metrics, 'get_metrics_response')
    assert callable(metrics.get_metrics_response)
    assert hasattr(metrics.metrics_collector, 'record_request')
    assert hasattr(metrics.metrics_collector, 'get_metrics')
    assert callable(metrics.metrics_collector.record_request)
    assert callable(metrics.metrics_collector.get_metrics)

@patch(PATCH_PROMETHEUS_INFO)
@patch(PATCH_PROMETHEUS_COUNTER)
@patch(PATCH_PROMETHEUS_GAUGE)
@patch(PATCH_PROMETHEUS_HISTOGRAM)
def test_metrics_collector_methods(mock_histogram, mock_gauge, mock_counter, mock_info):
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics as metrics

    metrics.metrics_collector.record_request("/orders", "200", 0.1)
    metrics.metrics_collector.record_request("/orders", "400", 0.05)
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response():
    import src.metrics as metrics
    response = metrics.get_metrics_response()
    assert response.status_code == 200
    assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
    assert "Cache-Control" in response.headers
    assert response.headers["Cache-Control"] == "no-cache"

def test_get_metrics_response_error_handling():
    import src.metrics as metrics
    with patch(PATCH_METRICS_GET_METRICS, side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == 500
        assert response.body == b"# Error\n"

def test_metrics_middleware():
    import asyncio
    from unittest.mock import MagicMock
    import src.middleware as middleware

    mock_request = MagicMock()
    mock_request.url.path = "/orders"
    mock_response = MagicMock()
    mock_response.status_code = 200

    async def mock_call_next(request):
        return mock_response

    async def run_test():
        result = await middleware.metrics_middleware(mock_request, mock_call_next)
        assert result == mock_response

    asyncio.run(run_test())
