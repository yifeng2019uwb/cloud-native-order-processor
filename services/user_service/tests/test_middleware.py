"""
Unit tests for User Service Middleware functionality
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import Request, Response

from .utils.dependency_constants import METRICS_COLLECTOR

class TestMetricsMiddleware:
    """Test cases for metrics middleware functionality"""

    @pytest.mark.asyncio
    async def test_successful_request_metrics(self):
        """Test middleware records metrics for successful requests"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/auth/login"
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_user_request.assert_called_once()
            mock_collector.record_auth_operation.assert_called_once_with("login", "success", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_error_response_metrics(self):
        """Test middleware records metrics for error responses"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/auth/login"
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400

        async def mock_call_next(request):
            return mock_response

        with patch('src.middleware.metrics_collector') as mock_collector:
            result = await metrics_middleware(mock_request, mock_call_next)

            assert result == mock_response
            mock_collector.record_user_request.assert_called_once()
            mock_collector.record_auth_operation.assert_called_once_with("login", "error", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test middleware handles exceptions and records error metrics"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/auth/login"
        mock_request.method = "POST"

        async def mock_call_next(request):
            raise ValueError("Test exception")

        with patch(METRICS_COLLECTOR) as mock_collector:
            with pytest.raises(ValueError):
                await metrics_middleware(mock_request, mock_call_next)

            mock_collector.record_user_request.assert_called_once()
            mock_collector.record_auth_operation.assert_called_once_with("login", "error", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_auth_endpoint_detection(self):
        """Test middleware detects auth endpoints correctly"""
        from src.middleware import metrics_middleware

        test_cases = [
            ("/auth/login", "login"),
            ("/auth/register", "register"),
            ("/auth/logout", "logout"),
            ("/auth/profile", "profile"),
        ]

        for endpoint, expected_op in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.url.path = endpoint
            mock_request.method = "POST"

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200

            async def mock_call_next(request):
                return mock_response

            with patch('src.middleware.metrics_collector') as mock_collector:
                await metrics_middleware(mock_request, mock_call_next)
                mock_collector.record_auth_operation.assert_called_with(expected_op, "success", pytest.approx(0.0, abs=0.1))

    @pytest.mark.asyncio
    async def test_balance_endpoint_detection(self):
        """Test middleware detects balance endpoints correctly"""
        from src.middleware import metrics_middleware

        test_cases = [
            ("/balance", "GET", "get_balance"),
            ("/balance", "POST", "balance_operation"),
            ("/deposit", "POST", "deposit"),
            ("/withdraw", "POST", "withdraw"),
        ]

        for endpoint, method, expected_op in test_cases:
            mock_request = MagicMock(spec=Request)
            mock_request.url.path = endpoint
            mock_request.method = method

            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200

            async def mock_call_next(request):
                return mock_response

            with patch(METRICS_COLLECTOR) as mock_collector:
                await metrics_middleware(mock_request, mock_call_next)
                mock_collector.record_balance_operation.assert_called_with(expected_op, "success", pytest.approx(0.0, abs=0.1))

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

            mock_collector.record_user_request.assert_called_once()
            mock_collector.record_auth_operation.assert_not_called()
            mock_collector.record_balance_operation.assert_not_called()

    @pytest.mark.asyncio
    async def test_duration_calculation(self):
        """Test middleware calculates duration correctly"""
        from src.middleware import metrics_middleware

        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/auth/login"
        mock_request.method = "POST"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.05)  # 50ms delay
            return mock_response

        with patch(METRICS_COLLECTOR) as mock_collector:
            await metrics_middleware(mock_request, mock_call_next)

            call_args = mock_collector.record_user_request.call_args[0]
            duration = call_args[2]
            assert duration >= 0.05
            assert duration < 0.1
