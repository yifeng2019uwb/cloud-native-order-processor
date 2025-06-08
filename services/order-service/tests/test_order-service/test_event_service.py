# services/order-service/tests/test_services/test_event_service.py
import pytest
import os
import uuid
import json
from datetime import datetime
from unittest.mock import MagicMock, patch, call
from decimal import Decimal

# Import from the correct path - these should now work with the updated PYTHONPATH
try:
    from services.event_service import EventService
except ImportError:
    # Fallback import path
    import sys

    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "order-service", "src"
        )
    )
    from services.event_service import EventService

from models.order import OrderResponse, OrderStatus
from models.events import OrderEvent, EventType


@pytest.fixture
def event_service():
    """Create EventService instance with mocked AWS clients."""
    with patch("boto3.client") as mock_boto_client:
        mock_sns = MagicMock()
        mock_s3 = MagicMock()

        # Configure boto3.client to return appropriate mocks
        def client_side_effect(service_name, **kwargs):
            if service_name == "sns":
                return mock_sns
            elif service_name == "s3":
                return mock_s3
            return MagicMock()

        mock_boto_client.side_effect = client_side_effect

        service = EventService()
        service.sns_client = mock_sns
        service.s3_client = mock_s3

        return service


@pytest.fixture
def sample_order_response():
    """Sample OrderResponse for testing."""
    return OrderResponse(
        order_id="order-123",
        customer_email="test@example.com",
        customer_name="John Doe",
        status=OrderStatus.PENDING,
        total_amount=Decimal("99.99"),
        currency="USD",
        items=[],
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )


