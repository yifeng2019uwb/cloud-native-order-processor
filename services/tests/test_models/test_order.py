import pytest
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import ValidationError
from typing import Dict, Any

from models.order import (
    OrderStatus, OrderItemCreate, OrderItem, OrderCreate, 
    Order, OrderResponse, OrderStatusUpdate
)


class TestOrderStatus:
    """Test cases for OrderStatus enum."""

    def test_order_status_values(self):
        """Test that all expected order statuses are defined."""
        expected_statuses = [
            "pending", "confirmed", "processing", "paid", 
            "shipped", "delivered", "cancelled", "refunded"
        ]
        
        for status in expected_statuses:
            assert hasattr(OrderStatus, status.upper())
            assert OrderStatus[status.upper()].value == status

    def test_order_status_is_string_enum(self):
        """Test that OrderStatus inherits from str and Enum."""
        assert issubclass(OrderStatus, str)
        assert issubclass(OrderStatus, Enum)

    def test_order_status_string_comparison(self):
        """Test that OrderStatus values can be compared with strings."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.CONFIRMED == "confirmed"
        assert OrderStatus.DELIVERED == "delivered"

    def test_all_order_statuses_accessible(self):
        """Test that all order statuses are accessible."""
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.PAID,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED
        ]
        
        assert len(statuses) == 8
        for status in statuses:
            assert isinstance(status, OrderStatus)


class TestOrderItemCreate:
    """Test cases for OrderItemCreate model."""

    def test_order_item_create_success(self):
        """Test successful OrderItemCreate creation."""
        item = OrderItemCreate(
            product_id="prod-123",
            quantity=2
        )
        
        assert item.product_id == "prod-123"
        assert item.quantity == 2

    def test_order_item_create_required_fields(self):
        """Test that required fields are enforced."""
        # Missing product_id
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(quantity=2)
        assert "product_id" in str(exc_info.value)

        # Missing quantity
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(product_id="prod-123")
        assert "quantity" in str(exc_info.value)

    def test_order_item_create_invalid_quantity(self):
        """Test validation of quantity field."""
        # Zero quantity
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id="prod-123", quantity=0)

        # Negative quantity
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id="prod-123", quantity=-1)

        # Non-integer quantity
        with pytest.raises(ValidationError):
            OrderItemCreate(product_id="prod-123", quantity=1.5)

    def test_order_item_create_serialization(self):
        """Test OrderItemCreate JSON serialization."""
        item = OrderItemCreate(product_id="prod-123", quantity=3)
        json_str = item.model_dump_json()
        
        assert "prod-123" in json_str
        assert "3" in json_str


class TestOrderItem:
    """Test cases for OrderItem model."""

    def test_order_item_creation_success(self):
        """Test successful OrderItem creation."""
        item = OrderItem(
            product_id="prod-123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("29.99"),
            line_total=Decimal("59.98")
        )
        
        assert item.product_id == "prod-123"
        assert item.product_name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == Decimal("29.99")
        assert item.line_total == Decimal("59.98")

    def test_order_item_required_fields(self):
        """Test that all fields are required."""
        required_fields = [
            "product_id", "product_name", "quantity", "unit_price", "line_total"
        ]
        
        base_data = {
            "product_id": "prod-123",
            "product_name": "Test Product",
            "quantity": 2,
            "unit_price": Decimal("29.99"),
            "line_total": Decimal("59.98")
        }
        
        for field in required_fields:
            test_data = base_data.copy()
            del test_data[field]
            
            with pytest.raises(ValidationError) as exc_info:
                OrderItem(**test_data)
            assert field in str(exc_info.value)

    def test_order_item_decimal_precision(self):
        """Test that decimal fields maintain precision."""
        item = OrderItem(
            product_id="prod-123",
            product_name="Test Product",
            quantity=3,
            unit_price=Decimal("12.345"),
            line_total=Decimal("37.035")
        )
        
        assert item.unit_price == Decimal("12.345")
        assert item.line_total == Decimal("37.035")

    def test_order_item_serialization(self):
        """Test OrderItem JSON serialization."""
        item = OrderItem(
            product_id="prod-123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("29.99"),
            line_total=Decimal("59.98")
        )
        
        json_str = item.model_dump_json()
        assert "prod-123" in json_str
        assert "Test Product" in json_str
        assert "29.99" in json_str


class TestOrderCreate:
    """Test cases for OrderCreate model."""

    def test_order_create_success(self):
        """Test successful OrderCreate creation."""
        items = [
            OrderItemCreate(product_id="prod-123", quantity=2),
            OrderItemCreate(product_id="prod-456", quantity=1)
        ]
        
        order = OrderCreate(
            customer_email="test@example.com",
            customer_name="John Doe",
            items=items,
            shipping_address={"street": "123 Main St", "city": "Test City"}
        )
        
        assert order.customer_email == "test@example.com"
        assert order.customer_name == "John Doe"
        assert len(order.items) == 2
        assert order.shipping_address["city"] == "Test City"

    def test_order_create_required_fields(self):
        """Test that required fields are enforced."""
        items = [OrderItemCreate(product_id="prod-123", quantity=1)]
        
        # Missing customer_email
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(
                customer_name="John Doe",
                items=items
            )
        assert "customer_email" in str(exc_info.value)

        # Missing customer_name
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(
                customer_email="test@example.com",
                items=items
            )
        assert "customer_name" in str(exc_info.value)

        # Missing items
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(
                customer_email="test@example.com",
                customer_name="John Doe"
            )
        assert "items" in str(exc_info.value)

    def test_order_create_email_validation(self):
        """Test email validation in OrderCreate."""
        items = [OrderItemCreate(product_id="prod-123", quantity=1)]
        
        # Invalid email format
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_email="invalid-email",
                customer_name="John Doe",
                items=items
            )

        # Valid email format
        order = OrderCreate(
            customer_email="valid@example.com",
            customer_name="John Doe",
            items=items
        )
        assert order.customer_email == "valid@example.com"

    def test_order_create_empty_items_list(self):
        """Test that empty items list is rejected."""
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_email="test@example.com",
                customer_name="John Doe",
                items=[]
            )

    def test_order_create_optional_shipping_address(self):
        """Test that shipping_address is optional."""
        items = [OrderItemCreate(product_id="prod-123", quantity=1)]
        
        order = OrderCreate(
            customer_email="test@example.com",
            customer_name="John Doe",
            items=items
            # shipping_address not provided
        )
        
        assert order.shipping_address is None


class TestOrder:
    """Test cases for Order model."""

    def test_order_creation_success(self, sample_order_data):
        """Test successful Order creation."""
        order = Order(**sample_order_data)
        
        assert order.order_id == "test-order-123"
        assert order.customer_email == "test@example.com"
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == Decimal("99.99")
        assert order.currency == "USD"

    def test_order_required_fields(self):
        """Test that required fields are enforced."""
        base_data = {
            "order_id": "test-order-123",
            "customer_id": "customer-456",
            "customer_email": "test@example.com",
            "customer_name": "John Doe",
            "status": OrderStatus.PENDING,
            "total_amount": Decimal("99.99"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        required_fields = [
            "order_id", "customer_id", "customer_email", "customer_name",
            "status", "total_amount", "created_at", "updated_at"
        ]
        
        for field in required_fields:
            test_data = base_data.copy()
            del test_data[field]
            
            with pytest.raises(ValidationError) as exc_info:
                Order(**test_data)
            assert field in str(exc_info.value)

    def test_order_default_currency(self):
        """Test that currency defaults to USD."""
        order = Order(
            order_id="test-order-123",
            customer_id="customer-456",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PENDING,
            total_amount=Decimal("99.99"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert order.currency == "USD"

    def test_order_custom_currency(self):
        """Test Order with custom currency."""
        order = Order(
            order_id="test-order-123",
            customer_id="customer-456",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PENDING,
            total_amount=Decimal("99.99"),
            currency="EUR",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert order.currency == "EUR"

    def test_order_status_enum_validation(self):
        """Test that status field accepts OrderStatus enum."""
        for status in OrderStatus:
            order = Order(
                order_id="test-order-123",
                customer_id="customer-456",
                customer_email="test@example.com",
                customer_name="John Doe",
                status=status,
                total_amount=Decimal("99.99"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            assert order.status == status


class TestOrderResponse:
    """Test cases for OrderResponse model."""

    def test_order_response_creation_success(self):
        """Test successful OrderResponse creation."""
        items = [
            OrderItem(
                product_id="prod-123",
                product_name="Test Product",
                quantity=2,
                unit_price=Decimal("29.99"),
                line_total=Decimal("59.98")
            )
        ]
        
        response = OrderResponse(
            order_id="test-order-123",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PENDING,
            total_amount=Decimal("99.99"),
            currency="USD",
            items=items,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert response.order_id == "test-order-123"
        assert len(response.items) == 1
        assert response.items[0].product_name == "Test Product"

    def test_order_response_with_shipping_address(self):
        """Test OrderResponse with shipping address."""
        items = [
            OrderItem(
                product_id="prod-123",
                product_name="Test Product",
                quantity=1,
                unit_price=Decimal("50.00"),
                line_total=Decimal("50.00")
            )
        ]
        
        shipping_address = {
            "street": "123 Main St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345"
        }
        
        response = OrderResponse(
            order_id="test-order-123",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.CONFIRMED,
            total_amount=Decimal("50.00"),
            currency="USD",
            items=items,
            shipping_address=shipping_address,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert response.shipping_address == shipping_address
        assert response.shipping_address["city"] == "Test City"

    def test_order_response_empty_items_list(self):
        """Test OrderResponse with empty items list."""
        response = OrderResponse(
            order_id="test-order-123",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PENDING,
            total_amount=Decimal("0.00"),
            currency="USD",
            items=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert len(response.items) == 0

    def test_order_response_serialization(self):
        """Test OrderResponse JSON serialization."""
        items = [
            OrderItem(
                product_id="prod-123",
                product_name="Test Product",
                quantity=1,
                unit_price=Decimal("25.50"),
                line_total=Decimal("25.50")
            )
        ]
        
        response = OrderResponse(
            order_id="test-order-123",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PAID,
            total_amount=Decimal("25.50"),
            currency="USD",
            items=items,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        json_str = response.model_dump_json()
        assert "test-order-123" in json_str
        assert "paid" in json_str
        assert "Test Product" in json_str


class TestOrderStatusUpdate:
    """Test cases for OrderStatusUpdate model."""

    def test_order_status_update_creation(self):
        """Test OrderStatusUpdate creation."""
        update = OrderStatusUpdate(status=OrderStatus.SHIPPED)
        assert update.status == OrderStatus.SHIPPED

    def test_order_status_update_all_statuses(self):
        """Test OrderStatusUpdate with all possible statuses."""
        for status in OrderStatus:
            update = OrderStatusUpdate(status=status)
            assert update.status == status

    def test_order_status_update_required_field(self):
        """Test that status is required."""
        with pytest.raises(ValidationError) as exc_info:
            OrderStatusUpdate()
        assert "status" in str(exc_info.value)

    def test_order_status_update_invalid_status(self):
        """Test OrderStatusUpdate with invalid status."""
        with pytest.raises(ValidationError):
            OrderStatusUpdate(status="invalid_status")


class TestOrderModelsIntegration:
    """Integration tests for all order models."""

    def test_order_create_to_order_response_workflow(self):
        """Test the workflow from OrderCreate to OrderResponse."""
        # Start with OrderCreate
        order_create = OrderCreate(
            customer_email="test@example.com",
            customer_name="John Doe",
            items=[
                OrderItemCreate(product_id="prod-123", quantity=2),
                OrderItemCreate(product_id="prod-456", quantity=1)
            ],
            shipping_address={"street": "123 Main St", "city": "Test City"}
        )
        
        # Simulate processing into OrderResponse
        order_items = [
            OrderItem(
                product_id="prod-123",
                product_name="Product 1",
                quantity=2,
                unit_price=Decimal("29.99"),
                line_total=Decimal("59.98")
            ),
            OrderItem(
                product_id="prod-456",
                product_name="Product 2",
                quantity=1,
                unit_price=Decimal("19.99"),
                line_total=Decimal("19.99")
            )
        ]
        
        order_response = OrderResponse(
            order_id="generated-order-id",
            customer_email=order_create.customer_email,
            customer_name=order_create.customer_name,
            status=OrderStatus.PENDING,
            total_amount=Decimal("79.97"),
            currency="USD",
            items=order_items,
            shipping_address=order_create.shipping_address,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Verify consistency
        assert order_response.customer_email == order_create.customer_email
        assert order_response.customer_name == order_create.customer_name
        assert len(order_response.items) == len(order_create.items)
        assert order_response.shipping_address == order_create.shipping_address

    def test_order_status_update_workflow(self):
        """Test order status update workflow."""
        # Create initial order
        order = Order(
            order_id="test-order-123",
            customer_id="customer-456",
            customer_email="test@example.com",
            customer_name="John Doe",
            status=OrderStatus.PENDING,
            total_amount=Decimal("99.99"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create status update
        status_update = OrderStatusUpdate(status=OrderStatus.CONFIRMED)
        
        # Simulate applying the update
        updated_order = order.model_copy(update={
            "status": status_update.status,
            "updated_at": datetime.now()
        })
        
        assert updated_order.status == OrderStatus.CONFIRMED
        assert updated_order.order_id == order.order_id

    def test_decimal_precision_consistency(self):
        """Test that decimal precision is consistent across models."""
        unit_price = Decimal("12.345")
        quantity = 3
        line_total = unit_price * quantity
        
        order_item = OrderItem(
            product_id="prod-123",
            product_name="Test Product",
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total
        )
        
        assert order_item.unit_price == Decimal("12.345")
        assert order_item.line_total == Decimal("37.035")

    def test_model_inheritance_and_composition(self):
        """Test that models work well together."""
        # All models should be Pydantic BaseModel instances
        models = [
            OrderItemCreate(product_id="prod-123", quantity=1),
            OrderItem(
                product_id="prod-123",
                product_name="Test",
                quantity=1,
                unit_price=Decimal("10.00"),
                line_total=Decimal("10.00")
            ),
            OrderCreate(
                customer_email="test@example.com",
                customer_name="Test User",
                items=[OrderItemCreate(product_id="prod-123", quantity=1)]
            ),
            Order(
                order_id="test",
                customer_id="cust",
                customer_email="test@example.com",
                customer_name="Test User",
                status=OrderStatus.PENDING,
                total_amount=Decimal("10.00"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            OrderStatusUpdate(status=OrderStatus.CONFIRMED)
        ]
        
        for model in models:
            # All should be serializable
            json_str = model.model_dump_json()
            assert isinstance(json_str, str)
            assert len(json_str) > 0
            
            # All should be deserializable
            data = model.model_dump()
            assert isinstance(data, dict)