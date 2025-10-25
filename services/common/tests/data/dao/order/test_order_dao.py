"""
Unit tests for OrderDAO
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.data.dao.order.order_dao import OrderDAO
from src.data.entities.order import Order, OrderItem
from src.data.entities.order.enums import OrderStatus, OrderType
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPOrderNotFoundException
from tests.utils.dependency_constants import MODEL_SAVE, MODEL_GET, MODEL_QUERY, DOES_NOT_EXIST



class TestOrderDAO:
    """Test OrderDAO database operations"""

    @pytest.fixture
    def order_dao(self):
        """Create OrderDAO instance"""
        return OrderDAO()

    @pytest.fixture
    def sample_order(self):
        """Sample order data"""
        now = datetime.now(timezone.utc)
        return Order(
            order_id="order_123",
            username="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price=Decimal("45000.00"),
            total_amount=Decimal("67500.00"),
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now
        )

    @patch.object(OrderItem, MODEL_SAVE)
    def test_create_order_success(self, mock_save, order_dao, sample_order):
        """Test successful order creation"""
        # Mock save to return None
        mock_save.return_value = None

        # Create order
        result = order_dao.create_order(sample_order)

        # Verify result
        assert isinstance(result, Order)
        assert result.order_id == sample_order.order_id
        assert result.username == sample_order.username
        assert result.order_type == sample_order.order_type
        assert result.asset_id == sample_order.asset_id
        assert result.quantity == sample_order.quantity
        assert result.price == sample_order.price
        assert result.total_amount == sample_order.total_amount

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(OrderItem, MODEL_SAVE)
    def test_create_order_database_error(self, mock_save, order_dao, sample_order):
        """Test order creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            order_dao.create_order(sample_order)

        assert "Database operation failed while creating order" in str(exc_info.value)
        assert "Database connection failed" in str(exc_info.value)

    @patch.object(OrderItem, MODEL_GET)
    def test_get_order_success(self, mock_get, order_dao):
        """Test successful order retrieval"""
        # Mock OrderItem.get to return a real OrderItem
        order_item = OrderItem(
            order_id='order_123',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.5',
            price='45000.00',
            total_amount='67500.00'
        )
        mock_get.return_value = order_item

        # Get order
        result = order_dao.get_order("order_123")

        # Verify result
        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.username == "user123"
        assert result.order_type == OrderType.MARKET_BUY
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal("1.5")
        assert result.price == Decimal("45000.00")
        assert result.total_amount == Decimal("67500.00")

        # Verify get was called
        mock_get.assert_called_once_with('order_123', 'ORDER')

    @patch.object(OrderItem, MODEL_GET)
    def test_get_order_not_found(self, mock_get, order_dao):
        """Test order retrieval when order not found"""
        # Mock OrderItem.get to raise DoesNotExist exception
        mock_get.side_effect = OrderItem.DoesNotExist()

        with pytest.raises(CNOPOrderNotFoundException) as exc_info:
            order_dao.get_order("nonexistent_order")

        assert "Order 'nonexistent_order' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent_order', 'ORDER')

    @patch.object(OrderItem, MODEL_GET)
    def test_get_order_database_error(self, mock_get, order_dao):
        """Test order retrieval with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            order_dao.get_order("order_123")

        assert "Database operation failed while retrieving order" in str(exc_info.value)
        assert "Database connection failed" in str(exc_info.value)

    @patch.object(OrderItem.user_orders_index, MODEL_QUERY)
    def test_get_orders_by_user_success(self, mock_query, order_dao):
        """Test successful retrieval of user orders"""
        # Mock query to return OrderItem instances
        order_item1 = OrderItem(
            order_id='order_1',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.0',
            price='50000.00',
            total_amount='50000.00'
        )
        order_item2 = OrderItem(
            order_id='order_2',
            username='user123',
            order_type='limit_sell',
            status='completed',
            asset_id='ETH',
            quantity='10.0',
            price='3000.00',
            total_amount='30000.00'
        )
        mock_query.return_value = [order_item1, order_item2]

        # Get user orders
        result = order_dao.get_orders_by_user("user123")

        # Verify result
        assert len(result) == 2
        assert result[0].order_id == "order_1"
        assert result[0].username == "user123"
        assert result[0].order_type == OrderType.MARKET_BUY
        assert result[1].order_id == "order_2"
        assert result[1].username == "user123"
        assert result[1].order_type == OrderType.LIMIT_SELL

        # Verify query was called
        mock_query.assert_called_once_with('user123', scan_index_forward=False, limit=50)

    @patch.object(OrderItem.user_orders_index, MODEL_QUERY)
    def test_get_orders_by_user_with_limit_offset(self, mock_query, order_dao):
        """Test retrieval of user orders with limit and offset"""
        # Mock empty query result
        mock_query.return_value = []

        # Get user orders with limit and offset
        result = order_dao.get_orders_by_user("user123", limit=10, offset=5)

        # Verify result
        assert result == []

        # Verify query was called with correct limit
        mock_query.assert_called_once_with('user123', scan_index_forward=False, limit=10)

    @patch.object(OrderItem.user_orders_index, MODEL_QUERY)
    def test_get_orders_by_user_database_error(self, mock_query, order_dao):
        """Test retrieval of user orders with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Query failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            order_dao.get_orders_by_user("user123")

        assert "Database operation failed while retrieving orders for user" in str(exc_info.value)
        assert "Query failed" in str(exc_info.value)

    @patch.object(OrderItem, MODEL_SAVE)
    @patch.object(OrderItem, MODEL_GET)
    def test_update_order_status_success(self, mock_get, mock_save, order_dao):
        """Test successful order status update"""
        # Mock OrderItem.get to return a real OrderItem
        order_item = OrderItem(
            order_id='order_123',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.5',
            price='45000.00',
            total_amount='67500.00'
        )
        mock_get.return_value = order_item
        mock_save.return_value = None

        # Update order status
        result = order_dao.update_order_status("order_123", OrderStatus.COMPLETED)

        # Verify result
        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == OrderStatus.COMPLETED

        # Verify get and save were called
        mock_get.assert_called_once_with('order_123', 'ORDER')
        mock_save.assert_called_once()

    @patch.object(OrderItem, MODEL_SAVE)
    @patch.object(OrderItem, MODEL_GET)
    def test_update_order_status_with_reason(self, mock_get, mock_save, order_dao):
        """Test order status update with reason"""
        # Mock OrderItem.get to return a real OrderItem
        order_item = OrderItem(
            order_id='order_123',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.5',
            price='45000.00',
            total_amount='67500.00'
        )
        mock_get.return_value = order_item
        mock_save.return_value = None

        # Update order status with reason
        result = order_dao.update_order_status("order_123", OrderStatus.COMPLETED, "Order filled")

        # Verify result
        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == OrderStatus.COMPLETED

        # Verify get and save were called
        mock_get.assert_called_once_with('order_123', 'ORDER')
        mock_save.assert_called_once()

    @patch.object(OrderItem, MODEL_GET)
    def test_update_order_status_not_found(self, mock_get, order_dao):
        """Test order status update when order not found"""
        # Mock OrderItem.get to raise DoesNotExist exception
        mock_get.side_effect = OrderItem.DoesNotExist()

        with pytest.raises(CNOPOrderNotFoundException) as exc_info:
            order_dao.update_order_status("nonexistent_order", OrderStatus.COMPLETED)

        assert "Order 'nonexistent_order' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent_order', 'ORDER')

    @patch.object(OrderItem, MODEL_SAVE)
    @patch.object(OrderItem, MODEL_GET)
    def test_update_order_status_database_error(self, mock_get, mock_save, order_dao):
        """Test order status update with database error"""
        # Mock OrderItem.get to return a real OrderItem
        order_item = OrderItem(
            order_id='order_123',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.5',
            price='45000.00',
            total_amount='67500.00'
        )
        mock_get.return_value = order_item
        # Mock database error on save
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            order_dao.update_order_status("order_123", OrderStatus.COMPLETED)

        assert "Database operation failed while updating order status" in str(exc_info.value)
        assert "Database connection failed" in str(exc_info.value)

    @patch.object(OrderItem, MODEL_GET)
    def test_order_exists_true(self, mock_get, order_dao):
        """Test order exists check when order exists"""
        # Mock OrderItem.get to return a real OrderItem
        order_item = OrderItem(
            order_id='order_123',
            username='user123',
            order_type='market_buy',
            status='pending',
            asset_id='BTC',
            quantity='1.5',
            price='45000.00',
            total_amount='67500.00'
        )
        mock_get.return_value = order_item

        # Check if order exists
        result = order_dao.order_exists("order_123")

        # Verify result
        assert result is True
        mock_get.assert_called_once_with('order_123', 'ORDER')

    @patch.object(OrderItem, MODEL_GET)
    def test_order_exists_false(self, mock_get, order_dao):
        """Test order exists check when order doesn't exist"""
        # Mock OrderItem.get to raise DoesNotExist exception
        mock_get.side_effect = OrderItem.DoesNotExist()

        # Check if order exists
        result = order_dao.order_exists("nonexistent_order")

        # Verify result
        assert result is False
        mock_get.assert_called_once_with('nonexistent_order', 'ORDER')

    @patch.object(OrderItem, MODEL_GET)
    def test_order_exists_database_error(self, mock_get, order_dao):
        """Test order exists check with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            order_dao.order_exists("order_123")

        assert "Database operation failed while checking existence of order" in str(exc_info.value)
        assert "Database connection failed" in str(exc_info.value)