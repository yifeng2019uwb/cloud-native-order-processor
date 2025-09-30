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

    import inventory_service.src.metrics
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

    import inventory_service.src.metrics as metrics

    # Test that functions exist
    assert hasattr(metrics, 'metrics_collector')
    assert hasattr(metrics, 'get_metrics_response')
    assert hasattr(metrics, 'get_metrics')

    # Test that they are callable
    assert callable(metrics.get_metrics_response)
    assert callable(metrics.get_metrics)

    # Test metrics_collector methods
    assert hasattr(metrics.metrics_collector, 'record_inventory_request')
    assert hasattr(metrics.metrics_collector, 'record_asset_operation')
    assert hasattr(metrics.metrics_collector, 'record_api_call')
    assert callable(metrics.metrics_collector.record_inventory_request)
    assert callable(metrics.metrics_collector.record_asset_operation)
    assert callable(metrics.metrics_collector.record_api_call)

def test_duration_conditional_blocks():
    """Test the uncovered duration conditional blocks"""
    import inventory_service.src.metrics as metrics

    # Test record_inventory_request with duration
    metrics.metrics_collector.record_inventory_request("200", "/inventory/assets", 0.1)

    # Test record_asset_operation with duration
    metrics.metrics_collector.record_asset_operation("list_assets", "success", 0.05)

    # Test record_api_call with duration
    metrics.metrics_collector.record_api_call("coingecko", "success", 0.02)

def test_get_metrics_method():
    """Test get_metrics method"""
    import inventory_service.src.metrics as metrics

    metrics_data = metrics.metrics_collector.get_metrics()
    assert isinstance(metrics_data, bytes)

def test_get_metrics_response_error_handling():
    """Test get_metrics_response error handling"""
    import inventory_service.src.metrics as metrics

    with patch('inventory_service.src.metrics.metrics_collector.get_metrics', side_effect=Exception("Test error")):
        response = metrics.get_metrics_response()
        assert response.status_code == 500
        assert response.body == b"# Error\n"