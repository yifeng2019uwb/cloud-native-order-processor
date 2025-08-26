"""
Tests for Asset Transaction Entity Models
"""

import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime, timezone

from src.data.entities.asset import (
    AssetTransaction,
    AssetTransactionCreate,
    AssetTransactionResponse,
    AssetTransactionType,
    AssetTransactionStatus
)


class TestAssetTransactionCreate:
    """Test AssetTransactionCreate model validation"""

    def test_valid_asset_transaction_create(self):
        """Test valid asset transaction creation data"""
        transaction_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "order_id": "order-123"
        }
        transaction = AssetTransactionCreate(**transaction_data)
        assert transaction.username == "testuser123"
        assert transaction.asset_id == "BTC"
        assert transaction.transaction_type == AssetTransactionType.BUY
        assert transaction.quantity == Decimal("2.5")
        assert transaction.price == Decimal("50000.00")
        assert transaction.order_id == "order-123"

    def test_asset_transaction_create_sell_type(self):
        """Test asset transaction creation with SELL type"""
        transaction_data = {
            "username": "testuser123",
            "asset_id": "ETH",
            "transaction_type": AssetTransactionType.SELL,
            "quantity": Decimal("10.0"),
            "price": Decimal("3000.00")
        }
        transaction = AssetTransactionCreate(**transaction_data)
        assert transaction.transaction_type == AssetTransactionType.SELL
        assert transaction.order_id is None

    def test_asset_transaction_create_zero_quantity(self):
        """Test asset transaction creation with zero quantity"""
        # Zero quantities are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("0.0"),
            price=Decimal("50000.00")
        )
        assert transaction.quantity == Decimal("0.0")

    def test_asset_transaction_create_negative_quantity(self):
        """Test asset transaction creation with negative quantity"""
        # Negative quantities are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("-2.5"),
            price=Decimal("50000.00")
        )
        assert transaction.quantity == Decimal("-2.5")

    def test_asset_transaction_create_zero_price(self):
        """Test asset transaction creation with zero price"""
        # Zero prices are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("0.0")
        )
        assert transaction.price == Decimal("0.0")

    def test_asset_transaction_create_negative_price(self):
        """Test asset transaction creation with negative price"""
        # Negative prices are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("-50000.00")
        )
        assert transaction.price == Decimal("-50000.00")

    def test_asset_transaction_create_missing_required_fields(self):
        """Test asset transaction creation with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetTransactionCreate(
                username="testuser123",
                asset_id="BTC",
                transaction_type=AssetTransactionType.BUY
            )
        assert "quantity" in str(exc_info.value)
        assert "price" in str(exc_info.value)

    def test_asset_transaction_create_empty_username(self):
        """Test asset transaction creation with empty username"""
        # Empty strings are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00")
        )
        assert transaction.username == ""

    def test_asset_transaction_create_empty_asset_id(self):
        """Test asset transaction creation with empty asset_id"""
        # Empty strings are allowed by default in Pydantic
        transaction = AssetTransactionCreate(
            username="testuser123",
            asset_id="",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00")
        )
        assert transaction.asset_id == ""


class TestAssetTransaction:
    """Test AssetTransaction model validation"""

    def test_valid_asset_transaction(self):
        """Test valid asset transaction data"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.Pk == "TRANS#testuser123#BTC"
        assert transaction.Sk == "2024-01-01T12:00:00Z"
        assert transaction.username == "testuser123"
        assert transaction.asset_id == "BTC"
        assert transaction.transaction_type == AssetTransactionType.BUY
        assert transaction.quantity == Decimal("2.5")
        assert transaction.price == Decimal("50000.00")
        assert transaction.total_amount == Decimal("125000.00")
        assert transaction.order_id == "order-123"
        assert transaction.status == AssetTransactionStatus.COMPLETED
        assert transaction.created_at == now

    def test_asset_transaction_default_status(self):
        """Test asset transaction with default status"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#ETH",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "ETH",
            "transaction_type": AssetTransactionType.SELL,
            "quantity": Decimal("10.0"),
            "price": Decimal("3000.00"),
            "total_amount": Decimal("30000.00"),
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.status == AssetTransactionStatus.COMPLETED

    def test_asset_transaction_default_timestamp(self):
        """Test asset transaction with default timestamp"""
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00")
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.created_at is not None
        assert isinstance(transaction.created_at, datetime)

    def test_asset_transaction_pending_status(self):
        """Test asset transaction with pending status"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "status": AssetTransactionStatus.PENDING,
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.status == AssetTransactionStatus.PENDING

    def test_asset_transaction_failed_status(self):
        """Test asset transaction with failed status"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "status": AssetTransactionStatus.FAILED,
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.status == AssetTransactionStatus.FAILED

    def test_asset_transaction_missing_required_fields(self):
        """Test asset transaction with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetTransaction(
                username="testuser123",
                asset_id="BTC",
                transaction_type=AssetTransactionType.BUY,
                quantity=Decimal("2.5"),
                price=Decimal("50000.00"),
                total_amount=Decimal("125000.00")
            )
        assert "Pk" in str(exc_info.value)
        assert "Sk" in str(exc_info.value)

    def test_asset_transaction_json_serialization(self):
        """Test asset transaction JSON serialization"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)

        # Test JSON serialization
        json_data = transaction.model_dump()
        assert json_data["Pk"] == "TRANS#testuser123#BTC"
        assert json_data["Sk"] == "2024-01-01T12:00:00Z"
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["transaction_type"] == AssetTransactionType.BUY
        assert json_data["quantity"] == Decimal("2.5")
        assert json_data["price"] == Decimal("50000.00")
        assert json_data["total_amount"] == Decimal("125000.00")
        assert json_data["order_id"] == "order-123"
        assert json_data["status"] == AssetTransactionStatus.COMPLETED
        assert json_data["created_at"] == now


class TestAssetTransactionResponse:
    """Test AssetTransactionResponse model validation"""

    def test_valid_asset_transaction_response(self):
        """Test valid asset transaction response data"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        response = AssetTransactionResponse(**response_data)
        assert response.username == "testuser123"
        assert response.asset_id == "BTC"
        assert response.transaction_type == AssetTransactionType.BUY
        assert response.quantity == Decimal("2.5")
        assert response.price == Decimal("50000.00")
        assert response.total_amount == Decimal("125000.00")
        assert response.order_id == "order-123"
        assert response.status == AssetTransactionStatus.COMPLETED
        assert response.created_at == now

    def test_asset_transaction_response_no_order_id(self):
        """Test asset transaction response without order_id"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "ETH",
            "transaction_type": AssetTransactionType.SELL,
            "quantity": Decimal("10.0"),
            "price": Decimal("3000.00"),
            "total_amount": Decimal("30000.00"),
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        response = AssetTransactionResponse(**response_data)
        assert response.order_id is None

    def test_asset_transaction_response_missing_fields(self):
        """Test asset transaction response with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetTransactionResponse(
                username="testuser123",
                asset_id="BTC",
                transaction_type=AssetTransactionType.BUY
            )
        assert "quantity" in str(exc_info.value)
        assert "price" in str(exc_info.value)
        assert "total_amount" in str(exc_info.value)
        assert "status" in str(exc_info.value)
        assert "created_at" in str(exc_info.value)

    def test_asset_transaction_response_json_serialization(self):
        """Test asset transaction response JSON serialization"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        response = AssetTransactionResponse(**response_data)

        # Test JSON serialization
        json_data = response.model_dump()
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["transaction_type"] == AssetTransactionType.BUY
        assert json_data["quantity"] == Decimal("2.5")
        assert json_data["price"] == Decimal("50000.00")
        assert json_data["total_amount"] == Decimal("125000.00")
        assert json_data["order_id"] == "order-123"
        assert json_data["status"] == AssetTransactionStatus.COMPLETED
        assert json_data["created_at"] == now


class TestAssetTransactionEnums:
    """Test Asset Transaction Enums"""

    def test_asset_transaction_type_values(self):
        """Test AssetTransactionType enum values"""
        assert AssetTransactionType.BUY == "BUY"
        assert AssetTransactionType.SELL == "SELL"

    def test_asset_transaction_status_values(self):
        """Test AssetTransactionStatus enum values"""
        assert AssetTransactionStatus.PENDING == "PENDING"
        assert AssetTransactionStatus.COMPLETED == "COMPLETED"
        assert AssetTransactionStatus.FAILED == "FAILED"

    def test_enum_serialization(self):
        """Test enum serialization in models"""
        now = datetime.now(timezone.utc)
        transaction_data = {
            "Pk": "TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now
        }
        transaction = AssetTransaction(**transaction_data)

        # Test that enums are properly serialized
        json_data = transaction.model_dump()
        assert json_data["transaction_type"] == AssetTransactionType.BUY
        assert json_data["status"] == AssetTransactionStatus.COMPLETED