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


class AssetBalance(BaseModel):
    """Asset Balance domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    quantity: Decimal = Field(default=Decimal('0.00'), description="Current asset quantity")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class AssetBalanceData(BaseModel):
    """Asset Balance database model - includes DynamoDB fields (Pk, Sk)"""
    Pk: str = Field(..., description="Primary Key - Username")
    Sk: str = Field(..., description="Sort Key - ASSET#{asset_id}")
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    quantity: Decimal = Field(default=Decimal('0.00'), description="Current asset quantity")
    created_at: str = Field(..., description="Asset balance creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")

    def get_key(self) -> dict:
        """Get database key for this asset balance item"""
        return {
            DatabaseFields.PK: self.Pk,
            DatabaseFields.SK: self.Sk
        }

    @staticmethod
    def get_key_for_user_asset(username: str, asset_id: str) -> dict:
        """Get database key for a user's asset balance (static method)"""
        return {
            DatabaseFields.PK: username,
            DatabaseFields.SK: f"{AssetBalanceFields.SK_PREFIX}{asset_id}"
        }

    @classmethod
    def from_asset_balance(cls, asset_balance: AssetBalance) -> AssetBalanceItem:
        """Create AssetBalanceItem from AssetBalance domain model"""
        return cls(
            Pk=asset_balance.username,
            Sk=f"{AssetBalanceFields.SK_PREFIX}{asset_balance.asset_id}",
            username=asset_balance.username,
            asset_id=asset_balance.asset_id,
            quantity=asset_balance.quantity,
            created_at=asset_balance.created_at.isoformat(),
            updated_at=asset_balance.updated_at.isoformat()
        )

    def to_asset_balance(self) -> AssetBalance:
        """Convert AssetBalanceData to AssetBalance domain model"""
        # Parse ISO string timestamps to datetime objects
        created_at = datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.now(timezone.utc)
        updated_at = datetime.fromisoformat(self.updated_at.replace('Z', '+00:00')) if self.updated_at else datetime.now(timezone.utc)
        
        return AssetBalance(
            username=self.username,
            asset_id=self.asset_id,
            quantity=self.quantity,
            created_at=created_at,
            updated_at=updated_at
        )

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

    def model_dump(self, **kwargs):
        """Pydantic-compatible model_dump method for testing"""
        return {
            'Pk': self.Pk,
            'Sk': self.Sk,
            'username': self.username,
            'asset_id': self.asset_id,
            'quantity': self.quantity,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(condition=condition, **kwargs)
