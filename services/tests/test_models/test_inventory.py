import pytest
from datetime import datetime
from pydantic import ValidationError

from models.inventory import InventoryUpdate, InventoryItem


class TestInventoryUpdate:
    """Test cases for InventoryUpdate model."""

    def test_inventory_update_creation_success(self):
        """Test successful InventoryUpdate creation."""
        update = InventoryUpdate(quantity_change=10)
        
        assert update.quantity_change == 10
        assert update.reason is None

    def test_inventory_update_with_reason(self):
        """Test InventoryUpdate creation with reason."""
        update = InventoryUpdate(
            quantity_change=-5,
            reason="Customer return"
        )
        
        assert update.quantity_change == -5
        assert update.reason == "Customer return"

    def test_inventory_update_negative_quantity(self):
        """Test InventoryUpdate with negative quantity change."""
        update = InventoryUpdate(quantity_change=-100)
        assert update.quantity_change == -100

    def test_inventory_update_zero_quantity(self):
        """Test InventoryUpdate with zero quantity change."""
        update = InventoryUpdate(quantity_change=0)
        assert update.quantity_change == 0

    def test_inventory_update_required_fields(self):
        """Test that quantity_change is required."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryUpdate(reason="Some reason")
        assert "quantity_change" in str(exc_info.value)

    def test_inventory_update_invalid_quantity_type(self):
        """Test InventoryUpdate with invalid quantity type."""
        with pytest.raises(ValidationError):
            InventoryUpdate(quantity_change="not_a_number")

    def test_inventory_update_serialization(self):
        """Test InventoryUpdate JSON serialization."""
        update = InventoryUpdate(
            quantity_change=15,
            reason="New stock received"
        )
        
        json_str = update.model_dump_json()
        assert "15" in json_str
        assert "New stock received" in json_str

    def test_inventory_update_optional_reason(self):
        """Test that reason field is optional."""
        update = InventoryUpdate(quantity_change=10)
        data = update.model_dump()
        
        assert "quantity_change" in data
        assert data["reason"] is None


class TestInventoryItem:
    """Test cases for InventoryItem model."""

    def test_inventory_item_creation_success(self, sample_inventory_data):
        """Test successful InventoryItem creation."""
        item = InventoryItem(**sample_inventory_data)
        
        assert item.product_id == "prod-123"
        assert item.stock_quantity == 100
        assert item.reserved_quantity == 10
        assert item.min_stock_level == 5
        assert item.warehouse_location == "Warehouse A"

    def test_inventory_item_required_fields(self):
        """Test that required fields are enforced."""
        # Missing product_id
        with pytest.raises(ValidationError) as exc_info:
            InventoryItem(
                stock_quantity=100,
                reserved_quantity=10,
                min_stock_level=5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        assert "product_id" in str(exc_info.value)

        # Missing stock_quantity
        with pytest.raises(ValidationError) as exc_info:
            InventoryItem(
                product_id="prod-123",
                reserved_quantity=10,
                min_stock_level=5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        assert "stock_quantity" in str(exc_info.value)

    def test_inventory_item_optional_fields(self):
        """Test that optional fields work correctly."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=100,
            reserved_quantity=10,
            min_stock_level=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
            # warehouse_location and last_restocked_at are optional
        )
        
        assert item.warehouse_location is None
        assert item.last_restocked_at is None

    def test_available_quantity_property(self):
        """Test available_quantity calculated property."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=100,
            reserved_quantity=25,
            min_stock_level=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.available_quantity == 75  # 100 - 25

    def test_available_quantity_negative_protection(self):
        """Test that available_quantity never goes below zero."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=10,
            reserved_quantity=25,  # More reserved than stock
            min_stock_level=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.available_quantity == 0  # max(0, 10 - 25)

    def test_is_low_stock_property_true(self):
        """Test is_low_stock property when stock is low."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=10,
            reserved_quantity=7,  # Available: 3
            min_stock_level=5,    # 3 <= 5, so low stock
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_low_stock is True

    def test_is_low_stock_property_false(self):
        """Test is_low_stock property when stock is sufficient."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=20,
            reserved_quantity=5,   # Available: 15
            min_stock_level=10,    # 15 > 10, so not low stock
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_low_stock is False

    def test_is_low_stock_property_boundary(self):
        """Test is_low_stock property at boundary condition."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=15,
            reserved_quantity=5,   # Available: 10
            min_stock_level=10,    # 10 <= 10, so low stock
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_low_stock is True

    def test_is_out_of_stock_property_true(self):
        """Test is_out_of_stock property when out of stock."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=5,
            reserved_quantity=5,   # Available: 0
            min_stock_level=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_out_of_stock is True

    def test_is_out_of_stock_property_false(self):
        """Test is_out_of_stock property when stock is available."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=10,
            reserved_quantity=5,   # Available: 5
            min_stock_level=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_out_of_stock is False

    def test_is_out_of_stock_property_negative_scenario(self):
        """Test is_out_of_stock property with over-reserved scenario."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=5,
            reserved_quantity=10,  # Available: 0 (protected by max)
            min_stock_level=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.is_out_of_stock is True

    def test_inventory_item_negative_values_validation(self):
        """Test that negative values are handled appropriately."""
        # Negative stock_quantity should be invalid
        with pytest.raises(ValidationError):
            InventoryItem(
                product_id="prod-123",
                stock_quantity=-10,
                reserved_quantity=5,
                min_stock_level=2,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        # Negative reserved_quantity should be invalid
        with pytest.raises(ValidationError):
            InventoryItem(
                product_id="prod-123",
                stock_quantity=10,
                reserved_quantity=-5,
                min_stock_level=2,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    def test_inventory_item_serialization(self, sample_inventory_data):
        """Test InventoryItem JSON serialization."""
        item = InventoryItem(**sample_inventory_data)
        
        json_str = item.model_dump_json()
        assert "prod-123" in json_str
        assert "100" in json_str
        assert "Warehouse A" in json_str

    def test_inventory_item_datetime_fields(self):
        """Test that datetime fields are properly handled."""
        now = datetime.now()
        earlier = datetime(2024, 1, 1, 12, 0, 0)
        
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=100,
            reserved_quantity=10,
            min_stock_level=5,
            last_restocked_at=earlier,
            created_at=now,
            updated_at=now
        )
        
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)
        assert isinstance(item.last_restocked_at, datetime)
        assert item.last_restocked_at == earlier

    def test_inventory_item_edge_cases(self):
        """Test InventoryItem edge cases."""
        # Zero stock
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=0,
            reserved_quantity=0,
            min_stock_level=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.available_quantity == 0
        assert item.is_out_of_stock is True
        assert item.is_low_stock is True

        # Very high stock
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=1000000,
            reserved_quantity=100,
            min_stock_level=50,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.available_quantity == 999900
        assert item.is_out_of_stock is False
        assert item.is_low_stock is False


