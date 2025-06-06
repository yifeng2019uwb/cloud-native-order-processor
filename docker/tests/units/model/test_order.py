import pytest
from unittest.mock import patch

# Assuming your Order class is in a module called 'models'
# from models import Order
# For this example, I'll include the Order class definition
from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class Order:
    order_id: str
    customer_email: str
    customer_name: str
    items: List[Dict]
    total_amount: float
    status: str
    created_at: str
    updated_at: str = None

    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self):
        return asdict(self)

    @property
    def item_count(self) -> int:
        return sum(item.get("quantity", 0) for item in self.items)

    def add_item(self, item_dict: Dict):
        """Add an item to the order"""
        self.items.append(item_dict)
        self._recalculate_total()

    def remove_item(self, product_id: str):
        """Remove an item from the order"""
        self.items = [
            item for item in self.items if item.get("product_id") != product_id
        ]
        self._recalculate_total()

    def _recalculate_total(self):
        """Recalculate the total amount based on items"""
        self.total_amount = sum(
            item.get("quantity", 0) * item.get("price", 0) for item in self.items
        )


# Test Fixtures
@pytest.fixture
def sample_order_data():
    """Fixture providing sample order data"""
    return {
        "order_id": "ORD-001",
        "customer_email": "test@example.com",
        "customer_name": "John Doe",
        "items": [
            {"product_id": "PROD-001", "name": "Widget", "quantity": 2, "price": 10.00},
            {"product_id": "PROD-002", "name": "Gadget", "quantity": 1, "price": 25.00},
        ],
        "total_amount": 45.00,
        "status": "pending",
        "created_at": "2024-01-15T10:30:00",
    }


@pytest.fixture
def sample_order(sample_order_data):
    """Fixture providing a sample Order instance"""
    return Order(**sample_order_data)


@pytest.fixture
def empty_order():
    """Fixture providing an order with no items"""
    return Order(
        order_id="ORD-002",
        customer_email="empty@example.com",
        customer_name="Jane Smith",
        items=[],
        total_amount=0.0,
        status="pending",
        created_at="2024-01-15T11:00:00",
    )


