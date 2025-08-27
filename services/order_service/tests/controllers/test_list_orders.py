"""
Tests for list_orders controller
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.list_orders import list_orders, router
from src.api_models.order import OrderListResponse, OrderSummary
from common.data.entities.order.enums import OrderType, OrderStatus
from common.exceptions import CNOPInternalServerException


class TestListOrders:
    """Test list_orders function"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user data"""
        return {
            "username": "testuser"
        }

    @pytest.fixture
    def mock_order_dao(self):
        """Mock order DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_asset_dao(self):
        """Mock asset DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_user_dao(self):
        """Mock user DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_orders(self):
        """Mock order objects"""
        orders = []
        for i in range(3):
            order = MagicMock()
            order.order_id = f"order{i+1}"
            order.order_type = OrderType.MARKET_BUY if i % 2 == 0 else OrderType.MARKET_SELL
            order.asset_id = "BTC" if i % 2 == 0 else "ETH"
            order.quantity = Decimal(f"{1.0 + i}")
            order.price = Decimal(f"{50000.00 + i * 1000}")
            order.created_at = datetime.now(timezone.utc)
            orders.append(order)
        return orders

    def test_list_orders_success(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test successful order listing"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate, \
             patch('src.controllers.list_orders.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function
            result = list_orders(
                asset_id=None,
                order_type=None,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result
            assert result.success is True
            assert result.message == "Orders retrieved successfully"
            assert len(result.data) == 3
            assert result.has_more is False  # 3 orders < limit of 50

            # Verify business validation was called
            mock_validate.assert_called_once_with(
                username="testuser",
                status=None,
                asset_id=None,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify DAO was called
            mock_order_dao.get_orders_by_user.assert_called_once_with("testuser")

            # Verify logging
            mock_logger.info.assert_called()


    def test_list_orders_with_asset_filter(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with asset filter"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function with BTC filter
            result = list_orders(
                asset_id="BTC",
                order_type=None,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result - should only have BTC orders
            assert result.success is True
            assert len(result.data) == 2  # 2 BTC orders

            # Verify business validation was called with asset filter
            mock_validate.assert_called_once_with(
                username="testuser",
                status=None,
                asset_id="BTC",
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )


    def test_list_orders_with_order_type_filter(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with order type filter"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function with MARKET_BUY filter
            result = list_orders(
                asset_id=None,
                order_type=OrderType.MARKET_BUY,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result - should only have MARKET_BUY orders
            assert result.success is True
            assert len(result.data) == 2  # 2 MARKET_BUY orders

            # Verify business validation was called
            mock_validate.assert_called_once_with(
                username="testuser",
                status=None,
                asset_id=None,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )


    def test_list_orders_with_pagination(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with pagination"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function with limit=2 and offset=1
            result = list_orders(
                asset_id=None,
                order_type=None,
                limit=2,
                offset=1,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result - should have 2 orders starting from offset 1
            assert result.success is True
            assert len(result.data) == 2
            # has_more is True when len(paginated_orders) == limit
            # Since we have 3 total orders, limit=2, offset=1, we get 2 orders
            # has_more should be True because we got exactly the limit
            assert result.has_more is True

            # Verify business validation was called
            mock_validate.assert_called_once_with(
                username="testuser",
                status=None,
                asset_id=None,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )


    def test_list_orders_with_combined_filters(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with combined filters"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function with both asset and order type filters
            result = list_orders(
                asset_id="BTC",
                order_type=OrderType.MARKET_BUY,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result - should only have BTC MARKET_BUY orders
            # From mock_orders: order1 (BTC, MARKET_BUY), order3 (BTC, MARKET_BUY)
            # So 2 BTC MARKET_BUY orders match both filters
            assert result.success is True
            assert len(result.data) == 2  # 2 BTC MARKET_BUY orders

            # Verify business validation was called
            mock_validate.assert_called_once_with(
                username="testuser",
                status=None,
                asset_id="BTC",
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )


    def test_list_orders_empty_result(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao
    ):
        """Test order listing with empty result"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate, \
             patch('src.controllers.list_orders.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = []

            # Test the function
            result = list_orders(
                asset_id=None,
                order_type=None,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result
            assert result.success is True
            assert result.message == "Orders retrieved successfully"
            assert len(result.data) == 0
            assert result.has_more is False

            # Verify logging
            mock_logger.info.assert_called()


    def test_list_orders_has_more_true(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao
    ):
        """Test order listing with has_more=True"""
        # Create more orders than the limit
        many_orders = []
        for i in range(60):  # More than limit of 50
            order = MagicMock()
            order.order_id = f"order{i+1}"
            order.order_type = OrderType.MARKET_BUY
            order.asset_id = "BTC"
            order.quantity = Decimal("1.0")
            order.price = Decimal("50000.00")
            order.created_at = datetime.now(timezone.utc)
            many_orders.append(order)

        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = many_orders

            # Test the function with limit=50
            result = list_orders(
                asset_id=None,
                order_type=None,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify result
            assert result.success is True
            assert len(result.data) == 50
            assert result.has_more is True  # 50 orders = limit of 50


    def test_list_orders_unexpected_error(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao
    ):
        """Test order listing when unexpected error occurs"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate, \
             patch('src.controllers.list_orders.logger') as mock_logger:

            # Setup mock to raise generic Exception
            mock_validate.side_effect = Exception("Unexpected error")

            # Test that the exception is raised
            with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
                list_orders(
                    asset_id=None,
                    order_type=None,
                    limit=50,
                    offset=0,
                    current_user=mock_current_user,
                    order_dao=mock_order_dao,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao
                )

            # Verify logging
            mock_logger.error.assert_called()


    def test_list_orders_logging_and_metrics(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing logging and metrics recording"""
        with patch('src.controllers.list_orders.validate_order_listing_business_rules') as mock_validate, \
             patch('src.controllers.list_orders.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_order_dao.get_orders_by_user.return_value = mock_orders

            # Test the function
            result = list_orders(
                asset_id=None,
                order_type=None,
                limit=50,
                offset=0,
                current_user=mock_current_user,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify logging was called for successful listing
            mock_logger.info.assert_called()

    def test_router_configuration(self):
        """Test router configuration"""
        # Test router tags
        assert router.tags == ["orders"]

        # Test endpoint path
        assert router.routes[0].path == "/"

        # Test HTTP method
        assert router.routes[0].methods == {"GET"}

        # Test response models
        assert router.routes[0].response_model is not None

        # Test responses documentation
        assert router.routes[0].responses is not None
        assert 200 in router.routes[0].responses
        assert 401 in router.routes[0].responses
        assert 500 in router.routes[0].responses