class TestEventService:
    """Test cases for EventService class."""

    def test_event_service_initialization(self):
        """Test EventService initialization with environment variables."""
        env_vars = {
            "AWS_REGION": "us-east-1",
            "SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:123456789:test-topic",
            "S3_EVENTS_BUCKET": "test-events-bucket",
        }

        with patch.dict(os.environ, env_vars):
            with patch("boto3.client") as mock_boto_client:
                service = EventService()

                # Verify boto3 clients were created with correct region
                assert mock_boto_client.call_count == 2
                mock_boto_client.assert_has_calls(
                    [
                        call("sns", region_name="us-east-1"),
                        call("s3", region_name="us-east-1"),
                    ]
                )

                assert (
                    service.sns_topic_arn
                    == "arn:aws:sns:us-east-1:123456789:test-topic"
                )
                assert service.s3_events_bucket == "test-events-bucket"

    def test_event_service_initialization_default_region(self):
        """Test EventService initialization with default region."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("boto3.client") as mock_boto_client:
                service = EventService()

                # Verify default region was used
                mock_boto_client.assert_has_calls(
                    [
                        call("sns", region_name="us-west-2"),
                        call("s3", region_name="us-west-2"),
                    ]
                )

    @pytest.mark.asyncio
    async def test_publish_order_event_success_both_services(
        self, event_service, sample_order_response
    ):
        """Test successful event publishing to both SNS and S3."""
        # Set environment variables
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"
        event_service.s3_events_bucket = "test-events-bucket"

        # Mock successful AWS calls
        event_service.sns_client.publish.return_value = {"MessageId": "msg-123"}
        event_service.s3_client.put_object.return_value = {"ETag": "etag-123"}

        with patch("services.event_service.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-9012-123456789012")

            with patch("services.event_service.datetime") as mock_datetime_module:
                fixed_time = datetime(2024, 1, 1, 15, 30, 0)
                mock_datetime_module.utcnow.return_value = fixed_time
                mock_datetime_module.return_value = fixed_time  # For datetime() calls

                # Mock the strftime method to return expected format
                mock_datetime_instance = MagicMock()
                mock_datetime_instance.strftime.return_value = "2024/01/01"
                mock_datetime_module.return_value = mock_datetime_instance

                await event_service.publish_order_event(
                    "order_created", sample_order_response
                )

        # Verify SNS publish was called
        event_service.sns_client.publish.assert_called_once()
        sns_call = event_service.sns_client.publish.call_args

        assert sns_call[1]["TopicArn"] == "arn:aws:sns:us-west-2:123456789:test-topic"
        assert sns_call[1]["Subject"] == "Order Event: order_created"

        # Parse and verify the message content
        message_json = sns_call[1]["Message"]
        message_data = json.loads(message_json)
        assert message_data["event_type"] == "order_created"
        assert message_data["order_id"] == "order-123"
        assert message_data["customer_email"] == "test@example.com"
        assert message_data["service_name"] == "order-service"

        # Verify S3 put_object was called
        event_service.s3_client.put_object.assert_called_once()
        s3_call = event_service.s3_client.put_object.call_args

        assert s3_call[1]["Bucket"] == "test-events-bucket"
        assert s3_call[1]["ContentType"] == "application/json"

        # Verify S3 key format contains expected components
        s3_key = s3_call[1]["Key"]
        assert "events/" in s3_key
        assert "order_created_order-123_" in s3_key
        assert s3_key.endswith(".json")

    @pytest.mark.asyncio
    async def test_publish_order_event_sns_only(
        self, event_service, sample_order_response
    ):
        """Test event publishing when only SNS is configured."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"
        event_service.s3_events_bucket = None

        event_service.sns_client.publish.return_value = {"MessageId": "msg-123"}

        await event_service.publish_order_event("order_updated", sample_order_response)

        # Verify SNS was called but S3 was not
        event_service.sns_client.publish.assert_called_once()
        event_service.s3_client.put_object.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_order_event_s3_only(
        self, event_service, sample_order_response
    ):
        """Test event publishing when only S3 is configured."""
        event_service.sns_topic_arn = None
        event_service.s3_events_bucket = "test-events-bucket"

        event_service.s3_client.put_object.return_value = {"ETag": "etag-123"}

        await event_service.publish_order_event(
            "order_cancelled", sample_order_response
        )

        # Verify S3 was called but SNS was not
        event_service.s3_client.put_object.assert_called_once()
        event_service.sns_client.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_order_event_no_services_configured(
        self, event_service, sample_order_response
    ):
        """Test event publishing when no services are configured."""
        event_service.sns_topic_arn = None
        event_service.s3_events_bucket = None

        # Should not raise exception, just silently skip
        await event_service.publish_order_event("order_created", sample_order_response)

        # Verify no AWS calls were made
        event_service.sns_client.publish.assert_not_called()
        event_service.s3_client.put_object.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_order_event_sns_failure(
        self, event_service, sample_order_response
    ):
        """Test handling of SNS publish failure."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"
        event_service.s3_events_bucket = "test-events-bucket"

        # Mock SNS failure
        event_service.sns_client.publish.side_effect = Exception("SNS Error")
        event_service.s3_client.put_object.return_value = {"ETag": "etag-123"}

        # Should handle exception gracefully (no re-raise)
        with patch("builtins.print") as mock_print:
            await event_service.publish_order_event(
                "order_created", sample_order_response
            )

            # Verify error was printed
            mock_print.assert_called_once()
            assert "Failed to publish event" in str(mock_print.call_args)

    @pytest.mark.asyncio
    async def test_publish_order_event_s3_failure(
        self, event_service, sample_order_response
    ):
        """Test handling of S3 put failure."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"
        event_service.s3_events_bucket = "test-events-bucket"

        # Mock S3 failure
        event_service.sns_client.publish.return_value = {"MessageId": "msg-123"}
        event_service.s3_client.put_object.side_effect = Exception("S3 Error")

        # Should handle exception gracefully
        with patch("builtins.print") as mock_print:
            await event_service.publish_order_event(
                "order_created", sample_order_response
            )

            mock_print.assert_called_once()
            assert "Failed to publish event" in str(mock_print.call_args)

    @pytest.mark.asyncio
    async def test_publish_order_event_event_creation(
        self, event_service, sample_order_response
    ):
        """Test that OrderEvent is created correctly."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"

        with patch("services.event_service.uuid.uuid4") as mock_uuid:
            test_uuid = uuid.UUID("11111111-2222-3333-4444-555555555555")
            mock_uuid.return_value = test_uuid

            with patch("services.event_service.datetime") as mock_datetime_module:
                fixed_time = datetime(2024, 6, 8, 10, 15, 30)
                mock_datetime_module.utcnow.return_value = fixed_time

                await event_service.publish_order_event(
                    "order_created", sample_order_response
                )

        # Verify the event was created with correct data
        event_service.sns_client.publish.assert_called_once()
        sns_call = event_service.sns_client.publish.call_args

        message_json = sns_call[1]["Message"]
        event_data = json.loads(message_json)

        assert event_data["event_id"] == "11111111-2222-3333-4444-555555555555"
        assert event_data["event_type"] == "order_created"
        assert event_data["order_id"] == "order-123"
        assert event_data["customer_email"] == "test@example.com"
        assert event_data["service_name"] == "order-service"
        assert "data" in event_data
        assert event_data["data"]["order_id"] == "order-123"

    @pytest.mark.asyncio
    async def test_publish_order_event_invalid_event_type(
        self, event_service, sample_order_response
    ):
        """Test handling of invalid event type."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"

        # Should handle invalid event type gracefully
        with patch("builtins.print") as mock_print:
            await event_service.publish_order_event(
                "invalid_event_type", sample_order_response
            )

            # Verify error was printed and no AWS calls were made
            mock_print.assert_called_once()
            assert "Failed to publish event" in str(mock_print.call_args)
            event_service.sns_client.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_order_event_with_valid_event_types(
        self, event_service, sample_order_response
    ):
        """Test publishing with all valid EventType values."""
        event_service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"

        valid_event_types = [
            "order_created",
            "order_updated",
            "order_status_changed",
            "order_cancelled",
            "inventory_updated",
            "inventory_low_stock",
            "payment_processed",
        ]

        for event_type in valid_event_types:
            event_service.sns_client.reset_mock()

            await event_service.publish_order_event(event_type, sample_order_response)

            # Each valid event type should result in a successful publish
            event_service.sns_client.publish.assert_called_once()

            # Verify event type in message
            sns_call = event_service.sns_client.publish.call_args
            message_json = sns_call[1]["Message"]
            event_data = json.loads(message_json)
            assert event_data["event_type"] == event_type


