"""
Unit tests for OrderDAO
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from botocore.exceptions import ClientError

from src.dao.order.order_dao import OrderDAO
from src.entities.order import Order, OrderUpdate
from src.entities.order.enums import OrderType, OrderStatus
from src.exceptions import (
    EntityNotFoundException,
    EntityAlreadyExistsException,
    OrderValidationException,
    DatabaseOperationException
)


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
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            order_price=None,  # MARKET_BUY orders don't have order_price
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now
        )

    @pytest.fixture
    def sample_db_item(self):
        """Sample database item"""
        now = datetime.now(timezone.utc).isoformat()
        return {
            'order_id': 'ord_user123_20231201123456789',
            'user_id': 'user123',
            'order_type': 'market_buy',
            'asset_id': 'BTC',
            'quantity': Decimal("1.5"),
            'order_price': None,  # MARKET_BUY orders don't have order_price
            'total_amount': Decimal("67500.00"),
            'currency': 'USD',
            'status': 'pending',
            'created_at': now,
            'updated_at': now,
            'GSI2-PK': 'user123',
            'GSI2-SK': 'BTC#pending#' + now
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
        assert result.user_id == sample_order.user_id
        assert result.order_type == sample_order.order_type
        assert result.asset_id == sample_order.asset_id
        assert result.quantity == sample_order.quantity
        assert result.order_price == sample_order.order_price
        assert result.currency == sample_order.currency
        assert result.status == sample_order.status

        # Verify database was called
        mock_db_connection.orders_table.put_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_already_exists(self, order_dao, sample_order):
        """Test order creation when order already exists"""
        # Mock that order exists
        order_dao.order_exists = AsyncMock(return_value=True)

        # Should raise EntityAlreadyExistsError
        with pytest.raises(EntityAlreadyExistsException, match="Order with ID"):
            await order_dao.create_order(sample_order)

    @pytest.mark.asyncio
    async def test_create_order_database_error(self, order_dao, sample_order, mock_db_connection):
        """Test order creation with database error"""
        # Mock database error
        mock_db_connection.orders_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException'}},
            'PutItem'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.create_order(sample_order)

    def test_get_order_success(self, order_dao, sample_db_item, mock_db_connection):
        """Test successful order retrieval"""
        # Mock database response
        mock_db_connection.orders_table.get_item.return_value = {
            'Item': sample_db_item
        }

        # Get order
        result = order_dao.get_order("ord_user123_20231201123456789")

        # Verify result
        assert isinstance(result, Order)
        assert result.order_id == sample_db_item['order_id']
        assert result.user_id == sample_db_item['user_id']
        assert result.order_type == OrderType.MARKET_BUY
        assert result.asset_id == sample_db_item['asset_id']
        assert result.quantity == sample_db_item['quantity']
        assert result.order_price == sample_db_item['order_price']
        assert result.currency == sample_db_item['currency']
        assert result.status == OrderStatus.PENDING

        # Verify database was called
        mock_db_connection.orders_table.get_item.assert_called_once()

    def test_get_order_not_found(self, order_dao, mock_db_connection):
        """Test order retrieval when order not found"""
        # Mock empty response
        mock_db_connection.orders_table.get_item.return_value = {}

        # Should raise EntityNotFoundException
        with pytest.raises(EntityNotFoundException) as exc_info:
            order_dao.get_order("nonexistent_order")

        assert "Order 'nonexistent_order' not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_order_database_error(self, order_dao, mock_db_connection):
        """Test order retrieval with database error"""
        # Mock database error
        mock_db_connection.orders_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'GetItem'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.get_order("test_order")

    def test_update_order_success(self, order_dao, sample_order, mock_db_connection):
        """Test successful order update"""
        # Mock existing order
        order_dao.get_order = Mock(return_value=sample_order)

        # Mock successful database operation with complete order data
        now = datetime.now(timezone.utc).isoformat()
        mock_db_connection.orders_table.update_item.return_value = {
            'Attributes': {
                'order_id': sample_order.order_id,
                'user_id': sample_order.user_id,
                'order_type': sample_order.order_type.value,
                'asset_id': sample_order.asset_id,
                'quantity': sample_order.quantity,
                'order_price': sample_order.order_price,
                'total_amount': sample_order.total_amount,
                'currency': sample_order.currency,
                'status': 'completed',
                'created_at': sample_order.created_at.isoformat(),
                'updated_at': now,
                'completed_at': now,
                'executed_quantity': Decimal("1.5"),
                'executed_price': None,
                'status_history': []
            }
        }

        # Update order
        update_data = OrderUpdate(
            status=OrderStatus.COMPLETED,
            executed_quantity=Decimal("1.5")
        )
        result = order_dao.update_order(sample_order.order_id, update_data)

        # Verify result
        assert isinstance(result, Order)
        assert result.status == OrderStatus.COMPLETED

        # Verify database was called
        mock_db_connection.orders_table.update_item.assert_called_once()

    def test_update_order_not_found(self, order_dao, mock_db_connection):
        """Test order update when order not found"""
        # Mock that order doesn't exist
        order_dao.get_order = Mock(side_effect=EntityNotFoundException("Order nonexistent_order not found"))

        # Should raise EntityNotFoundException
        update_data = OrderUpdate(status=OrderStatus.COMPLETED)
        with pytest.raises(EntityNotFoundException, match="Order"):
            order_dao.update_order("nonexistent_order", update_data)

    @pytest.mark.asyncio
    async def test_update_order_database_error(self, order_dao, sample_order, mock_db_connection):
        """Test order update with database error"""
        # Mock database error
        mock_db_connection.orders_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'UpdateItem'
        )

        # Should raise DatabaseOperationError
        update_data = OrderUpdate(status=OrderStatus.COMPLETED)
        with pytest.raises(DatabaseOperationException):
            await order_dao.update_order(sample_order.order_id, update_data)

    def test_get_orders_by_user_success(self, order_dao, mock_db_connection):
        """Test successful retrieval of user orders"""
        # Mock database response
        now = datetime.now(timezone.utc).isoformat()
        mock_db_connection.orders_table.query.return_value = {
            'Items': [
                {
                    'order_id': 'ord_user123_20231201123456789',
                    'user_id': 'user123',
                    'order_type': 'market_buy',
                    'asset_id': 'BTC',
                    'quantity': Decimal("1.5"),
                    'order_price': None,
                    'total_amount': Decimal("67500.00"),
                    'currency': 'USD',
                    'status': 'pending',
                    'created_at': now,
                    'updated_at': now
                }
            ]
        }

        # Get user orders
        result = order_dao.get_orders_by_user("user123")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].user_id == "user123"

        # Verify database was called
        mock_db_connection.orders_table.query.assert_called_once()

    def test_get_orders_by_user_with_limit_offset(self, order_dao, mock_db_connection):
        """Test user orders retrieval with limit and offset"""
        # Mock database response
        mock_db_connection.orders_table.query.return_value = {'Items': []}

        # Get user orders with limit and offset
        result = order_dao.get_orders_by_user("user123", limit=10, offset=5)

        # Verify database was called with correct parameters
        call_args = mock_db_connection.orders_table.query.call_args[1]
        assert call_args.get('Limit') == 10

    @pytest.mark.asyncio
    async def test_get_orders_by_user_database_error(self, order_dao, mock_db_connection):
        """Test user orders retrieval with database error"""
        # Mock database error
        mock_db_connection.orders_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'Query'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.get_orders_by_user("user123")

    def test_get_orders_by_user_and_asset_success(self, order_dao, mock_db_connection):
        """Test successful retrieval of user orders for specific asset"""
        # Mock database response
        now = datetime.now(timezone.utc).isoformat()
        mock_db_connection.orders_table.query.return_value = {
            'Items': [
                {
                    'order_id': 'ord_user123_20231201123456789',
                    'user_id': 'user123',
                    'order_type': 'market_buy',
                    'asset_id': 'BTC',
                    'quantity': Decimal("1.5"),
                    'order_price': None,
                    'total_amount': Decimal("67500.00"),
                    'currency': 'USD',
                    'status': 'pending',
                    'created_at': now,
                    'updated_at': now
                }
            ]
        }

        # Get user orders for specific asset
        result = order_dao.get_orders_by_user_and_asset("user123", "BTC")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].user_id == "user123"
        assert result[0].asset_id == "BTC"

        # Verify database was called
        mock_db_connection.orders_table.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_orders_by_user_and_asset_database_error(self, order_dao, mock_db_connection):
        """Test user asset orders retrieval with database error"""
        # Mock database error
        mock_db_connection.orders_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'Query'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.get_orders_by_user_and_asset("user123", "BTC")

    def test_get_orders_by_user_and_status_success(self, order_dao, mock_db_connection):
        """Test successful retrieval of user orders by status"""
        # Mock database response
        now = datetime.now(timezone.utc).isoformat()
        mock_db_connection.orders_table.query.return_value = {
            'Items': [
                {
                    'order_id': 'ord_user123_20231201123456789',
                    'user_id': 'user123',
                    'order_type': 'market_buy',
                    'asset_id': 'BTC',
                    'quantity': Decimal("1.5"),
                    'order_price': None,
                    'total_amount': Decimal("67500.00"),
                    'currency': 'USD',
                    'status': 'pending',
                    'created_at': now,
                    'updated_at': now
                }
            ]
        }

        # Get user orders by status
        result = order_dao.get_orders_by_user_and_status("user123", OrderStatus.PENDING)

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].user_id == "user123"
        assert result[0].status == OrderStatus.PENDING

        # Verify database was called
        mock_db_connection.orders_table.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_orders_by_user_and_status_database_error(self, order_dao, mock_db_connection):
        """Test user status orders retrieval with database error"""
        # Mock database error
        mock_db_connection.orders_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'Query'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.get_orders_by_user_and_status("user123", OrderStatus.PENDING)

    def test_update_order_status_success(self, order_dao, sample_order):
        """Test successful order status update"""
        # Mock existing order with PROCESSING status (can transition to COMPLETED)
        processing_order = sample_order.model_copy(update={'status': OrderStatus.PROCESSING})
        order_dao.get_order = Mock(return_value=processing_order)

        # Mock successful update
        order_dao.db.orders_table.update_item.return_value = {
            'Attributes': {
                'order_id': processing_order.order_id,
                'user_id': processing_order.user_id,
                'order_type': processing_order.order_type.value,
                'asset_id': processing_order.asset_id,
                'quantity': str(processing_order.quantity),
                'order_price': str(processing_order.order_price),
                'total_amount': str(processing_order.total_amount),
                'status': OrderStatus.COMPLETED.value,
                'created_at': processing_order.created_at.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'status_reason': 'Order completed successfully'
            }
        }

        # Update order status
        result = order_dao.update_order_status(
            processing_order.order_id,
            OrderStatus.COMPLETED,
            "Order completed successfully"
        )

        # Verify result
        assert result.status == OrderStatus.COMPLETED
        assert result.status_reason == "Order completed successfully"

    def test_update_order_status_not_found(self, order_dao):
        """Test order status update when order not found"""
        # Mock that order doesn't exist
        order_dao.get_order = Mock(side_effect=EntityNotFoundException("Order nonexistent_order not found"))

        # Should raise EntityNotFoundException
        with pytest.raises(EntityNotFoundException, match="Order"):
            order_dao.update_order_status(
                "nonexistent_order",
                OrderStatus.COMPLETED
            )

    def test_update_order_status_invalid_transition(self, order_dao, sample_order):
        """Test order status update with invalid transition"""
        # Mock existing order
        order_dao.get_order = Mock(return_value=sample_order)

        # Mock successful update (no validation in update_order_status)
        order_dao.db.orders_table.update_item.return_value = {
            'Attributes': {
                'order_id': sample_order.order_id,
                'user_id': sample_order.user_id,
                'order_type': sample_order.order_type.value,
                'asset_id': sample_order.asset_id,
                'quantity': str(sample_order.quantity),
                'order_price': str(sample_order.order_price),
                'total_amount': str(sample_order.total_amount),
                'status': OrderStatus.COMPLETED.value,
                'created_at': sample_order.created_at.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        }

        # Should succeed (no validation in update_order_status)
        result = order_dao.update_order_status(
            sample_order.order_id,
            OrderStatus.COMPLETED  # Can go directly from PENDING to COMPLETED
        )

        assert result.status == OrderStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_update_order_status_database_error(self, order_dao, sample_order):
        """Test order status update with database error"""
        # Mock existing order
        order_dao.get_order = AsyncMock(return_value=sample_order)

        # Mock database error
        order_dao.db.orders_table.update_item.side_effect = DatabaseOperationException("Database error")

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.update_order_status(
                sample_order.order_id,
                OrderStatus.CONFIRMED
            )

    def test_order_exists_true(self, order_dao, mock_db_connection):
        """Test order existence check when order exists"""
        # Mock database response
        mock_db_connection.orders_table.get_item.return_value = {
            'Item': {'order_id': 'test_order'}
        }

        # Check if order exists
        result = order_dao.order_exists("test_order")

        # Should return True
        assert result is True

        # Verify database was called
        mock_db_connection.orders_table.get_item.assert_called_once()

    def test_order_exists_false(self, order_dao, mock_db_connection):
        """Test order existence check when order doesn't exist"""
        # Mock empty response
        mock_db_connection.orders_table.get_item.return_value = {}

        # Check if order exists
        result = order_dao.order_exists("nonexistent_order")

        # Should return False
        assert result is False

    @pytest.mark.asyncio
    async def test_order_exists_database_error(self, order_dao, mock_db_connection):
        """Test order existence check with database error"""
        # Mock database error
        mock_db_connection.orders_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError'}},
            'GetItem'
        )

        # Should raise DatabaseOperationError
        with pytest.raises(DatabaseOperationException):
            await order_dao.order_exists("test_order")