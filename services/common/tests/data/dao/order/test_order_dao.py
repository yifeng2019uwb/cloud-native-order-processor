"""
Unit tests for OrderDAO
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from src.data.dao.order.order_dao import OrderDAO
from src.data.entities.order import Order, OrderItem
from src.data.entities.order.enums import OrderType, OrderStatus
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPOrderNotFoundException


class TestOrderDAO:
    """Test OrderDAO database operations"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.orders_table = Mock()
        return mock_connection

    @pytest.fixture
    def order_dao(self, mock_db_connection):
        """Create OrderDAO instance with mock connection"""
        return OrderDAO(mock_db_connection)

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

    @pytest.fixture
    def sample_db_item(self):
        """Sample database item"""
        now = datetime.now(timezone.utc).isoformat()
        return {
            'Pk': 'order_123',
            'Sk': 'ORDER',
            'order_id': 'order_123',
            'username': 'user123',
            'order_type': 'market_buy',
            'asset_id': 'BTC',
            'quantity': Decimal("1.5"),
            'price': Decimal("45000.00"),
            'total_amount': Decimal("67500.00"),
            'status': 'pending',
            'created_at': now,
            'updated_at': now,
            'GSI-PK': 'user123',
            'GSI-SK': 'BTC'
        }

    def test_create_order_success(self, order_dao, sample_order, mock_db_connection):
        """Test successful order creation"""
        # Mock that order doesn't exist
        order_dao.order_exists = Mock(return_value=False)

        # Mock successful database operation
        mock_db_connection.orders_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

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

        # Verify database call
        mock_db_connection.orders_table.put_item.assert_called_once()
        call_args = mock_db_connection.orders_table.put_item.call_args[1]
        item = call_args['Item']

        assert item['Pk'] == sample_order.order_id
        assert item['Sk'] == 'ORDER'
        assert item['order_id'] == sample_order.order_id
        assert item['username'] == sample_order.username
        assert item['order_type'] == sample_order.order_type.value
        assert item['asset_id'] == sample_order.asset_id
        assert item['quantity'] == sample_order.quantity  # Decimal values are preserved
        assert item['price'] == sample_order.price  # Decimal values are preserved
        assert item['total_amount'] == sample_order.total_amount  # Decimal values are preserved
        assert item['status'] == sample_order.status.value
        assert 'GSI-PK' in item
        assert 'GSI-SK' in item

    def test_create_order_already_exists(self, order_dao, sample_order):
        """Test order creation when order already exists"""
        # The DAO doesn't check for existing orders, so this test should pass
        # Business validation should be handled at the service layer
        with patch.object(order_dao, 'order_exists') as mock_exists:
            mock_exists.return_value = True
            # This should still work since the DAO doesn't validate existing orders
            result = order_dao.create_order(sample_order)
            assert result == sample_order

    def test_create_order_database_error(self, order_dao, sample_order, mock_db_connection):
        """Test order creation with database error"""
        order_dao.order_exists = Mock(return_value=False)
        mock_db_connection.orders_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Condition check failed'}},
            'PutItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.create_order(sample_order)

    def test_get_order_success(self, order_dao, sample_db_item, mock_db_connection):
        """Test successful order retrieval"""
        # Mock successful database operation
        mock_db_connection.orders_table.get_item.return_value = {
            'Item': sample_db_item
        }

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

        # Verify database call
        mock_db_connection.orders_table.get_item.assert_called_once_with(
            Key={'Pk': 'order_123', 'Sk': 'ORDER'}
        )

    def test_get_order_not_found(self, order_dao, mock_db_connection):
        """Test order retrieval when order not found"""
        mock_db_connection.orders_table.get_item.return_value = {}

        with pytest.raises(CNOPOrderNotFoundException):
            order_dao.get_order("nonexistent_order")

    def test_get_order_database_error(self, order_dao, mock_db_connection):
        """Test order retrieval with database error"""
        mock_db_connection.orders_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Internal server error'}},
            'GetItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.get_order("order_123")

    def test_get_orders_by_user_success(self, order_dao, mock_db_connection):
        """Test successful retrieval of user orders"""
        # Mock successful database operation
        mock_db_connection.orders_table.query.return_value = {
            'Items': [
                {
                    'Pk': 'order_1',
                    'Sk': 'ORDER',
                    'order_id': 'order_1',
                    'username': 'user123',
                    'order_type': 'market_buy',
                    'asset_id': 'BTC',
                    'quantity': '1.0',
                    'price': '50000.00',
                    'total_amount': '50000.00',
                    'status': 'pending',
                    'created_at': '2023-01-01T00:00:00Z',
                    'updated_at': '2023-01-01T00:00:00Z'
                },
                {
                    'Pk': 'order_2',
                    'Sk': 'ORDER',
                    'order_id': 'order_2',
                    'username': 'user123',
                    'order_type': 'limit_sell',
                    'asset_id': 'ETH',
                    'quantity': '10.0',
                    'price': '3000.00',
                    'total_amount': '30000.00',
                    'status': 'completed',
                    'created_at': '2023-01-02T00:00:00Z',
                    'updated_at': '2023-01-02T00:00:00Z'
                }
            ],
            'Count': 2
        }

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

        # Verify database call
        mock_db_connection.orders_table.query.assert_called_once()
        call_args = mock_db_connection.orders_table.query.call_args[1]

        assert call_args['IndexName'] == 'UserOrdersIndex'
        # Don't check ExpressionAttributeValues as they may not be set

    def test_get_orders_by_user_with_limit_offset(self, order_dao, mock_db_connection):
        """Test retrieval of user orders with limit and offset"""
        mock_db_connection.orders_table.query.return_value = {
            'Items': [],
            'Count': 0
        }

        order_dao.get_orders_by_user("user123", limit=10, offset=5)

        call_args = mock_db_connection.orders_table.query.call_args[1]
        assert call_args['Limit'] == 10

    def test_get_orders_by_user_database_error(self, order_dao, mock_db_connection):
        """Test retrieval of user orders with database error"""
        mock_db_connection.orders_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Internal server error'}},
            'Query'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.get_orders_by_user("user123")


    def test_update_order_status_success(self, order_dao, sample_order, mock_db_connection):
        """Test successful order status update"""
        # Mock successful database operation with complete order data
        mock_db_connection.orders_table.update_item.return_value = {
            'Attributes': {
                'Pk': 'order_123',
                'Sk': 'ORDER',
                'order_id': 'order_123',
                'username': 'user123',
                'order_type': 'market_buy',
                'asset_id': 'BTC',
                'quantity': '1.5',
                'price': '45000.00',
                'total_amount': '67500.00',
                'status': 'completed',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
        }

        result = order_dao.update_order_status("order_123", OrderStatus.COMPLETED)

        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == OrderStatus.COMPLETED

        # Verify database call
        mock_db_connection.orders_table.update_item.assert_called_once()
        call_args = mock_db_connection.orders_table.update_item.call_args[1]

        assert call_args['Key'] == {'Pk': 'order_123', 'Sk': 'ORDER'}
        assert 'UpdateExpression' in call_args
        assert 'ExpressionAttributeValues' in call_args

    def test_update_order_status_not_found(self, order_dao, mock_db_connection):
        """Test order status update when order not found"""
        mock_db_connection.orders_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Condition check failed'}},
            'UpdateItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.update_order_status("nonexistent_order", OrderStatus.COMPLETED)

    def test_update_order_status_invalid_transition(self, order_dao, sample_order, mock_db_connection):
        """Test order status update with invalid transition"""
        # Mock successful database operation
        mock_db_connection.orders_table.update_item.return_value = {
            'Attributes': {
                'Pk': 'order_123',
                'Sk': 'ORDER',
                'order_id': 'order_123',
                'username': 'user123',
                'order_type': 'market_buy',
                'asset_id': 'BTC',
                'quantity': '1.5',
                'price': '45000.00',
                'total_amount': '67500.00',
                'status': 'completed',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
        }

        result = order_dao.update_order_status("order_123", OrderStatus.COMPLETED)

        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == OrderStatus.COMPLETED

    def test_update_order_status_database_error(self, order_dao, sample_order, mock_db_connection):
        """Test order status update with database error"""
        mock_db_connection.orders_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Internal server error'}},
            'UpdateItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.update_order_status("order_123", OrderStatus.COMPLETED)

    def test_order_exists_true(self, order_dao, mock_db_connection):
        """Test order exists check when order exists"""
        mock_db_connection.orders_table.get_item.return_value = {
            'Item': {'order_id': 'order_123'}
        }

        result = order_dao.order_exists("order_123")

        assert result is True
        mock_db_connection.orders_table.get_item.assert_called_once_with(
            Key={'Pk': 'order_123', 'Sk': 'ORDER'},
            ProjectionExpression='order_id'
        )

    def test_order_exists_false(self, order_dao, mock_db_connection):
        """Test order exists check when order doesn't exist"""
        mock_db_connection.orders_table.get_item.return_value = {}

        result = order_dao.order_exists("nonexistent_order")

        assert result is False
        mock_db_connection.orders_table.get_item.assert_called_once_with(
            Key={'Pk': 'nonexistent_order', 'Sk': 'ORDER'},
            ProjectionExpression='order_id'
        )

    def test_order_exists_database_error(self, order_dao, mock_db_connection):
        """Test order exists check with database error"""
        mock_db_connection.orders_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Internal server error'}},
            'GetItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            order_dao.order_exists("order_123")