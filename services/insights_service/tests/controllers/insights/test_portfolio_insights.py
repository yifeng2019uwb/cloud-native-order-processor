"""
Unit tests for portfolio insights controller
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException
from common.shared.constants.api_constants import HTTPStatus
from src.controllers.insights.portfolio_insights import get_portfolio_insights, router
from src.api_models.insights.insights_models import GetInsightsResponse, InsightsData
from src.api_models.insights.portfolio_context import PortfolioContext, HoldingData
from src.api_info_enum import ApiPaths, ApiTags
from src.constants import (
    MSG_ERROR_INSIGHTS_NOT_CONFIGURED,
    MSG_ERROR_EMPTY_PORTFOLIO,
    MSG_ERROR_INSIGHTS_TIMEOUT,
    MSG_ERROR_INSIGHTS_RATE_LIMITED,
    MSG_ERROR_INSIGHTS_FAILED,
    MSG_ERROR_UNEXPECTED,
    MSG_ERROR_USER_NOT_FOUND,
    MSG_ERROR_LLM_BLOCKED,
    LLM_MODEL_NAME,
    ERROR_KEYWORD_TIMEOUT,
    ERROR_KEYWORD_TIMED_OUT,
    ERROR_KEYWORD_RATE_LIMIT,
    ERROR_CODE_RATE_LIMIT
)

# Test constants
TEST_USERNAME = "testuser"
TEST_SUMMARY = "Your portfolio is well-diversified with 45% in BTC."

# Patch path constants
PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR = "src.controllers.insights.portfolio_insights.get_data_aggregator"
PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE = "src.controllers.insights.portfolio_insights.get_llm_service"
PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER = "src.controllers.insights.portfolio_insights.logger"
PATCH_PATH_INSIGHTS_CACHE_GET_CACHED = "src.controllers.insights.portfolio_insights.get_cached"


class TestPortfolioInsightsController:
    """Test portfolio insights controller"""

    @pytest.fixture(autouse=True)
    def clear_insights_cache(self):
        """Clear in-memory insights cache before each test to avoid cross-test pollution"""
        from src.services.insights_cache import clear_cache
        clear_cache()
        yield

    @pytest.fixture
    def mock_portfolio_context(self):
        """Mock portfolio context"""
        return PortfolioContext(
            username=TEST_USERNAME,
            account_age_days=45,
            usd_balance=Decimal("5000.00"),
            total_portfolio_value=Decimal("15000.00"),
            holdings=[
                HoldingData(
                    asset_id="BTC",
                    quantity=Decimal("0.15"),
                    current_price=Decimal("45000"),
                    price_change_24h_pct=Decimal("2.5"),
                    value_usd=Decimal("6750"),
                    allocation_pct=Decimal("45.0")
                )
            ],
            recent_orders=[]
        )

    @pytest.fixture
    def mock_empty_portfolio_context(self):
        """Mock empty portfolio context"""
        return PortfolioContext(
            username=TEST_USERNAME,
            account_age_days=45,
            usd_balance=Decimal("0"),
            total_portfolio_value=Decimal("0"),
            holdings=[],
            recent_orders=[]
        )

    def test_router_configuration(self):
        """Test router is properly configured"""
        assert router.tags == [ApiTags.INSIGHTS.value]
        routes = [r for r in router.routes if hasattr(r, 'path')]
        assert any(ApiPaths.PORTFOLIO_INSIGHTS.value in str(r.path) for r in routes)

    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_success(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context
    ):
        """Test successful insights generation"""
        # Setup mocks
        mock_llm_service = MagicMock()
        mock_llm_service.generate_insights.return_value = TEST_SUMMARY
        mock_get_llm_service.return_value = mock_llm_service
        
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator

        # Call function
        result = get_portfolio_insights(
            current_user=mock_current_user,
            data_aggregator=mock_aggregator,
            llm_service=mock_llm_service
        )

        # Assertions - Check attributes instead of isinstance (Pydantic model comparison issue)
        assert hasattr(result, 'data')
        assert result.data.summary == TEST_SUMMARY
        assert result.data.model == LLM_MODEL_NAME
        assert isinstance(result.data.generated_at, datetime)
        mock_aggregator.aggregate_portfolio_data.assert_called_once_with(TEST_USERNAME)
        mock_llm_service.generate_insights.assert_called_once()

    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_empty_portfolio(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_empty_portfolio_context
    ):
        """Test empty portfolio returns early without LLM call"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_empty_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_get_llm_service.return_value = mock_llm_service

        result = get_portfolio_insights(
            current_user=mock_current_user,
            data_aggregator=mock_aggregator,
            llm_service=mock_llm_service
        )

        # Check response structure (Pydantic models may have isinstance issues)
        assert hasattr(result, 'data')
        assert result.data.summary == MSG_ERROR_EMPTY_PORTFOLIO
        assert result.data.model == LLM_MODEL_NAME
        assert isinstance(result.data.generated_at, datetime)
        # LLM should not be called for empty portfolio
        mock_llm_service.generate_insights.assert_not_called()

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_cache_hit(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_current_user,
        mock_portfolio_context
    ):
        """Test cache hit returns cached result without calling LLM"""
        from datetime import datetime, timezone

        cached_summary = "Cached insights from previous request"
        cached_at = datetime.now(timezone.utc)

        def mock_get_cached(username, portfolio_hash):
            return (cached_summary, cached_at, LLM_MODEL_NAME)

        with patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, side_effect=mock_get_cached):
            mock_aggregator = MagicMock()
            mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
            mock_get_data_aggregator.return_value = mock_aggregator
            mock_llm_service = MagicMock()
            mock_get_llm_service.return_value = mock_llm_service

            result = get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert result.data.summary == cached_summary
        mock_llm_service.generate_insights.assert_not_called()

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_no_llm_service(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_current_user
    ):
        """Test 503 when LLM service not configured"""
        mock_aggregator = MagicMock()
        mock_get_data_aggregator.return_value = mock_aggregator
        mock_get_llm_service.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=None
            )

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert exc_info.value.detail == MSG_ERROR_INSIGHTS_NOT_CONFIGURED

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_invalid_user(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger
    ):
        """Test 401 when user context is invalid"""
        invalid_user = MagicMock(username=None)  # Object with missing username
        
        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=invalid_user,
                data_aggregator=MagicMock(),
                llm_service=MagicMock()
            )

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize("error_keyword", [ERROR_KEYWORD_TIMEOUT, ERROR_KEYWORD_TIMED_OUT])
    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_llm_timeout(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context,
        error_keyword
    ):
        """Test timeout error from LLM service (both 'timeout' and 'timed out' variations)"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_llm_service.generate_insights.side_effect = Exception(f"Request {error_keyword}")
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == MSG_ERROR_INSIGHTS_TIMEOUT
        mock_logger.error.assert_called()

    @pytest.mark.parametrize("error_message", [
        f"{ERROR_KEYWORD_RATE_LIMIT} exceeded",
        f"Error {ERROR_CODE_RATE_LIMIT}"
    ])
    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_llm_rate_limit(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context,
        error_message
    ):
        """Test rate limit error from LLM service (both keyword and error code variations)"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_llm_service.generate_insights.side_effect = Exception(error_message)
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert exc_info.value.detail == MSG_ERROR_INSIGHTS_RATE_LIMITED

    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_llm_other_error(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context
    ):
        """Test other error from LLM service"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        test_error_message = "Some other LLM error"
        mock_llm_service.generate_insights.side_effect = Exception(test_error_message)
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == MSG_ERROR_INSIGHTS_FAILED
        mock_logger.error.assert_called()

    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_llm_blocked(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context
    ):
        """Test 429 when LLM raises ValueError with MSG_ERROR_LLM_BLOCKED (content filtering)"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator

        mock_llm_service = MagicMock()
        mock_llm_service.generate_insights.side_effect = ValueError(MSG_ERROR_LLM_BLOCKED)
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert exc_info.value.detail == MSG_ERROR_LLM_BLOCKED
        mock_logger.warning.assert_called()

    @patch(PATCH_PATH_INSIGHTS_CACHE_GET_CACHED, return_value=None)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_llm_value_error(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_get_cached,
        mock_current_user,
        mock_portfolio_context
    ):
        """Test 500 when LLM raises ValueError (non-blocked, e.g. invalid response)"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.return_value = mock_portfolio_context
        mock_get_data_aggregator.return_value = mock_aggregator

        mock_llm_service = MagicMock()
        mock_llm_service.generate_insights.side_effect = ValueError("Invalid response format")
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == MSG_ERROR_INSIGHTS_FAILED
        mock_logger.error.assert_called()

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_user_not_found(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_current_user
    ):
        """Test ValueError when user not found"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.side_effect = ValueError(MSG_ERROR_USER_NOT_FOUND)
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert MSG_ERROR_USER_NOT_FOUND in exc_info.value.detail
        mock_logger.warning.assert_called()

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_unexpected_error(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_current_user
    ):
        """Test unexpected exception handling"""
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_portfolio_data.side_effect = RuntimeError("Unexpected error")
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert MSG_ERROR_UNEXPECTED in exc_info.value.detail
        mock_logger.error.assert_called()

    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_LOGGER)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_DATA_AGGREGATOR)
    @patch(PATCH_PATH_PORTFOLIO_INSIGHTS_GET_LLM_SERVICE)
    def test_get_portfolio_insights_http_exception_re_raise(
        self,
        mock_get_llm_service,
        mock_get_data_aggregator,
        mock_logger,
        mock_current_user
    ):
        """Test HTTPException is re-raised without modification"""
        mock_aggregator = MagicMock()
        test_http_exception = HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Test HTTP exception"
        )
        mock_aggregator.aggregate_portfolio_data.side_effect = test_http_exception
        mock_get_data_aggregator.return_value = mock_aggregator
        
        mock_llm_service = MagicMock()
        mock_get_llm_service.return_value = mock_llm_service

        with pytest.raises(HTTPException) as exc_info:
            get_portfolio_insights(
                current_user=mock_current_user,
                data_aggregator=mock_aggregator,
                llm_service=mock_llm_service
            )

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == "Test HTTP exception"
