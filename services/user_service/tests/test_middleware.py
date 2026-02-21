"""
Unit tests for User Service Middleware functionality - 3 metrics: record_request only.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response

from common.shared.constants.api_constants import HTTPStatus
from src.api_info_enum import ApiPaths

from .utils.dependency_constants import METRICS_COLLECTOR


class TestMetricsMiddleware:
    """Test cases for metrics middleware functionality"""

    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        """Test middleware records metrics for successful requests"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.LOGIN.value
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = HTTPStatus.OK

        async def mock_call_next(request):
            return mock_response

        with patch(METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint=ApiPaths.LOGIN.value,
                status_code=str(HTTPStatus.OK),
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        """Test middleware records metrics for error responses"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.LOGIN.value
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = HTTPStatus.BAD_REQUEST

        async def mock_call_next(request):
            return mock_response

        with patch(METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint=ApiPaths.LOGIN.value,
                status_code=str(HTTPStatus.BAD_REQUEST),
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test middleware handles exceptions and records error metrics"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.LOGIN.value
        mock_request.method = "POST"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(METRICS_COLLECTOR) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_request.assert_called_once_with(
                endpoint=ApiPaths.LOGIN.value,
                status_code="500",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_internal_path_skipped(self):
        """Test middleware skips recording for internal paths"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.METRICS.value

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = HTTPStatus.OK

        async def mock_call_next(request):
            return mock_response

        with patch(METRICS_COLLECTOR) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        """Test middleware calculates duration correctly for record_request"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.LOGIN.value
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = HTTPStatus.OK

        async def mock_call_next(request):
            await asyncio.sleep(0.05)  # 50ms delay
            return mock_response

        with patch(METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            call_kw = mock_collector.record_request.call_args[1]
            duration = call_kw["duration"]
            assert duration >= 0.05
            assert duration < 0.1