class TestOrderInitialization:
    """Test Order class initialization"""

    def test_order_initialization_with_all_fields(self, sample_order_data):
        """Test creating an order with all fields provided"""
        order = Order(**sample_order_data)

        assert order.order_id == "ORD-001"
        assert order.customer_email == "test@example.com"
        assert order.customer_name == "John Doe"
        assert len(order.items) == 2
        assert order.total_amount == 45.00
        assert order.status == "pending"
        assert order.created_at == "2024-01-15T10:30:00"
        assert order.updated_at == "2024-01-15T10:30:00"  # Should match created_at

    def test_order_initialization_with_updated_at(self, sample_order_data):
        """Test creating an order with explicit updated_at"""
        sample_order_data["updated_at"] = "2024-01-15T12:00:00"
        order = Order(**sample_order_data)

        assert order.updated_at == "2024-01-15T12:00:00"
        assert order.updated_at != order.created_at

    def test_order_initialization_missing_required_field(self, sample_order_data):
        """Test that missing required fields raise TypeError"""
        del sample_order_data["customer_email"]

        with pytest.raises(TypeError):
            Order(**sample_order_data)

    def test_order_initialization_with_empty_items(self):
        """Test creating an order with empty items list"""
        order = Order(
            order_id="ORD-003",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[],
            total_amount=0.0,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert order.items == []
        assert order.item_count == 0
        assert order.total_amount == 0.0


class TestOrderProperties:
    """Test Order properties and computed values"""

    def test_item_count_property(self, sample_order):
        """Test item_count property calculation"""
        assert sample_order.item_count == 3  # 2 + 1

    def test_item_count_with_missing_quantity(self):
        """Test item_count when items have missing quantity"""
        order = Order(
            order_id="ORD-004",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[
                {"product_id": "PROD-001", "price": 10.00},  # Missing quantity
                {"product_id": "PROD-002", "quantity": 2, "price": 5.00},
            ],
            total_amount=10.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert order.item_count == 2  # 0 + 2

    def test_item_count_empty_order(self, empty_order):
        """Test item_count for order with no items"""
        assert empty_order.item_count == 0


class TestOrderMethods:
    """Test Order instance methods"""

    def test_to_dict_method(self, sample_order):
        """Test conversion of Order to dictionary"""
        order_dict = sample_order.to_dict()

        assert isinstance(order_dict, dict)
        assert order_dict["order_id"] == "ORD-001"
        assert order_dict["customer_email"] == "test@example.com"
        assert order_dict["items"] == sample_order.items
        assert order_dict["total_amount"] == 45.00
        assert "updated_at" in order_dict

    def test_add_item_method(self, sample_order):
        """Test adding an item to the order"""
        initial_count = sample_order.item_count
        initial_total = sample_order.total_amount

        new_item = {
            "product_id": "PROD-003",
            "name": "New Product",
            "quantity": 3,
            "price": 15.00,
        }

        sample_order.add_item(new_item)

        assert len(sample_order.items) == 3
        assert sample_order.items[-1] == new_item
        assert sample_order.item_count == initial_count + 3
        assert sample_order.total_amount == initial_total + (3 * 15.00)

    def test_add_item_with_missing_fields(self, sample_order):
        """Test adding an item with missing quantity/price fields"""
        new_item = {"product_id": "PROD-004", "name": "Incomplete Product"}

        initial_total = sample_order.total_amount
        sample_order.add_item(new_item)

        assert len(sample_order.items) == 3
        assert sample_order.total_amount == initial_total  # Should not change

    def test_remove_item_method(self, sample_order):
        """Test removing an item from the order"""
        initial_count = len(sample_order.items)

        sample_order.remove_item("PROD-001")

        assert len(sample_order.items) == initial_count - 1
        assert all(item["product_id"] != "PROD-001" for item in sample_order.items)
        assert sample_order.total_amount == 25.00  # Only PROD-002 remains

    def test_remove_nonexistent_item(self, sample_order):
        """Test removing an item that doesn't exist"""
        initial_items = sample_order.items.copy()
        initial_total = sample_order.total_amount

        sample_order.remove_item("PROD-999")

        assert sample_order.items == initial_items
        assert sample_order.total_amount == initial_total

    def test_remove_all_items(self, sample_order):
        """Test removing all items from order"""
        sample_order.remove_item("PROD-001")
        sample_order.remove_item("PROD-002")

        assert len(sample_order.items) == 0
        assert sample_order.total_amount == 0.0

    def test_recalculate_total_private_method(self, sample_order):
        """Test that _recalculate_total works correctly"""
        # Manually change total to incorrect value
        sample_order.total_amount = 999.99

        # Call private method directly (for testing purposes)
        sample_order._recalculate_total()

        assert sample_order.total_amount == 45.00


class TestOrderEdgeCases:
    """Test edge cases and error scenarios"""

    def test_order_with_negative_quantities(self):
        """Test order with negative quantities"""
        order = Order(
            order_id="ORD-005",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[{"product_id": "PROD-001", "quantity": -2, "price": 10.00}],
            total_amount=-20.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert order.item_count == -2
        assert order.total_amount == -20.00

    def test_order_with_zero_price_items(self):
        """Test order with zero-priced items"""
        order = Order(
            order_id="ORD-006",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[{"product_id": "PROD-001", "quantity": 5, "price": 0.00}],
            total_amount=0.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert order.item_count == 5
        assert order.total_amount == 0.00

    def test_order_with_float_quantities(self):
        """Test order with float quantities (e.g., for weight-based items)"""
        order = Order(
            order_id="ORD-007",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[{"product_id": "PROD-001", "quantity": 2.5, "price": 10.00}],
            total_amount=25.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert order.item_count == 2.5
        assert order.total_amount == 25.00

    def test_order_status_variations(self):
        """Test order with different status values"""
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

        for status in statuses:
            order = Order(
                order_id=f"ORD-{status}",
                customer_email="test@example.com",
                customer_name="Test User",
                items=[],
                total_amount=0.00,
                status=status,
                created_at="2024-01-15T10:00:00",
            )
            assert order.status == status


class TestOrderIntegration:
    """Test Order class in integration scenarios"""

    def test_order_workflow(self):
        """Test a complete order workflow"""
        # Create new order
        order = Order(
            order_id="ORD-008",
            customer_email="customer@example.com",
            customer_name="Customer Name",
            items=[],
            total_amount=0.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        # Add items
        order.add_item({"product_id": "P1", "quantity": 2, "price": 10.00})
        order.add_item({"product_id": "P2", "quantity": 1, "price": 20.00})

        assert order.item_count == 3
        assert order.total_amount == 40.00

        # Remove an item
        order.remove_item("P1")

        assert order.item_count == 1
        assert order.total_amount == 20.00

        # Convert to dict for API response
        order_dict = order.to_dict()
        assert isinstance(order_dict, dict)
        assert order_dict["total_amount"] == 20.00

    @patch("datetime.datetime")
    def test_order_with_mocked_datetime(self, mock_datetime):
        """Test order creation with mocked datetime"""
        mock_now = "2024-01-15T15:30:00"
        mock_datetime.now.return_value.isoformat.return_value = mock_now

        order = Order(
            order_id="ORD-009",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[],
            total_amount=0.00,
            status="pending",
            created_at=mock_now,
        )

        assert order.created_at == mock_now
        assert order.updated_at == mock_now


class TestOrderValidation:
    """Test validation scenarios (if you add validation later)"""

    def test_email_format_validation(self):
        """Test that email validation could be added"""
        # This test is a placeholder for when you add email validation
        order = Order(
            order_id="ORD-010",
            customer_email="invalid-email",  # Invalid format
            customer_name="Test User",
            items=[],
            total_amount=0.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        # Currently no validation, but you might want to add it
        assert order.customer_email == "invalid-email"

    def test_order_id_format(self):
        """Test various order ID formats"""
        order_ids = ["ORD-001", "12345", "order_2024_001", ""]

        for order_id in order_ids:
            order = Order(
                order_id=order_id,
                customer_email="test@example.com",
                customer_name="Test User",
                items=[],
                total_amount=0.00,
                status="pending",
                created_at="2024-01-15T10:00:00",
            )
            assert order.order_id == order_id


# Performance and stress tests
class TestOrderPerformance:
    """Test Order class performance with large datasets"""

    def test_order_with_many_items(self):
        """Test order with a large number of items"""
        items = [
            {"product_id": f"PROD-{i}", "quantity": 1, "price": 10.00}
            for i in range(1000)
        ]

        order = Order(
            order_id="ORD-LARGE",
            customer_email="test@example.com",
            customer_name="Test User",
            items=items,
            total_amount=10000.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        assert len(order.items) == 1000
        assert order.item_count == 1000
        assert order.total_amount == 10000.00

    def test_repeated_add_remove_operations(self):
        """Test repeated add/remove operations"""
        order = Order(
            order_id="ORD-STRESS",
            customer_email="test@example.com",
            customer_name="Test User",
            items=[],
            total_amount=0.00,
            status="pending",
            created_at="2024-01-15T10:00:00",
        )

        # Add and remove items repeatedly
        for i in range(100):
            order.add_item({"product_id": f"P-{i}", "quantity": 1, "price": 5.00})

        assert order.item_count == 100
        assert order.total_amount == 500.00

        for i in range(0, 100, 2):  # Remove every other item
            order.remove_item(f"P-{i}")

        assert order.item_count == 50
        assert order.total_amount == 250.00
