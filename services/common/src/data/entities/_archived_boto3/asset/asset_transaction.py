"""
Asset Transaction Entity

This module contains the AssetTransaction entity for managing asset transactions
in the multi-asset portfolio system.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from ..entity_constants import (AssetTransactionFields, DatabaseFields,
                                FieldConstraints)
from .enums import AssetTransactionStatus, AssetTransactionType


class AssetTransaction(BaseModel):
    """Asset Transaction domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    transaction_type: AssetTransactionType = Field(..., description="Type of transaction (BUY/SELL)")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total transaction value")
    order_id: Optional[str] = Field(None, max_length=FieldConstraints.ORDER_ID_MAX_LENGTH, description="Reference to order")
    status: AssetTransactionStatus = Field(default=AssetTransactionStatus.COMPLETED, description="Transaction status")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class AssetTransactionItem(BaseModel):
    """Asset Transaction database model - includes DynamoDB fields (Pk, Sk)"""
    Pk: str = Field(..., description="Primary Key - TRANS#{username}#{asset_id}")
    Sk: str = Field(..., description="Sort Key - timestamp (ISO format string)")
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    transaction_type: AssetTransactionType = Field(..., description="Type of transaction (BUY/SELL)")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total transaction value")
    order_id: Optional[str] = Field(None, max_length=FieldConstraints.ORDER_ID_MAX_LENGTH, description="Reference to order")
    status: AssetTransactionStatus = Field(default=AssetTransactionStatus.COMPLETED, description="Transaction status")
    created_at: str = Field(..., description="Transaction creation timestamp (ISO string)")

    def get_key(self) -> dict:
        """Get database key for this asset transaction item"""
        return {
            DatabaseFields.PK: self.Pk,
            DatabaseFields.SK: self.Sk
        }

    @staticmethod
    def get_key_for_user_asset(username: str, asset_id: str) -> dict:
        """Get database key for a user's asset transactions (static method)"""
        return {
            DatabaseFields.PK: f"{AssetTransactionFields.PK_PREFIX}{username}#{asset_id}",
            DatabaseFields.SK: ""  # Empty SK for querying all transactions
        }

    @classmethod
    def from_asset_transaction(cls, asset_transaction: AssetTransaction) -> AssetTransactionItem:
        """Create AssetTransactionItem from AssetTransaction domain model"""
        # Use created_at as sort key for chronological ordering
        sort_key = asset_transaction.created_at.isoformat()
        return cls(
            Pk=f"{AssetTransactionFields.PK_PREFIX}{asset_transaction.username}#{asset_transaction.asset_id}",
            Sk=sort_key,
            username=asset_transaction.username,
            asset_id=asset_transaction.asset_id,
            transaction_type=asset_transaction.transaction_type,
            quantity=asset_transaction.quantity,
            price=asset_transaction.price,
            total_amount=asset_transaction.total_amount,
            order_id=asset_transaction.order_id,
            status=asset_transaction.status,
            created_at=asset_transaction.created_at.isoformat()
        )

    def to_asset_transaction(self) -> AssetTransaction:
        """Convert AssetTransactionItem to AssetTransaction domain model"""
        return AssetTransaction(
            username=self.username,
            asset_id=self.asset_id,
            transaction_type=self.transaction_type,
            quantity=self.quantity,
            price=self.price,
            total_amount=self.total_amount,
            order_id=self.order_id,
            status=self.status,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow()
        )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
