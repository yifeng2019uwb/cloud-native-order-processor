"""
Unit tests for LLM service
"""
import pytest
import os
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.services.llm_service import LLMService
from src.api_models.insights.portfolio_context import PortfolioContext, HoldingData, OrderData
from src.constants import (
    LLM_API_KEY_ENV_VAR,
    LLM_MODEL_NAME,
    LLM_SYSTEM_PROMPT,
    PROMPT_HEADER,
    PROMPT_USD_BALANCE,
    PROMPT_TOTAL_VALUE,
    PROMPT_HOLDINGS_HEADER,
    PROMPT_RECENT_ACTIVITY_HEADER,
    PROMPT_SUMMARY_INSTRUCTION
)

# Test constants
TEST_API_KEY = "test-api-key-12345"
TEST_SUMMARY = "Your portfolio is well-diversified."
TEST_USERNAME = "testuser"

# Patch path constants
PATCH_PATH_LLM_SERVICE_GENAI = "src.services.llm_service.genai"
PATCH_PATH_LLM_SERVICE_LOGGER = "src.services.llm_service.logger"


class TestLLMService:
    """Test LLM service"""

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

    @patch(PATCH_PATH_LLM_SERVICE_LOGGER)
    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE_GENAI)
    def test_llm_service_initialization_success(self, mock_genai, mock_logger):
        """Test LLM service initializes successfully"""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        service = LLMService()

        assert service.model == mock_model
        mock_genai.configure.assert_called_once_with(api_key=TEST_API_KEY)
        mock_genai.GenerativeModel.assert_called_once_with(LLM_MODEL_NAME)

    @patch.dict(os.environ, {}, clear=True)
    def test_llm_service_initialization_no_api_key(self):
        """Test LLM service raises error when API key not configured"""
        with pytest.raises(ValueError) as exc_info:
            LLMService()

        assert LLM_API_KEY_ENV_VAR in str(exc_info.value)

    @patch(PATCH_PATH_LLM_SERVICE_LOGGER)
    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE_GENAI)
    def test_generate_insights_success(self, mock_genai, mock_logger, mock_portfolio_context):
        """Test successful insights generation"""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = f"  {TEST_SUMMARY}  "  # Test strip()

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        service = LLMService()
        result = service.generate_insights(mock_portfolio_context)

        assert result == TEST_SUMMARY
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args
        assert call_args.kwargs['system_instruction'] == LLM_SYSTEM_PROMPT

    @patch(PATCH_PATH_LLM_SERVICE_LOGGER)
    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE_GENAI)
    def test_build_prompt_with_holdings(self, mock_genai, mock_logger, mock_portfolio_context):
        """Test prompt building includes holdings"""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        service = LLMService()
        prompt = service._build_prompt(mock_portfolio_context)

        assert PROMPT_HEADER in prompt
        assert PROMPT_USD_BALANCE in prompt
        assert PROMPT_TOTAL_VALUE in prompt
        assert PROMPT_HOLDINGS_HEADER in prompt
        assert PROMPT_SUMMARY_INSTRUCTION in prompt
        assert "BTC" in prompt
        assert "45.0%" in prompt

    @patch(PATCH_PATH_LLM_SERVICE_LOGGER)
    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE_GENAI)
    def test_build_prompt_with_orders(self, mock_genai, mock_logger):
        """Test prompt building includes recent orders"""
        context = PortfolioContext(
            username=TEST_USERNAME,
            account_age_days=45,
            usd_balance=Decimal("5000.00"),
            total_portfolio_value=Decimal("15000.00"),
            holdings=[],
            recent_orders=[
                OrderData(
                    order_type="MARKET_BUY",
                    asset_id="BTC",
                    quantity=Decimal("0.05"),
                    price=Decimal("44000"),
                    created_at=datetime(2026, 1, 30, 14, 0, 0, tzinfo=timezone.utc)
                )
            ]
        )

        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        service = LLMService()
        prompt = service._build_prompt(context)

        assert PROMPT_RECENT_ACTIVITY_HEADER in prompt
        assert "MARKET_BUY" in prompt
        assert "BTC" in prompt

    @patch(PATCH_PATH_LLM_SERVICE_LOGGER)
    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE_GENAI)
    def test_generate_insights_api_error(self, mock_genai, mock_logger, mock_portfolio_context):
        """Test error handling when LLM API fails"""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_genai.GenerativeModel.return_value = mock_model

        service = LLMService()

        with pytest.raises(Exception):
            service.generate_insights(mock_portfolio_context)
