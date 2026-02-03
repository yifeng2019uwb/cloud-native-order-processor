"""
Unit tests for controller dependencies
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from src.controllers.dependencies import get_data_aggregator, get_llm_service
from src.services.data_aggregator import DataAggregator
from src.services.llm_service import LLMService
from src.constants import (
    LLM_API_KEY_ENV_VAR,
    MSG_ERROR_LLM_API_KEY_NOT_CONFIGURED
)

# Test constants
TEST_API_KEY = "test-api-key"
TEST_ERROR_MESSAGE_API_KEY_NOT_CONFIGURED = f"API key {MSG_ERROR_LLM_API_KEY_NOT_CONFIGURED}"

# Patch path constants
PATCH_PATH_GET_USER_DAO = "src.controllers.dependencies.get_user_dao"
PATCH_PATH_GET_BALANCE_DAO = "src.controllers.dependencies.get_balance_dao"
PATCH_PATH_GET_ASSET_BALANCE_DAO = "src.controllers.dependencies.get_asset_balance_dao"
PATCH_PATH_GET_ASSET_DAO = "src.controllers.dependencies.get_asset_dao"
PATCH_PATH_GET_ORDER_DAO = "src.controllers.dependencies.get_order_dao"
PATCH_PATH_LLM_SERVICE = "src.controllers.dependencies.LLMService"


class TestDependencies:
    """Test dependency injection functions"""

    @patch(PATCH_PATH_GET_ORDER_DAO)
    @patch(PATCH_PATH_GET_ASSET_DAO)
    @patch(PATCH_PATH_GET_ASSET_BALANCE_DAO)
    @patch(PATCH_PATH_GET_BALANCE_DAO)
    @patch(PATCH_PATH_GET_USER_DAO)
    def test_get_data_aggregator(
        self,
        mock_get_user_dao,
        mock_get_balance_dao,
        mock_get_asset_balance_dao,
        mock_get_asset_dao,
        mock_get_order_dao
    ):
        """Test get_data_aggregator returns DataAggregator instance"""
        # Clear cache before test
        get_data_aggregator.cache_clear()
        
        mock_user_dao = MagicMock()
        mock_balance_dao = MagicMock()
        mock_asset_balance_dao = MagicMock()
        mock_asset_dao = MagicMock()
        mock_order_dao = MagicMock()
        
        mock_get_user_dao.return_value = mock_user_dao
        mock_get_balance_dao.return_value = mock_balance_dao
        mock_get_asset_balance_dao.return_value = mock_asset_balance_dao
        mock_get_asset_dao.return_value = mock_asset_dao
        mock_get_order_dao.return_value = mock_order_dao

        result = get_data_aggregator()

        assert hasattr(result, 'user_dao')
        assert result.user_dao == mock_user_dao
        assert result.balance_dao == mock_balance_dao
        assert result.asset_balance_dao == mock_asset_balance_dao
        assert result.asset_dao == mock_asset_dao
        assert result.order_dao == mock_order_dao

    @patch.dict(os.environ, {LLM_API_KEY_ENV_VAR: TEST_API_KEY})
    @patch(PATCH_PATH_LLM_SERVICE)
    def test_get_llm_service_success(self, mock_llm_service_class):
        """Test get_llm_service returns LLMService when configured"""
        # Clear cache before test
        get_llm_service.cache_clear()
        
        mock_service = MagicMock()
        mock_llm_service_class.return_value = mock_service

        result = get_llm_service()

        assert result == mock_service
        mock_llm_service_class.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch(PATCH_PATH_LLM_SERVICE)
    def test_get_llm_service_not_configured(self, mock_llm_service_class):
        """Test get_llm_service returns None when API key not configured"""
        # Clear cache before test
        get_llm_service.cache_clear()
        
        # Make the LLMService constructor raise ValueError
        mock_llm_service_class.side_effect = ValueError(TEST_ERROR_MESSAGE_API_KEY_NOT_CONFIGURED)

        result = get_llm_service()

        assert result is None
        mock_llm_service_class.assert_called_once()
