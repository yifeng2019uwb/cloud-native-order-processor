# services/order-service/tests/test_services/test_order_service.py
import pytest
import uuid
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import asyncpg

from services.order_service import OrderService
from models.order import OrderCreate, OrderItemCreate, OrderResponse, OrderStatus
from services.event_service import EventService


@pytest.fixture
def order_service():
    """Create OrderService instance with mocked event service."""
    with patch.object(
        OrderService, "__init__", lambda x: setattr(x, "event_service", AsyncMock())
    ):
        service = OrderService()
        return service


@pytest.fixture
def sample_order_create():
    """Sample OrderCreate data for testing."""
    return OrderCreate(
        customer_email="test@example.com",
        customer_name="John Doe",
        items=[
            OrderItemCreate(product_id="prod-123", quantity=2),
            OrderItemCreate(product_id="prod-456", quantity=1),
        ],
        shipping_address={
            "street": "123 Main St",
            "city": "Test City",
            "state": "TS",
            "zip": "12345",
        },
    )


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    mock_conn = AsyncMock(spec=asyncpg.Connection)

    # Mock transaction context manager
    class MockTransaction:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    mock_conn.transaction.return_value = MockTransaction()
    return mock_conn


class TestOrderService:
    """Test cases for OrderService class."""

    @pytest.mark.asyncio
    async def test_create_order_success(
        self, order_service, sample_order_create, mock_db_connection
    ):
        """Test successful order creation."""
        # Mock product data
        mock_product_1 = {
            "product_id": "prod-123",
            "name": "Product 1",
            "price": 29.99,
            "sku": "PROD-123",
        }
        mock_product_2 = {
            "product_id": "prod-456",
            "name": "Product 2",
            "price": 49.99,
            "sku": "PROD-456",
        }

        # Mock inventory data
        mock_inventory_1 = {
            "product_id": "prod-123",
            "stock_quantity": 100,
            "reserved_quantity": 10,
        }
        mock_inventory_2 = {
            "product_id": "prod-456",
            "stock_quantity": 50,
            "reserved_quantity": 5,
        }

        # Configure mock database responses
        mock_db_connection.fetchrow.side_effect = [
            mock_product_1,  # First product lookup
            mock_inventory_1,  # First inventory lookup
            mock_product_2,  # Second product lookup
            mock_inventory_2,  # Second inventory lookup
        ]

        # Mock database execute calls
        mock_db_connection.execute.return_value = None

        # Mock event service
        order_service.event_service.publish_order_event = AsyncMock()

        # Execute test
        result = await order_service.create_order(
            sample_order_create, mock_db_connection
        )

        # Assertions
        assert isinstance(result, OrderResponse)
        assert result.customer_email == "test@example.com"
        assert result.customer_name == "John Doe"
        assert result.status == OrderStatus.PENDING
        assert result.currency == "USD"
        assert len(result.items) == 2
        assert result.total_amount == Decimal("109.97")  # (29.99 * 2) + (49.99 * 1)

        # Verify items
        item_1 = result.items[0]
        assert item_1.product_name == "Product 1"
        assert item_1.quantity == 2
        assert item_1.unit_price == Decimal("29.99")
        assert item_1.line_total == Decimal("59.98")

        # Verify database calls
        assert mock_db_connection.fetchrow.call_count == 4
        assert (
            mock_db_connection.execute.call_count == 5
        )  # 1 order + 2 items + 2 inventory reserves

        # Verify event was published
        order_service.event_service.publish_order_event.assert_called_once_with(
            "order_created", result
        )

    @pytest.mark.asyncio
    async def test_create_order_product_not_found(
        self, order_service, sample_order_create, mock_db_connection
    ):
        """Test order creation fails when product not found."""
        # Mock product not found
        mock_db_connection.fetchrow.return_value = None

        with pytest.raises(ValueError, match="Product prod-123 not found"):
            await order_service.create_order(sample_order_create, mock_db_connection)

    @pytest.mark.asyncio
    async def test_create_order_no_inventory(
        self, order_service, sample_order_create, mock_db_connection
    ):
        """Test order creation fails when no inventory found."""
        mock_product = {"product_id": "prod-123", "name": "Product 1", "price": 29.99}

        # Return product, then None for inventory
        mock_db_connection.fetchrow.side_effect = [mock_product, None]

        with pytest.raises(ValueError, match="No inventory found for product prod-123"):
            await order_service.create_order(sample_order_create, mock_db_connection)

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(
        self, order_service, sample_order_create, mock_db_connection
    ):
        """Test order creation fails when insufficient stock."""
        mock_product = {"product_id": "prod-123", "name": "Product 1", "price": 29.99}
        mock_inventory = {
            "product_id": "prod-123",
            "stock_quantity": 5,
            "reserved_quantity": 4,  # Available: 1, but need 2
        }

        mock_db_connection.fetchrow.side_effect = [mock_product, mock_inventory]

        with pytest.raises(
            ValueError, match="Insufficient stock for Product 1. Available: 1"
        ):
            await order_service.create_order(sample_order_create, mock_db_connection)

    @pytest.mark.asyncio
    async def test_get_order_success(self, order_service, mock_db_connection):
        """Test successful order retrieval."""
        order_id = str(uuid.uuid4())

        # Mock order data
        mock_order = {
            "order_id": order_id,
            "customer_email": "test@example.com",
            "customer_name": "John Doe",
            "status": "pending",
            "total_amount": 79.98,
            "currency": "USD",
            "shipping_address": '{"street": "123 Main St"}',
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Mock order items
        mock_items = [
            {
                "product_id": "prod-123",
                "product_name": "Product 1",
                "quantity": 2,
                "unit_price": 29.99,
                "line_total": 59.98,
            },
            {
                "product_id": "prod-456",
                "product_name": "Product 2",
                "quantity": 1,
                "unit_price": 19.99,
                "line_total": 19.99,
            },
        ]

        mock_db_connection.fetchrow.return_value = mock_order
        mock_db_connection.fetch.return_value = mock_items

        result = await order_service.get_order(order_id, mock_db_connection)

        assert result is not None
        assert result.order_id == order_id
        assert result.customer_email == "test@example.com"
        assert result.status == OrderStatus.PENDING
        assert len(result.items) == 2
        assert result.shipping_address == {"street": "123 Main St"}

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, order_service, mock_db_connection):
        """Test order retrieval when order doesn't exist."""
        mock_db_connection.fetchrow.return_value = None

        result = await order_service.get_order("nonexistent-id", mock_db_connection)

        assert result is None

    @pytest.mark.asyncio
    async def test_list_orders_no_filters(self, order_service, mock_db_connection):
        """Test listing orders without filters."""
        mock_orders = [
            {"order_id": "order-1", "created_at": datetime.utcnow()},
            {"order_id": "order-2", "created_at": datetime.utcnow()},
        ]

        mock_db_connection.fetch.return_value = mock_orders

        # Mock get_order calls
        with patch.object(order_service, "get_order") as mock_get_order:
            mock_order_response = OrderResponse(
                order_id="order-1",
                customer_email="test@example.com",
                customer_name="Test User",
                status=OrderStatus.PENDING,
                total_amount=Decimal("50.00"),
                currency="USD",
                items=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            mock_get_order.return_value = mock_order_response

            result = await order_service.list_orders(mock_db_connection)

            assert len(result) == 2
            assert mock_get_order.call_count == 2

    @pytest.mark.asyncio
    async def test_list_orders_with_filters(self, order_service, mock_db_connection):
        """Test listing orders with status and email filters."""
        mock_orders = [{"order_id": "order-1", "created_at": datetime.utcnow()}]
        mock_db_connection.fetch.return_value = mock_orders

        with patch.object(order_service, "get_order") as mock_get_order:
            mock_get_order.return_value = None  # Simulate order not found

            result = await order_service.list_orders(
                mock_db_connection,
                limit=10,
                status="pending",
                customer_email="test@example.com",
            )

            # Verify the query was built with filters
            call_args = mock_db_connection.fetch.call_args
            query = call_args[0][0]
            params = call_args[0][1:]

            assert "AND status = $1" in query
            assert "AND customer_email = $2" in query
            assert "LIMIT $3" in query
            assert params == ("pending", "test@example.com", 10)

    @pytest.mark.asyncio
    async def test_update_order_status_success(self, order_service, mock_db_connection):
        """Test successful order status update."""
        order_id = str(uuid.uuid4())

        # Mock successful update
        mock_db_connection.execute.return_value = "UPDATE 1"

        # Mock get_order for event publishing
        with patch.object(order_service, "get_order") as mock_get_order:
            mock_order = OrderResponse(
                order_id=order_id,
                customer_email="test@example.com",
                customer_name="Test User",
                status=OrderStatus.CONFIRMED,
                total_amount=Decimal("50.00"),
                currency="USD",
                items=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            mock_get_order.return_value = mock_order

            # Mock event service
            order_service.event_service.publish_order_event = AsyncMock()

            result = await order_service.update_order_status(
                order_id, OrderStatus.CONFIRMED, mock_db_connection
            )

            assert result is True
            order_service.event_service.publish_order_event.assert_called_once_with(
                "order_status_updated", mock_order
            )

    @pytest.mark.asyncio
    async def test_update_order_status_not_found(
        self, order_service, mock_db_connection
    ):
        """Test order status update when order doesn't exist."""
        mock_db_connection.execute.return_value = "UPDATE 0"

        result = await order_service.update_order_status(
            "nonexistent-id", OrderStatus.CONFIRMED, mock_db_connection
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_create_order_with_shipping_address(
        self, order_service, mock_db_connection
    ):
        """Test order creation with shipping address handling."""
        order_data = OrderCreate(
            customer_email="test@example.com",
            customer_name="John Doe",
            items=[OrderItemCreate(product_id="prod-123", quantity=1)],
            shipping_address={"street": "456 Oak Ave", "city": "New City"},
        )

        # Mock product and inventory data
        mock_product = {"product_id": "prod-123", "name": "Product", "price": 25.00}
        mock_inventory = {"stock_quantity": 10, "reserved_quantity": 0}

        mock_db_connection.fetchrow.side_effect = [mock_product, mock_inventory]
        mock_db_connection.execute.return_value = None

        order_service.event_service.publish_order_event = AsyncMock()

        result = await order_service.create_order(order_data, mock_db_connection)

        assert result.shipping_address == {"street": "456 Oak Ave", "city": "New City"}

        # Verify shipping address was JSON-encoded in database call
        create_order_call = mock_db_connection.execute.call_args_list[0]
        shipping_arg = create_order_call[0][7]  # 8th parameter (0-indexed)
        assert json.loads(shipping_arg) == {"street": "456 Oak Ave", "city": "New City"}

    @pytest.mark.asyncio
    async def test_create_order_without_shipping_address(
        self, order_service, mock_db_connection
    ):
        """Test order creation without shipping address."""
        order_data = OrderCreate(
            customer_email="test@example.com",
            customer_name="John Doe",
            items=[OrderItemCreate(product_id="prod-123", quantity=1)],
            # No shipping_address
        )

        # Mock product and inventory data
        mock_product = {"product_id": "prod-123", "name": "Product", "price": 25.00}
        mock_inventory = {"stock_quantity": 10, "reserved_quantity": 0}

        mock_db_connection.fetchrow.side_effect = [mock_product, mock_inventory]
        mock_db_connection.execute.return_value = None

        order_service.event_service.publish_order_event = AsyncMock()

        result = await order_service.create_order(order_data, mock_db_connection)

        assert result.shipping_address is None

        # Verify shipping address was None in database call
        create_order_call = mock_db_connection.execute.call_args_list[0]
        shipping_arg = create_order_call[0][7]  # 8th parameter (0-indexed)
        assert shipping_arg is None


class TestOrderServiceIntegration:
    """Integration-style tests for OrderService."""

    @pytest.mark.asyncio
    async def test_complete_order_workflow(self, order_service, mock_db_connection):
        """Test complete order creation to status update workflow."""
        # Step 1: Create order
        order_data = OrderCreate(
            customer_email="integration@test.com",
            customer_name="Integration Test",
            items=[OrderItemCreate(product_id="prod-integration", quantity=1)],
        )

        mock_product = {
            "product_id": "prod-integration",
            "name": "Integration Product",
            "price": 100.00,
        }
        mock_inventory = {"stock_quantity": 20, "reserved_quantity": 5}

        mock_db_connection.fetchrow.side_effect = [mock_product, mock_inventory]
        mock_db_connection.execute.return_value = None
        order_service.event_service.publish_order_event = AsyncMock()

        created_order = await order_service.create_order(order_data, mock_db_connection)

        # Reset mocks for status update
        mock_db_connection.reset_mock()

        # Step 2: Update order status
        mock_db_connection.execute.return_value = "UPDATE 1"

        with patch.object(order_service, "get_order") as mock_get_order:
            updated_order = created_order.model_copy(
                update={"status": OrderStatus.CONFIRMED}
            )
            mock_get_order.return_value = updated_order

            success = await order_service.update_order_status(
                created_order.order_id, OrderStatus.CONFIRMED, mock_db_connection
            )

            assert success is True

            # Verify both events were published
            assert order_service.event_service.publish_order_event.call_count == 2
            event_calls = order_service.event_service.publish_order_event.call_args_list
            assert event_calls[0][0][0] == "order_created"
            assert event_calls[1][0][0] == "order_status_updated"

    @pytest.mark.asyncio
    async def test_order_creation_rollback_scenario(
        self, order_service, mock_db_connection
    ):
        """Test that order creation handles database transaction failures."""
        order_data = OrderCreate(
            customer_email="rollback@test.com",
            customer_name="Rollback Test",
            items=[OrderItemCreate(product_id="prod-fail", quantity=1)],
        )

        mock_product = {
            "product_id": "prod-fail",
            "name": "Failing Product",
            "price": 50.00,
        }
        mock_inventory = {"stock_quantity": 10, "reserved_quantity": 0}

        mock_db_connection.fetchrow.side_effect = [mock_product, mock_inventory]

        # Simulate database failure during order creation
        mock_db_connection.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await order_service.create_order(order_data, mock_db_connection)

        # Verify transaction was attempted (transaction context manager was used)
        mock_db_connection.transaction.assert_called_once()

    def test_order_service_initialization(self):
        """Test OrderService initialization creates EventService."""
        with patch("services.order_service.EventService") as mock_event_service_class:
            mock_event_service_instance = MagicMock()
            mock_event_service_class.return_value = mock_event_service_instance

            service = OrderService()

            assert service.event_service == mock_event_service_instance
            mock_event_service_class.assert_called_once()
