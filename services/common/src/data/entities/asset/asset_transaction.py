"""
Asset Transaction Entity

This module contains the AssetTransaction entity for managing asset transactions
in the multi-asset portfolio system.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute

from ..entity_constants import (AssetTransactionFields, FieldConstraints,
                                UserConstants)
from ...database.database_constants import AWSConfig, TableNames
from ..datetime_utils import get_current_utc
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
    created_at: datetime = Field(default_factory=get_current_utc, description="Transaction creation timestamp")
    updated_at: datetime = Field(default_factory=get_current_utc, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )

    def get_pk(self) -> str:
        """Build primary key for asset transaction using username and asset_id"""
        return f"{AssetTransactionFields.PK_PREFIX}{self.username}#{self.asset_id}"

    @staticmethod
    def build_pk(username: str, asset_id: str) -> str:
        """Build primary key for asset transaction using username and asset_id"""
        return f"{AssetTransactionFields.PK_PREFIX}{username}#{asset_id}"


class AssetTransactionItem(Model):
    """Asset Transaction PynamoDB model - handles DynamoDB operations"""

    class Meta:
        """Meta class for AssetTransactionItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary key
    Pk = UnicodeAttribute(hash_key=True)
    Sk = UnicodeAttribute(range_key=True)

    # Transaction fields
    username = UnicodeAttribute()
    asset_id = UnicodeAttribute()
    transaction_type = UnicodeAttribute()
    quantity = UnicodeAttribute()  # Store as string for Decimal precision
    price = UnicodeAttribute()     # Store as string for Decimal precision
    total_amount = UnicodeAttribute()  # Store as string for Decimal precision
    order_id = UnicodeAttribute(null=True)
    status = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_asset_transaction(cls, asset_transaction: AssetTransaction) -> 'AssetTransactionItem':
        """Create AssetTransactionItem from AssetTransaction domain model"""
        # Use created_at as sort key for chronological ordering
        sort_key = asset_transaction.created_at.isoformat()
        return cls(
            Pk=f"{AssetTransactionFields.PK_PREFIX}{asset_transaction.username}#{asset_transaction.asset_id}",
            Sk=sort_key,
            username=asset_transaction.username,
            asset_id=asset_transaction.asset_id,
            transaction_type=asset_transaction.transaction_type.value,
            quantity=str(asset_transaction.quantity),
            price=str(asset_transaction.price),
            total_amount=str(asset_transaction.total_amount),
            order_id=asset_transaction.order_id,
            status=asset_transaction.status.value,
            created_at=asset_transaction.created_at.replace(tzinfo=None)  # Convert to naive UTC for PynamoDB
        )

    def to_asset_transaction(self) -> AssetTransaction:
        """Convert AssetTransactionItem to AssetTransaction domain model"""
        return AssetTransaction(
            username=self.username,
            asset_id=self.asset_id,
            transaction_type=AssetTransactionType(self.transaction_type),
            quantity=Decimal(self.quantity),
            price=Decimal(self.price),
            total_amount=Decimal(self.total_amount),
            order_id=self.order_id,
            status=AssetTransactionStatus(self.status),
            created_at=self.created_at.replace(tzinfo=timezone.utc)  # Convert back to timezone-aware
        )
