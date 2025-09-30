"""
Unit tests for Order Service Metrics functionality
"""
import pytest
from unittest.mock import patch, MagicMock

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
    assert hasattr(metrics.metrics_collector, 'record_order_request')
    assert hasattr(metrics.metrics_collector, 'record_order_operation')
    assert hasattr(metrics.metrics_collector, 'record_portfolio_operation')
    assert hasattr(metrics.metrics_collector, 'record_asset_operation')
    assert callable(metrics.metrics_collector.record_order_request)
    assert callable(metrics.metrics_collector.record_order_operation)
    assert callable(metrics.metrics_collector.record_portfolio_operation)
    assert callable(metrics.metrics_collector.record_asset_operation)

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

    # Test record_order_request
    metrics.metrics_collector.record_order_request("200", "/orders", 0.1)

    # Test record_order_operation
    metrics.metrics_collector.record_order_operation("create", "success", 0.05)

    # Test record_portfolio_operation
    metrics.metrics_collector.record_portfolio_operation("get", "success", 0.02)

    # Test record_asset_operation
    metrics.metrics_collector.record_asset_operation("balance", "success", 0.01)

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

    # Test record_order_request with duration
    metrics.metrics_collector.record_order_request("200", "/orders", 0.1)

    # Test record_order_operation with duration
    metrics.metrics_collector.record_order_operation("create", "success", 0.05)

    # Test record_portfolio_operation with duration
    metrics.metrics_collector.record_portfolio_operation("get", "success", 0.02)

    # Test record_asset_operation with duration
    metrics.metrics_collector.record_asset_operation("balance", "success", 0.01)

def test_get_metrics_method():
    """Test get_metrics method"""
    import src.metrics as metrics

    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response_error_handling():
    """Test get_metrics_response error handling"""
    import src.metrics as metrics

    with patch('src.metrics.metrics_collector.get_metrics', side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == 500
        assert response.body == b"# Error\n"

def test_metrics_middleware():
    """Test metrics middleware function"""
    import asyncio
    from unittest.mock import MagicMock, AsyncMock
    import src.middleware as middleware

    # Create mock request and response
    mock_request = MagicMock()
    mock_request.url.path = "/orders"

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