class TestInventoryModelsIntegration:
    """Integration tests for inventory models."""

    def test_inventory_update_and_item_compatibility(self):
        """Test that InventoryUpdate can be used to update InventoryItem."""
        # Simulate applying an inventory update
        original_item = InventoryItem(
            product_id="prod-123",
            stock_quantity=100,
            reserved_quantity=10,
            min_stock_level=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        update = InventoryUpdate(
            quantity_change=25,
            reason="New shipment received"
        )
        
        # Simulate applying the update (this would be done in a service)
        new_stock = original_item.stock_quantity + update.quantity_change
        
        assert new_stock == 125
        assert update.reason == "New shipment received"

    def test_multiple_updates_scenario(self):
        """Test scenario with multiple inventory updates."""
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=50,
            reserved_quantity=5,
            min_stock_level=10,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        updates = [
            InventoryUpdate(quantity_change=20, reason="Restock"),
            InventoryUpdate(quantity_change=-15, reason="Sale"),
            InventoryUpdate(quantity_change=10, reason="Return")
        ]
        
        final_stock = item.stock_quantity
        for update in updates:
            final_stock += update.quantity_change
        
        assert final_stock == 65  # 50 + 20 - 15 + 10

    def test_warehouse_location_consistency(self):
        """Test warehouse location handling across models."""
        # InventoryUpdate doesn't have warehouse info (it's applied to specific items)
        update = InventoryUpdate(quantity_change=10)
        assert not hasattr(update, 'warehouse_location')
        
        # InventoryItem does have warehouse info
        item = InventoryItem(
            product_id="prod-123",
            stock_quantity=100,
            reserved_quantity=10,
            min_stock_level=5,
            warehouse_location="Main Warehouse",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert item.warehouse_location == "Main Warehouse"

    def test_model_validation_consistency(self):
        """Test that both models have consistent validation behavior."""
        # Both models should reject invalid data types appropriately
        with pytest.raises(ValidationError):
            InventoryUpdate(quantity_change=None)
        
        with pytest.raises(ValidationError):
            InventoryItem(
                product_id=None,
                stock_quantity=100,
                reserved_quantity=10,
                min_stock_level=5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )