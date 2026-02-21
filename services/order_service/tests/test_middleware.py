"""
Unit tests for Order Service Middleware functionality - 3 metrics: record_request only.
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi import Request, Response

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from dependency_constants import PATCH_METRICS_COLLECTOR
from src.api_info_enum import ApiPaths


class TestMetricsMiddleware:
    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/orders"
        mock_request.method = "POST"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201

        async def mock_call_next(request):
            return mock_response

        with patch(PATCH_METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint="/orders",
                status_code="201",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/orders"
        mock_request.method = "POST"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400

        async def mock_call_next(request):
            return mock_response

        with patch(PATCH_METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint="/orders",
                status_code="400",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/orders"
        mock_request.method = "POST"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(PATCH_METRICS_COLLECTOR) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)
            mock_collector.record_request.assert_called_once_with(
                endpoint="/orders",
                status_code="500",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_internal_path_skipped(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.METRICS.value
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(PATCH_METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/orders"
        mock_request.method = "POST"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201

        async def mock_call_next(request):
            await asyncio.sleep(0.05)
            return mock_response

        with patch(PATCH_METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)
            call_kw = mock_collector.record_request.call_args[1]
            assert call_kw["duration"] >= 0.05
            assert call_kw["duration"] < 0.1
