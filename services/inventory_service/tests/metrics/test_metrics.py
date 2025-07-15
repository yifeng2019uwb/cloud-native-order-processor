import pytest
from unittest.mock import patch

@patch('prometheus_client.Counter')
@patch('prometheus_client.Gauge')
@patch('prometheus_client.Histogram')
def test_metrics_import(mock_histogram, mock_gauge, mock_counter):
    """Test that metrics module can be imported without error"""
    import inventory_service.src.metrics
    # If we get here, the import succeeded

@patch('prometheus_client.Counter')
@patch('prometheus_client.Gauge')
@patch('prometheus_client.Histogram')
def test_metrics_functions_exist(mock_histogram, mock_gauge, mock_counter):
    """Test that metrics functions exist and are callable"""
    import inventory_service.src.metrics as metrics

    # Test that functions exist
    assert hasattr(metrics, 'record_asset_retrieval')
    assert hasattr(metrics, 'record_asset_detail_view')
    assert hasattr(metrics, 'update_asset_counts')

    # Test that they are callable
    assert callable(metrics.record_asset_retrieval)
    assert callable(metrics.record_asset_detail_view)
    assert callable(metrics.update_asset_counts)