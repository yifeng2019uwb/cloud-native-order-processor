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
from src.api_models.list_orders import ListOrdersRequest, ListOrdersResponse
from src.api_models.shared.data_models import OrderSummary
from common.data.entities.order.enums import OrderType, OrderStatus
from common.data.entities.user import User
from common.exceptions import CNOPInternalServerException


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request


class TestListOrders:
    """Test list_orders function"""

    # Shared constants (used in multiple tests/fixtures)
    TEST_USERNAME = "testuser"
    TEST_EMAIL = "test@example.com"
    TEST_PASSWORD = "hashed_password_123"
    TEST_FIRST_NAME = "Test"
    TEST_LAST_NAME = "User"
    TEST_ROLE_CUSTOMER = "customer"

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user data"""
        return User(
            username=self.TEST_USERNAME,
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME,
            role=self.TEST_ROLE_CUSTOMER
        )

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
        asset_ids = ["BTC", "ETH"]
        orders = []

        for i in range(3):
            order_id = f"order{i+1}"
            asset_id = asset_ids[i % 2]

            order = MagicMock()
            order.order_id = order_id
            order.order_type = OrderType.MARKET_BUY if i % 2 == 0 else OrderType.MARKET_SELL
            order.asset_id = asset_id
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

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
            filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result
        assert result.data is not None
        assert len(result.data) == 3
        assert result.has_more is False  # 3 orders < limit of 50

        # Verify DAO was called
        mock_order_dao.get_orders_by_user.assert_called_once_with("testuser")


    def test_list_orders_with_asset_filter(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with asset filter"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function with BTC filter
        filter_params = ListOrdersRequest(asset_id="BTC", order_type=None, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
        filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result - should only have BTC orders
        assert result.data is not None
        assert len(result.data) == 2  # 2 BTC orders


    def test_list_orders_with_order_type_filter(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with order type filter"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function with MARKET_BUY filter
        filter_params = ListOrdersRequest(asset_id=None, order_type=OrderType.MARKET_BUY, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
        filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result - should only have MARKET_BUY orders
        assert result.data is not None
        assert len(result.data) == 2  # 2 MARKET_BUY orders



    def test_list_orders_with_pagination(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with pagination"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function with limit=2 and offset=1
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=2, offset=1)
        result = list_orders(
            request=create_mock_request(),
            filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result - should have 2 orders starting from offset 1
        assert result.data is not None
        assert len(result.data) == 2
        # has_more is True when len(paginated_orders) == limit
        # Since we have 3 total orders, limit=2, offset=1, we get 2 orders
        # has_more should be True because we got exactly the limit
        assert result.has_more is True



    def test_list_orders_with_combined_filters(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing with combined filters"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function with both asset and order type filters
        filter_params = ListOrdersRequest(asset_id="BTC", order_type=OrderType.MARKET_BUY, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
            filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result - should only have BTC MARKET_BUY orders
        # From mock_orders: order1 (BTC, MARKET_BUY), order3 (BTC, MARKET_BUY)
        # So 2 BTC MARKET_BUY orders match both filters
        assert result.data is not None
        assert len(result.data) == 2  # 2 BTC MARKET_BUY orders


    def test_list_orders_empty_result(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao
    ):
        """Test order listing with empty result"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = []

        # Test the function
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
            filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result
        assert result.data is not None
        assert len(result.data) == 0
        assert result.has_more is False



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


        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = many_orders

        # Test the function with limit=50
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
                filter_params=filter_params,
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )

        # Verify result
        assert result.data is not None
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

        # Setup mock to raise generic Exception
        mock_order_dao.get_orders_by_user.side_effect = Exception("Unexpected error")

        # Test that the exception is raised
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=50, offset=0)
        with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable"):
            list_orders(
            request=create_mock_request(),
                filter_params=filter_params,
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )


    def test_list_orders_logging_and_metrics(
        self,
        mock_current_user,
        mock_order_dao,
        mock_asset_dao,
        mock_user_dao,
        mock_orders
    ):
        """Test order listing logging and metrics recording"""

        # Setup mocks
        mock_order_dao.get_orders_by_user.return_value = mock_orders

        # Test the function
        filter_params = ListOrdersRequest(asset_id=None, order_type=None, limit=50, offset=0)
        result = list_orders(
            request=create_mock_request(),
            filter_params=filter_params,
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )
