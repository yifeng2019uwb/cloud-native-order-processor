"""
Tests for get_order controller
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.get_order import get_order, router
from src.api_models.order import GetOrderResponse, OrderData
from common.entities.order.enums import OrderType, OrderStatus
from common.exceptions import (
    OrderNotFoundException,
    InternalServerException
)


class TestGetOrder:
    """Test get_order function"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user data"""
        return {
            "username": "testuser",
            "user_id": "user123"
        }

    @pytest.fixture
    def mock_order_dao(self):
        """Mock order DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_user_dao(self):
        """Mock user DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_order(self):
        """Mock order object"""
        order = MagicMock()
        order.order_id = "order123"
        order.order_type = OrderType.MARKET_BUY
        order.asset_id = "BTC"
        order.quantity = Decimal("1.0")
        order.price = Decimal("50000.00")
        order.username = "testuser"
        order.created_at = datetime.now(timezone.utc)
        return order

    @pytest.mark.asyncio
    async def test_get_order_success(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao,
        mock_order
    ):
        """Test successful order retrieval"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate, \
             patch('src.controllers.get_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_order.return_value = mock_order

            # Test the function
            result = await get_order(
                order_id="order123",
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                user_dao=mock_user_dao
            )

            # Verify result
            assert result.success is True
            assert result.message == "Order retrieved successfully"
            assert result.data.order_id == "order123"
            assert result.data.asset_id == "BTC"
            assert result.data.quantity == Decimal("1.0")
            assert result.data.price == Decimal("50000.00")

            # Verify business validation was called
            mock_validate.assert_called_once_with(
                order_id="order123",
                username="testuser",
                order_dao=mock_order_dao,
                user_dao=mock_user_dao
            )

            # Verify DAO was called
            mock_order_dao.get_order.assert_called_once_with("order123")

            # Verify logging
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_get_order_unauthorized_access(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval with unauthorized access"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate, \
             patch('src.controllers.get_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None

            # Mock order with different username
            mock_order = MagicMock()
            mock_order.username = "otheruser"
            mock_order_dao.get_order.return_value = mock_order

            # Test that the exception is raised
            with pytest.raises(OrderNotFoundException, match="Order 'order123' not found"):
                await get_order(
                    order_id="order123",
                    current_user=mock_current_user,
                    order_dao=mock_order_dao,
                    user_dao=mock_user_dao
                )

            # Verify logging
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_order_not_found(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval when order not found"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate:

            # Setup mock to raise OrderNotFoundException
            mock_validate.side_effect = OrderNotFoundException("Order not found")

            # Test that the exception is raised
            with pytest.raises(OrderNotFoundException, match="Order not found"):
                await get_order(
                    order_id="nonexistent",
                    current_user=mock_current_user,
                    order_dao=mock_order_dao,
                    user_dao=mock_user_dao
                )

    @pytest.mark.asyncio
    async def test_get_order_unexpected_error(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval when unexpected error occurs"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate, \
             patch('src.controllers.get_order.logger') as mock_logger:

            # Setup mock to raise generic Exception
            mock_validate.side_effect = Exception("Unexpected error")

            # Test that the exception is raised
            with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
                await get_order(
                    order_id="order123",
                    current_user=mock_current_user,
                    order_dao=mock_order_dao,
                    user_dao=mock_user_dao
                )

            # Verify logging
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_order_different_user_order(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval for order belonging to different user"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate, \
             patch('src.controllers.get_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None

            # Mock order with different username
            mock_order = MagicMock()
            mock_order.username = "otheruser"
            mock_order_dao.get_order.return_value = mock_order

            # Test that the exception is raised
            with pytest.raises(OrderNotFoundException, match="Order 'order123' not found"):
                await get_order(
                    order_id="order123",
                    current_user=mock_current_user,
                    order_dao=mock_order_dao,
                    user_dao=mock_user_dao
                )

            # Verify logging
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_order_logging_and_metrics(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao,
        mock_order
    ):
        """Test order retrieval logging and metrics recording"""
        with patch('src.controllers.get_order.validate_order_retrieval_business_rules') as mock_validate, \
             patch('src.controllers.get_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_order.return_value = mock_order

            # Test the function
            result = await get_order(
                order_id="order123",
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                user_dao=mock_user_dao
            )

            # Verify logging was called for successful retrieval
            mock_logger.info.assert_called()

    def test_router_configuration(self):
        """Test router configuration"""
        # Test router tags
        assert router.tags == ["orders"]

        # Test endpoint path
        assert router.routes[0].path == "/{order_id}"

        # Test HTTP method
        assert router.routes[0].methods == {"GET"}

        # Test response models
        assert router.routes[0].response_model is not None

        # Test responses documentation
        assert router.routes[0].responses is not None
        assert 200 in router.routes[0].responses
        assert 401 in router.routes[0].responses
        assert 404 in router.routes[0].responses
        assert 500 in router.routes[0].responses
