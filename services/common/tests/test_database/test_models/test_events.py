import pytest
from datetime import datetime
from enum import Enum
from pydantic import ValidationError

from models.events import EventType, BaseEvent, OrderEvent, InventoryEvent


class TestEventType:
    """Test cases for EventType enum."""

    def test_event_type_values(self):
        """Test that all expected event types are defined."""
        expected_events = [
            "order_created",
            "order_updated",
            "order_status_changed",
            "order_cancelled",
            "inventory_updated",
            "inventory_low_stock",
            "payment_processed",
        ]

        for event in expected_events:
            assert hasattr(EventType, event.upper())
            assert EventType[event.upper()].value == event

    def test_event_type_is_string_enum(self):
        """Test that EventType inherits from str and Enum."""
        assert issubclass(EventType, str)
        assert issubclass(EventType, Enum)

    def test_event_type_string_comparison(self):
        """Test that EventType values can be compared with strings."""
        assert EventType.ORDER_CREATED == "order_created"
        assert EventType.INVENTORY_UPDATED == "inventory_updated"

    def test_all_event_types_accessible(self):
        """Test that all event types are accessible."""
        event_types = [
            EventType.ORDER_CREATED,
            EventType.ORDER_UPDATED,
            EventType.ORDER_STATUS_CHANGED,
            EventType.ORDER_CANCELLED,
            EventType.INVENTORY_UPDATED,
            EventType.INVENTORY_LOW_STOCK,
            EventType.PAYMENT_PROCESSED,
        ]

        assert len(event_types) == 7
        for event_type in event_types:
            assert isinstance(event_type, EventType)


class TestBaseEvent:
    """Test cases for BaseEvent model."""

    def test_base_event_creation_success(self):
        """Test successful BaseEvent creation."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.ORDER_CREATED,
            "timestamp": datetime.now(),
            "service_name": "order-service",
            "data": {"order_id": "order_123"},
        }

        event = BaseEvent(**event_data)

        assert event.event_id == "evt_123"
        assert event.event_type == EventType.ORDER_CREATED
        assert event.service_name == "order-service"
        assert event.data == {"order_id": "order_123"}
        assert event.metadata is None

    def test_base_event_with_metadata(self):
        """Test BaseEvent creation with metadata."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.ORDER_CREATED,
            "timestamp": datetime.now(),
            "service_name": "order-service",
            "data": {"order_id": "order_123"},
            "metadata": {"source": "api", "version": "v1"},
        }

        event = BaseEvent(**event_data)

        assert event.metadata == {"source": "api", "version": "v1"}

    def test_base_event_required_fields(self):
        """Test that BaseEvent requires all mandatory fields."""
        # Missing event_id
        with pytest.raises(ValidationError) as exc_info:
            BaseEvent(
                event_type=EventType.ORDER_CREATED,
                timestamp=datetime.now(),
                service_name="order-service",
                data={},
            )
        assert "event_id" in str(exc_info.value)

        # Missing event_type
        with pytest.raises(ValidationError) as exc_info:
            BaseEvent(
                event_id="evt_123",
                timestamp=datetime.now(),
                service_name="order-service",
                data={},
            )
        assert "event_type" in str(exc_info.value)

        # Missing timestamp
        with pytest.raises(ValidationError) as exc_info:
            BaseEvent(
                event_id="evt_123",
                event_type=EventType.ORDER_CREATED,
                service_name="order-service",
                data={},
            )
        assert "timestamp" in str(exc_info.value)

    def test_base_event_invalid_event_type(self):
        """Test BaseEvent with invalid event type."""
        with pytest.raises(ValidationError):
            BaseEvent(
                event_id="evt_123",
                event_type="invalid_event_type",
                timestamp=datetime.now(),
                service_name="order-service",
                data={},
            )

    def test_base_event_serialization(self):
        """Test BaseEvent JSON serialization."""
        event = BaseEvent(
            event_id="evt_123",
            event_type=EventType.ORDER_CREATED,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            service_name="order-service",
            data={"order_id": "order_123"},
        )

        json_str = event.model_dump_json()
        assert "evt_123" in json_str
        assert "order_created" in json_str
        assert "order-service" in json_str

    def test_base_event_deserialization(self):
        """Test BaseEvent JSON deserialization."""
        json_data = {
            "event_id": "evt_123",
            "event_type": "order_created",
            "timestamp": "2024-01-01T12:00:00",
            "service_name": "order-service",
            "data": {"order_id": "order_123"},
        }

        event = BaseEvent(**json_data)
        assert event.event_id == "evt_123"
        assert event.event_type == EventType.ORDER_CREATED


class TestOrderEvent:
    """Test cases for OrderEvent model."""

    def test_order_event_creation_success(self):
        """Test successful OrderEvent creation."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.ORDER_CREATED,
            "timestamp": datetime.now(),
            "service_name": "order-service",
            "data": {"order_id": "order_123"},
            "order_id": "order_123",
            "customer_email": "test@example.com",
        }

        event = OrderEvent(**event_data)

        assert event.order_id == "order_123"
        assert event.customer_email == "test@example.com"
        assert isinstance(event, BaseEvent)

    def test_order_event_inheritance(self):
        """Test that OrderEvent inherits from BaseEvent."""
        assert issubclass(OrderEvent, BaseEvent)

    def test_order_event_additional_fields_required(self):
        """Test that OrderEvent requires additional fields."""
        base_data = {
            "event_id": "evt_123",
            "event_type": EventType.ORDER_CREATED,
            "timestamp": datetime.now(),
            "service_name": "order-service",
            "data": {"order_id": "order_123"},
        }

        # Missing order_id
        with pytest.raises(ValidationError) as exc_info:
            OrderEvent(**base_data, customer_email="test@example.com")
        assert "order_id" in str(exc_info.value)

        # Missing customer_email
        with pytest.raises(ValidationError) as exc_info:
            OrderEvent(**base_data, order_id="order_123")
        assert "customer_email" in str(exc_info.value)

    def test_order_event_with_all_fields(self):
        """Test OrderEvent with all possible fields."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.ORDER_STATUS_CHANGED,
            "timestamp": datetime.now(),
            "service_name": "order-service",
            "data": {
                "order_id": "order_123",
                "old_status": "pending",
                "new_status": "confirmed",
            },
            "metadata": {"user_id": "user_456"},
            "order_id": "order_123",
            "customer_email": "test@example.com",
        }

        event = OrderEvent(**event_data)

        assert event.event_type == EventType.ORDER_STATUS_CHANGED
        assert event.metadata == {"user_id": "user_456"}
        assert event.data["old_status"] == "pending"
