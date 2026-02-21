"""
Unit tests for Auth Service Middleware functionality - 3 metrics: record_request only.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response
from tests.utils.dependency_constants import AUTH_SERVICE_MIDDLEWARE_METRICS


class TestMetricsMiddleware:
    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint="/some/endpoint",
                status_code="200",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400

        async def mock_call_next(request):
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint="/some/endpoint",
                status_code="400",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_validate_endpoint_metrics(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/internal/auth/validate"
        mock_request.method = "POST"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_called_once_with(
                endpoint="/internal/auth/validate",
                status_code="200",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)
            mock_collector.record_request.assert_called_once_with(
                endpoint="/some/endpoint",
                status_code="500",
                duration=pytest.approx(0.0, abs=0.1),
            )

    @pytest.mark.asyncio
    async def test_internal_path_skipped(self):
        from src.middleware import metrics_middleware
        from src.api_info_enum import ApiPaths

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = ApiPaths.METRICS.value
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)
            assert result == mock_response
            mock_collector.record_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.05)
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)
            call_kw = mock_collector.record_request.call_args[1]
            assert call_kw["duration"] >= 0.05
            assert call_kw["duration"] < 0.1
