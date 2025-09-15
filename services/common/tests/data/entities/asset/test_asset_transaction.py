"""
Tests for Asset Transaction Entity Models
"""

import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime, timezone

from src.data.entities.asset import (
    AssetTransaction,
    AssetTransactionItem,
    AssetTransactionType,
    AssetTransactionStatus
)


class TestAssetTransaction:
    """Test AssetTransaction model validation"""

    def test_valid_asset_transaction(self):
        """Test valid asset transaction creation"""
        transaction_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123"
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.username == "testuser123"
        assert transaction.asset_id == "BTC"
        assert transaction.transaction_type == AssetTransactionType.BUY
        assert transaction.quantity == Decimal("2.5")
        assert transaction.price == Decimal("50000.00")
        assert transaction.total_amount == Decimal("125000.00")
        assert transaction.order_id == "order-123"

    def test_asset_transaction_sell_type(self):
        """Test asset transaction with SELL type"""
        transaction_data = {
            "username": "testuser123",
            "asset_id": "ETH",
            "transaction_type": AssetTransactionType.SELL,
            "quantity": Decimal("10.0"),
            "price": Decimal("3000.00"),
            "total_amount": Decimal("30000.00")
        }
        transaction = AssetTransaction(**transaction_data)
        assert transaction.transaction_type == AssetTransactionType.SELL
        assert transaction.total_amount == Decimal("30000.00")
        assert transaction.order_id is None

    def test_asset_transaction_zero_quantity(self):
        """Test asset transaction with zero quantity"""
        transaction = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("0.0"),
            price=Decimal("50000.00"),
            total_amount=Decimal("0.00")
        )
        assert transaction.quantity == Decimal("0.0")

    def test_asset_transaction_negative_quantity(self):
        """Test asset transaction with negative quantity"""
        transaction = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("-2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("-125000.00")
        )
        assert transaction.quantity == Decimal("-2.5")

    def test_asset_transaction_zero_price(self):
        """Test asset transaction with zero price"""
        transaction = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("0.0"),
            total_amount=Decimal("0.00")
        )
        assert transaction.price == Decimal("0.0")

    def test_asset_transaction_missing_required_fields(self):
        """Test asset transaction with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetTransaction(
                username="testuser123",
                asset_id="BTC",
                transaction_type=AssetTransactionType.BUY
            )
        assert "quantity" in str(exc_info.value)
        assert "price" in str(exc_info.value)
        assert "total_amount" in str(exc_info.value)

    def test_asset_transaction_empty_username(self):
        """Test asset transaction with empty username"""
        transaction = AssetTransaction(
            username="",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00")
        )
        assert transaction.username == ""

    def test_asset_transaction_empty_asset_id(self):
        """Test asset transaction with empty asset_id"""
        transaction = AssetTransaction(
            username="testuser123",
            asset_id="",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00")
        )
        assert transaction.asset_id == ""

    def test_asset_transaction_default_status(self):
        """Test asset transaction with default status"""
        now = datetime.now(timezone.utc)
        transaction_data = {
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

    def test_asset_transaction_json_serialization(self):
        """Test asset transaction JSON serialization"""
        now = datetime.now(timezone.utc)
        transaction_data = {
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

        # Test model_dump
        json_data = transaction.model_dump()
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["transaction_type"] == AssetTransactionType.BUY
        assert json_data["quantity"] == Decimal("2.5")
        assert json_data["price"] == Decimal("50000.00")
        assert json_data["total_amount"] == Decimal("125000.00")
        assert json_data["order_id"] == "order-123"
        assert json_data["status"] == AssetTransactionStatus.COMPLETED
        assert json_data["created_at"] == now


class TestAssetTransactionItem:
    """Test AssetTransactionItem model validation"""

    def test_valid_asset_transaction_item(self):
        """Test valid asset transaction item creation"""
        now = datetime.now(timezone.utc)
        transaction_item_data = {
            "Pk": "ASSET_TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now.isoformat()
        }
        transaction_item = AssetTransactionItem(**transaction_item_data)
        assert transaction_item.Pk == "ASSET_TRANS#testuser123#BTC"
        assert transaction_item.Sk == "2024-01-01T12:00:00Z"
        assert transaction_item.username == "testuser123"
        assert transaction_item.asset_id == "BTC"
        assert transaction_item.transaction_type == AssetTransactionType.BUY
        assert transaction_item.quantity == Decimal("2.5")
        assert transaction_item.price == Decimal("50000.00")
        assert transaction_item.total_amount == Decimal("125000.00")
        assert transaction_item.order_id == "order-123"
        assert transaction_item.status == AssetTransactionStatus.COMPLETED

    def test_asset_transaction_item_from_entity(self):
        """Test creating AssetTransactionItem from AssetTransaction entity"""
        transaction = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00"),
            order_id="order-123",
            status=AssetTransactionStatus.COMPLETED
        )
        transaction_item = AssetTransactionItem.from_asset_transaction(transaction)
        assert transaction_item.Pk == "ASSET_TRANS#testuser123#BTC"
        assert transaction_item.Sk is not None  # Will be the created_at timestamp
        assert transaction_item.username == "testuser123"
        assert transaction_item.asset_id == "BTC"
        assert transaction_item.transaction_type == AssetTransactionType.BUY
        assert transaction_item.quantity == Decimal("2.5")
        assert transaction_item.price == Decimal("50000.00")
        assert transaction_item.total_amount == Decimal("125000.00")
        assert transaction_item.order_id == "order-123"
        assert transaction_item.status == AssetTransactionStatus.COMPLETED

    def test_asset_transaction_item_to_entity(self):
        """Test converting AssetTransactionItem to AssetTransaction entity"""
        now = datetime.now(timezone.utc)
        transaction_item = AssetTransactionItem(
            Pk="ASSET_TRANS#testuser123#BTC",
            Sk="2024-01-01T12:00:00Z",
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00"),
            order_id="order-123",
            status=AssetTransactionStatus.COMPLETED,
            created_at=now.isoformat()
        )
        transaction = transaction_item.to_asset_transaction()
        assert transaction.username == "testuser123"
        assert transaction.asset_id == "BTC"
        assert transaction.transaction_type == AssetTransactionType.BUY
        assert transaction.quantity == Decimal("2.5")
        assert transaction.price == Decimal("50000.00")
        assert transaction.total_amount == Decimal("125000.00")
        assert transaction.order_id == "order-123"
        assert transaction.status == AssetTransactionStatus.COMPLETED

    def test_asset_transaction_item_json_serialization(self):
        """Test asset transaction item JSON serialization"""
        now = datetime.now(timezone.utc)
        transaction_item_data = {
            "Pk": "ASSET_TRANS#testuser123#BTC",
            "Sk": "2024-01-01T12:00:00Z",
            "username": "testuser123",
            "asset_id": "BTC",
            "transaction_type": AssetTransactionType.BUY,
            "quantity": Decimal("2.5"),
            "price": Decimal("50000.00"),
            "total_amount": Decimal("125000.00"),
            "order_id": "order-123",
            "status": AssetTransactionStatus.COMPLETED,
            "created_at": now.isoformat()
        }
        transaction_item = AssetTransactionItem(**transaction_item_data)

        # Test model_dump
        json_data = transaction_item.model_dump()
        assert json_data["Pk"] == "ASSET_TRANS#testuser123#BTC"
        assert json_data["Sk"] == "2024-01-01T12:00:00Z"
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["transaction_type"] == AssetTransactionType.BUY
        assert json_data["quantity"] == Decimal("2.5")
        assert json_data["price"] == Decimal("50000.00")
        assert json_data["total_amount"] == Decimal("125000.00")
        assert json_data["order_id"] == "order-123"
        assert json_data["status"] == AssetTransactionStatus.COMPLETED


class TestAssetTransactionEnums:
    """Test AssetTransaction enums"""

    def test_asset_transaction_type_values(self):
        """Test asset transaction type enum values"""
        assert AssetTransactionType.BUY == "BUY"
        assert AssetTransactionType.SELL == "SELL"

    def test_asset_transaction_status_values(self):
        """Test asset transaction status enum values"""
        assert AssetTransactionStatus.PENDING == "PENDING"
        assert AssetTransactionStatus.COMPLETED == "COMPLETED"
        assert AssetTransactionStatus.FAILED == "FAILED"

    def test_enum_serialization(self):
        """Test enum serialization"""
        assert AssetTransactionType.BUY.value == "BUY"
        assert AssetTransactionStatus.COMPLETED.value == "COMPLETED"