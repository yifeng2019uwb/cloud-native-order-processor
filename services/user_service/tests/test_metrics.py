"""
Unit tests for User Service Metrics functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from common.shared.constants.http_status import HTTPStatus

@patch('prometheus_client.Info')
@patch('prometheus_client.Counter')
@patch('prometheus_client.Gauge')
@patch('prometheus_client.Histogram')
def test_metrics_import(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test that metrics module can be imported without error"""
    # Mock the Info object
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance

    import src.metrics
    # If we get here, the import succeeded

@patch('prometheus_client.Info')
@patch('prometheus_client.Counter')
@patch('prometheus_client.Gauge')
@patch('prometheus_client.Histogram')
def test_metrics_functions_exist(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test that metrics functions exist and are callable"""
    # Mock the Info object
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance

    import src.metrics as metrics

    # Test that functions exist
    assert hasattr(metrics, 'metrics_collector')
    assert hasattr(metrics, 'get_metrics_response')

    # Test that they are callable
    assert callable(metrics.get_metrics_response)

    # Test metrics_collector methods
    assert hasattr(metrics.metrics_collector, 'record_user_request')
    assert hasattr(metrics.metrics_collector, 'record_auth_operation')
    assert hasattr(metrics.metrics_collector, 'record_balance_operation')
    assert callable(metrics.metrics_collector.record_user_request)
    assert callable(metrics.metrics_collector.record_auth_operation)
    assert callable(metrics.metrics_collector.record_balance_operation)

@patch('prometheus_client.Info')
@patch('prometheus_client.Counter')
@patch('prometheus_client.Gauge')
@patch('prometheus_client.Histogram')
def test_metrics_collector_methods(mock_histogram, mock_gauge, mock_counter, mock_info):
    """Test that metrics collector methods work correctly"""
    # Mock the Info object
    mock_info_instance = MagicMock()
    mock_info.return_value = mock_info_instance

    import src.metrics as metrics

    # Test record_user_request
    metrics.metrics_collector.record_user_request("200", "/users/profile", 0.1)

    # Test record_auth_operation
    metrics.metrics_collector.record_auth_operation("login", "success", 0.05)

    # Test record_balance_operation
    metrics.metrics_collector.record_balance_operation("deposit", "success", 0.02)

    # Test get_metrics
    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response():
    """Test get_metrics_response function"""
    import src.metrics as metrics

    response = metrics.get_metrics_response()
    assert response.status_code == 200
    assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
    assert "Cache-Control" in response.headers
    assert response.headers["Cache-Control"] == "no-cache"

def test_duration_conditional_blocks():
    """Test the uncovered duration conditional blocks"""
    import src.metrics as metrics

    # Test record_user_request with duration (covers lines 45-46)
    metrics.metrics_collector.record_user_request("200", "/test", 0.1)

    # Test record_auth_operation with duration (covers lines 51-52)
    metrics.metrics_collector.record_auth_operation("login", "success", 0.05)

    # Test record_balance_operation with duration (covers lines 57-58)
    metrics.metrics_collector.record_balance_operation("deposit", "success", 0.02)

def test_get_metrics_method():
    """Test get_metrics method (covers lines 61-62)"""
    import src.metrics as metrics

    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response_error_handling():
    """Test get_metrics_response error handling (covers lines 80-81)"""
    import src.metrics as metrics

    with patch('src.metrics.metrics_collector.get_metrics', side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.body == b"# Error\n"

def test_metrics_middleware():
    """Test metrics middleware function"""
    import asyncio
    from unittest.mock import MagicMock, AsyncMock
    import src.middleware as middleware

    # Create mock request and response
    mock_request = MagicMock()
    mock_request.url.path = "/users/profile"

    mock_response = MagicMock()
    mock_response.status_code = 200

    # Create mock call_next function
    async def mock_call_next(request):
        return mock_response

    # Test the middleware
    async def run_test():
        result = await middleware.metrics_middleware(mock_request, mock_call_next)
        assert result == mock_response

    # Run the async test
    asyncio.run(run_test())