class TestEventServiceIntegration:
    """Integration tests for EventService."""

    @pytest.mark.asyncio
    async def test_event_service_with_real_order_data(self):
        """Test EventService with comprehensive order data."""
        # Create EventService with mocked AWS clients
        with patch("boto3.client") as mock_boto_client:
            mock_sns = MagicMock()
            mock_s3 = MagicMock()

            def client_side_effect(service_name, **kwargs):
                return mock_sns if service_name == "sns" else mock_s3

            mock_boto_client.side_effect = client_side_effect

            service = EventService()
            service.sns_topic_arn = "arn:aws:sns:us-west-2:123456789:test-topic"
            service.s3_events_bucket = "test-events-bucket"

            # Create comprehensive order response
            from models.order import OrderItem

            order_response = OrderResponse(
                order_id="integration-order-123",
                customer_email="integration@test.com",
                customer_name="Integration Test User",
                status=OrderStatus.CONFIRMED,
                total_amount=Decimal("199.98"),
                currency="USD",
                items=[
                    OrderItem(
                        product_id="prod-1",
                        product_name="Test Product 1",
                        quantity=2,
                        unit_price=Decimal("49.99"),
                        line_total=Decimal("99.98"),
                    ),
                    OrderItem(
                        product_id="prod-2",
                        product_name="Test Product 2",
                        quantity=1,
                        unit_price=Decimal("99.99"),
                        line_total=Decimal("99.99"),
                    ),
                ],
                shipping_address={
                    "street": "123 Integration St",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345",
                },
                created_at=datetime(2024, 6, 8, 12, 0, 0),
                updated_at=datetime(2024, 6, 8, 12, 30, 0),
            )

            mock_sns.publish.return_value = {"MessageId": "msg-123"}
            mock_s3.put_object.return_value = {"ETag": "etag-123"}

            await service.publish_order_event("order_status_changed", order_response)

            # Verify both services were called
            mock_sns.publish.assert_called_once()
            mock_s3.put_object.assert_called_once()

            # Verify the complete order data was included
            sns_call = mock_sns.publish.call_args
            message_json = sns_call[1]["Message"]
            event_data = json.loads(message_json)

            order_data = event_data["data"]
            assert order_data["total_amount"] == "199.98"
            assert len(order_data["items"]) == 2
            assert order_data["shipping_address"]["city"] == "Test City"
