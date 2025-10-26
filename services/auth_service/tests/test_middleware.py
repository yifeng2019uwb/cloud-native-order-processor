"""
Unit tests for Auth Service Middleware functionality
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response
from tests.utils.dependency_constants import AUTH_SERVICE_MIDDLEWARE_METRICS

class TestMetricsMiddleware:
    """Test cases for metrics middleware functionality"""

    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        """Test middleware records metrics for successful requests"""
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
            mock_collector.record_request.assert_called_once()
            mock_collector.record_jwt_validation.assert_not_called()

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        """Test middleware records metrics for error responses"""
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
            mock_collector.record_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_endpoint_metrics(self):
        """Test middleware records JWT validation metrics for validate endpoint"""
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
            mock_collector.record_request.assert_called_once()
            mock_collector.record_jwt_validation.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test middleware handles exceptions and records error metrics"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_endpoint_exception(self):
        """Test middleware handles exceptions for validate endpoint"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/internal/auth/validate"
        mock_request.method = "POST"

        async def mock_call_next(request):
            raise ValueError("Validation error")

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_request.assert_called_once()
            mock_collector.record_jwt_validation.assert_called_once()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        """Test middleware calculates duration correctly"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/some/endpoint"
        mock_request.method = "GET"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.05)  # 50ms delay
            return mock_response

        with patch(AUTH_SERVICE_MIDDLEWARE_METRICS) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            call_args = mock_collector.record_request.call_args[0]
            duration = call_args[1]
            assert duration >= 0.05
            assert duration < 0.1
