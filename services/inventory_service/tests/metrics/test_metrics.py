import pytest
from unittest.mock import patch, MagicMock


@patch("prometheus_client.Counter")
@patch("prometheus_client.Histogram")
def test_metrics_import(mock_histogram, mock_counter):
    import inventory_service.src.metrics


@patch("prometheus_client.Counter")
@patch("prometheus_client.Histogram")
def test_metrics_functions_exist(mock_histogram, mock_counter):
    import inventory_service.src.metrics as metrics

    assert hasattr(metrics, "metrics_collector")
    assert hasattr(metrics.metrics_collector, "record_request")
    assert callable(metrics.metrics_collector.record_request)
    assert callable(metrics.get_metrics_response)
    assert callable(metrics.get_metrics)


def test_record_request_with_duration():
    import inventory_service.src.metrics as metrics

    metrics.metrics_collector.record_request("/inventory/assets", "200", 0.1)
    metrics.metrics_collector.record_request("/inventory/assets", "404", 0.05)


def test_get_metrics_returns_bytes():
    import inventory_service.src.metrics as metrics

    data = metrics.metrics_collector.get_metrics()
    assert isinstance(data, bytes)


def test_get_metrics_response_error_handling():
    import inventory_service.src.metrics as metrics

    with patch(
        "inventory_service.src.metrics.metrics_collector.get_metrics",
        side_effect=Exception("Test error"),
    ):
        response = metrics.get_metrics_response()
        assert response.status_code == 500
        assert response.body == b"# Error\n"
