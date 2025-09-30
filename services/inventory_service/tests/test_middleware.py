"""
Unit tests for Inventory Service Middleware functionality
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response

class TestMetricsMiddleware:
    """Test cases for metrics middleware functionality"""

    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        """Test middleware records metrics for successful requests"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_inventory_request.assert_called_once()
            mock_collector.record_asset_operation.assert_called_once_with("list_assets", "success", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        """Test middleware records metrics for error responses"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_inventory_request.assert_called_once()
            mock_collector.record_asset_operation.assert_called_once_with("list_assets", "error", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test middleware handles exceptions and records error metrics"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"
        mock_request.method = "GET"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch('src.middleware.metrics_collector') as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_inventory_request.assert_called_once()
            mock_collector.record_asset_operation.assert_called_once_with("list_assets", "error", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_asset_endpoint_detection(self):
        """Test middleware detects asset endpoints correctly"""
        from src.middleware import metrics_middleware

        test_cases = [
            ("/inventory/assets", "GET", "list_assets"),
            ("/inventory/assets/BTC", "GET", "list_assets"),  # Only 3 slashes, so it's list_assets
            ("/inventory/assets/BTC/details", "GET", "get_asset_detail"),  # 4 slashes, so it's get_asset_detail
            ("/inventory/assets", "POST", "create_asset"),
            ("/inventory/assets/BTC", "PUT", "update_asset"),
            ("/inventory/assets/BTC", "DELETE", "delete_asset"),
        ]

        for endpoint, method, expected_op in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.url.path = endpoint
            mock_request.method = method

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200

            async def mock_call_next(request):
                return mock_response

            with patch('src.middleware.metrics_collector') as mock_collector:
                await metrics_middleware(mock_request, mock_call_next)
                mock_collector.record_asset_operation.assert_called_with(expected_op, "success", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_api_call_detection(self):
        """Test middleware detects API calls correctly"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/coingecko"
        mock_request.method = "GET"
        mock_request.url = MagicMock()
        mock_request.url.__str__ = MagicMock(return_value="https://api.coingecko.com/coins")

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_inventory_request.assert_called_once()
            mock_collector.record_api_call.assert_called_once_with("coingecko", "success", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_unknown_endpoint_no_specific_metrics(self):
        """Test middleware doesn't record specific metrics for unknown endpoints"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/unknown/endpoint"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_inventory_request.assert_called_once()
            mock_collector.record_asset_operation.assert_not_called()
            mock_collector.record_api_call.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        """Test middleware calculates duration correctly"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.05)  # 50ms delay
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            call_args = mock_collector.record_inventory_request.call_args[0]
            duration = call_args[2]
            assert duration >= 0.05
            assert duration < 0.1
