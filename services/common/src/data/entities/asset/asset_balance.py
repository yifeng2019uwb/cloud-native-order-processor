"""
Asset Balance Entity

This module contains the AssetBalance entity for managing user asset balances
in the multi-asset portfolio system.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
# Optional import removed as it's not used

from pydantic import BaseModel, Field
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from ..entity_constants import (AssetBalanceFields, AWSConfig, DatabaseFields,
                                FieldConstraints, TableNames, UserConstants)
from ..datetime_utils import get_current_utc


class AssetBalance(BaseModel):
    """Asset Balance domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    quantity: Decimal = Field(default=Decimal('0.00'), description="Current asset quantity")
    created_at: datetime = Field(default_factory=get_current_utc)
    updated_at: datetime = Field(default_factory=get_current_utc)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


# ==================== PYNAMODB MODEL ====================

class AssetBalanceItem(Model):
    """Asset Balance PynamoDB model - handles DynamoDB operations for user asset balances"""

    class Meta:
        """Meta class for AssetBalanceItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary Key
    Pk = UnicodeAttribute(hash_key=True)
    Sk = UnicodeAttribute(range_key=True, default=AssetBalanceFields.SK_VALUE)

    # Asset Balance fields
    username = UnicodeAttribute()
    asset_id = UnicodeAttribute()
    quantity = UnicodeAttribute()  # Store as string for Decimal precision
    entity_type = UnicodeAttribute(default=AssetBalanceFields.DEFAULT_ENTITY_TYPE)

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_asset_balance(cls, asset_balance: AssetBalance) -> AssetBalanceItem:
        """Create AssetBalanceItem from AssetBalance domain model"""
        asset_balance_item = cls()
        asset_balance_item.Pk = asset_balance.username
        asset_balance_item.Sk = f"{AssetBalanceFields.SK_PREFIX}{asset_balance.asset_id}"
        asset_balance_item.username = asset_balance.username
        asset_balance_item.asset_id = asset_balance.asset_id
        asset_balance_item.quantity = str(asset_balance.quantity)
        asset_balance_item.created_at = asset_balance.created_at
        asset_balance_item.updated_at = asset_balance.updated_at
        return asset_balance_item

    def to_asset_balance(self) -> AssetBalance:
        """Convert AssetBalanceItem to AssetBalance domain model"""
        return AssetBalance(
            username=self.username,
            asset_id=self.asset_id,
            quantity=Decimal(self.quantity),
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(condition=condition, **kwargs)
