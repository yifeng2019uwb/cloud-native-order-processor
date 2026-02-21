"""
Unit tests for User Service Metrics functionality - 3 metrics: record_request only.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.shared.constants.api_constants import HTTPStatus
from src.api_info_enum import ApiPaths
from tests.utils.dependency_constants import (
    PROMETHEUS_INFO,
    PROMETHEUS_COUNTER,
    PROMETHEUS_GAUGE,
    PROMETHEUS_HISTOGRAM,
    METRICS_COLLECTOR_GET_METRICS,
)

@patch(PROMETHEUS_INFO)
@patch(PROMETHEUS_COUNTER)
@patch(PROMETHEUS_GAUGE)
@patch(PROMETHEUS_HISTOGRAM)
def test_metrics_import(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test that metrics module can be imported without error"""
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics  # noqa: F401

@patch(PROMETHEUS_INFO)
@patch(PROMETHEUS_COUNTER)
@patch(PROMETHEUS_GAUGE)
@patch(PROMETHEUS_HISTOGRAM)
def test_metrics_functions_exist(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test that metrics functions exist and are callable"""
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics as metrics

    assert hasattr(metrics, 'metrics_collector')
    assert hasattr(metrics, 'get_metrics_response')
    assert callable(metrics.get_metrics_response)
    assert hasattr(metrics.metrics_collector, 'record_request')
    assert callable(metrics.metrics_collector.record_request)
    assert hasattr(metrics.metrics_collector, 'get_metrics')
    assert callable(metrics.metrics_collector.get_metrics)

@patch(PROMETHEUS_INFO)
@patch(PROMETHEUS_COUNTER)
@patch(PROMETHEUS_GAUGE)
@patch(PROMETHEUS_HISTOGRAM)
def test_metrics_collector_record_request(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test record_request and get_metrics"""
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance
    import src.metrics as metrics

    metrics.metrics_collector.record_request(
        endpoint=ApiPaths.PROFILE.value, status_code="200", duration=0.05
    )
    metrics.metrics_collector.record_request(
        endpoint=ApiPaths.LOGIN.value, status_code="400", duration=0.02
    )
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response():
    """Test get_metrics_response function"""
    import src.metrics as metrics
    response = metrics.get_metrics_response()
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
    assert "Cache-Control" in response.headers
    assert response.headers["Cache-Control"] == "no-cache"

def test_get_metrics_response_error_handling():
    """Test get_metrics_response error handling"""
    import src.metrics as metrics
    with patch(METRICS_COLLECTOR_GET_METRICS, side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.body == b"# Error\n"
