"""
Unit tests for Inventory Service Middleware - 3 metrics (requests, errors, latency).
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response

from .dependency_constants import PATH_METRICS_COLLECTOR
from src.api_info_enum import ApiPaths


class TestMetricsMiddleware:
    @pytest.mark.asyncio
    async def test_successful_request_records_once(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.ASSETS.value
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(PATH_METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once()
            args = mock_collector.record_request.call_args
            assert args[1]["endpoint"] == ApiPaths.ASSETS.value
            assert args[1]["status_code"] == "200"

    @pytest.mark.asyncio
    async def test_error_response_records_with_status_code(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400

        async def mock_call_next(request):
            return mock_response

        with patch(PATH_METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)
            mock_collector.record_request.assert_called_once_with(
                endpoint="/inventory/assets", status_code="400", duration=pytest.approx(0.0, abs=0.1)
            )

    @pytest.mark.asyncio
    async def test_exception_records_500(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/inventory/assets"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(PATH_METRICS_COLLECTOR) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)
            mock_collector.record_request.assert_called_once()
            assert mock_collector.record_request.call_args[1]["status_code"] == "500"

    @pytest.mark.asyncio
    async def test_internal_path_skips_recording(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.METRICS.value
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(PATH_METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)
            mock_collector.record_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_passed(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.ASSETS.value
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.05)
            return mock_response

        with patch(PATH_METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)
            call_kw = mock_collector.record_request.call_args[1]
            assert call_kw["duration"] >= 0.05
            assert call_kw["duration"] < 0.1
