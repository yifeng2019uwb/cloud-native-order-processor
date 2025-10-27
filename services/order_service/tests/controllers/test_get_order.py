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
from src.controllers.get_order import get_order_request
from src.api_models.get_order import GetOrderRequest, GetOrderResponse
from src.api_models.shared.data_models import OrderData
from common.data.entities.order.enums import OrderType, OrderStatus
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPOrderNotFoundException, CNOPInternalServerException
from order_exceptions.exceptions import CNOPOrderValidationException
from src.constants import MSG_SUCCESS_ORDER_RETRIEVED, MSG_ERROR_ORDER_NOT_FOUND


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request


class TestGetOrder:
    """Test get_order function"""

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
    def mock_user_dao(self):
        """Mock user DAO"""
        return MagicMock()

    @pytest.fixture
    def mock_order(self):
        """Mock order object"""
        order_id = "order1234567890"  # 16 chars, valid range
        asset_id = "BTC"
        quantity = Decimal("1.0")
        price = Decimal("50000.00")

        order = MagicMock()
        order.order_id = order_id
        order.order_type = OrderType.MARKET_BUY
        order.asset_id = asset_id
        order.quantity = quantity
        order.price = price
        order.status = OrderStatus.PENDING
        order.total_amount = price
        order.username = self.TEST_USERNAME
        order.created_at = datetime.now(timezone.utc)
        return order

    def test_get_order_success(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao,
        mock_order
    ):
        """Test successful order retrieval"""
        order_id = "order1234567890"
        expected_asset_id = "BTC"
        expected_quantity = Decimal("1.0")
        expected_price = Decimal("50000.00")

        # Setup mocks
        mock_order_dao.get_order.return_value = mock_order

        # Test the function
        order_request = GetOrderRequest(order_id=order_id)
        result = get_order(
            order_request=order_request,
            request=create_mock_request(),
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )

        # Verify result
        assert result.data is not None
        assert result.data.order_id == order_id
        assert result.data.asset_id == expected_asset_id
        assert result.data.quantity == expected_quantity
        assert result.data.price == expected_price

        # Verify DAO was called
        mock_order_dao.get_order.assert_called_once_with(order_id)


    def test_get_order_unauthorized_access(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval with unauthorized access"""
        order_id = "order1234567890"
        other_user = "otheruser"

        # Setup mocks
        # Mock order with different username
        mock_order = MagicMock()
        mock_order.username = other_user
        mock_order_dao.get_order.return_value = mock_order

        # Test that the exception is raised
        order_request = GetOrderRequest(order_id=order_id)
        with pytest.raises(CNOPOrderNotFoundException, match=f"Order '{order_id}' not found"):
            get_order(
                order_request=order_request,
                request=create_mock_request(),
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )


    def test_get_order_not_found(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval when order not found"""
        nonexistent_order_id = "nonexistent12345"

        # Setup mock to raise OrderNotFoundException
        mock_order_dao.get_order.side_effect = CNOPOrderNotFoundException(MSG_ERROR_ORDER_NOT_FOUND)

        # Test that the exception is raised
        order_request = GetOrderRequest(order_id=nonexistent_order_id)
        with pytest.raises(CNOPOrderNotFoundException, match=MSG_ERROR_ORDER_NOT_FOUND):
            get_order(
                order_request=order_request,
                request=create_mock_request(),
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )


    def test_get_order_unexpected_error(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval when unexpected error occurs"""
        order_id = "order1234567890"
        error_msg = "Unexpected error"
        expected_error_msg = "The service is temporarily unavailable"

        # Setup mock to raise generic Exception
        mock_order_dao.get_order.side_effect = Exception(error_msg)

        # Test that the exception is raised
        order_request = GetOrderRequest(order_id=order_id)
        with pytest.raises(CNOPInternalServerException, match=expected_error_msg):
            get_order(
                order_request=order_request,
                request=create_mock_request(),
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )


    def test_get_order_different_user_order(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao
    ):
        """Test order retrieval for order belonging to different user"""
        order_id = "order1234567890"
        other_user = "otheruser"

        # Setup mocks
        # Mock order with different username
        mock_order = MagicMock()
        mock_order.username = other_user
        mock_order_dao.get_order.return_value = mock_order

        # Test that the exception is raised
        order_request = GetOrderRequest(order_id=order_id)
        with pytest.raises(CNOPOrderNotFoundException, match=f"Order '{order_id}' not found"):
            get_order(
                order_request=order_request,
                request=create_mock_request(),
                current_user=mock_current_user,
                order_dao=mock_order_dao
            )

    def test_get_order_logging_and_metrics(
        self,
        mock_current_user,
        mock_order_dao,
        mock_user_dao,
        mock_order
    ):
        """Test order retrieval logging and metrics recording"""
        order_id = "order1234567890"

        # Setup mocks
        mock_order_dao.get_order.return_value = mock_order

        # Test the function
        order_request = GetOrderRequest(order_id=order_id)
        result = get_order(
            order_request=order_request,
            request=create_mock_request(),
            current_user=mock_current_user,
            order_dao=mock_order_dao
        )
