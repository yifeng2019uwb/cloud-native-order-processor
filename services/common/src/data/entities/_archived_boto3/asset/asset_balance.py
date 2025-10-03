"""
Asset Balance Entity

This module contains the AssetBalance entity for managing user asset balances
in the multi-asset portfolio system.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
from ..entity_constants import AssetBalanceFields, DatabaseFields, FieldConstraints


class AssetBalance(BaseModel):
    """Asset Balance domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset identifier")
    quantity: Decimal = Field(default=Decimal('0.00'), description="Current asset quantity")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class AssetBalanceItem(BaseModel):
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
        """Convert AssetBalanceItem to AssetBalance domain model"""
        return AssetBalance(
            username=self.username,
            asset_id=self.asset_id,
            quantity=self.quantity,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow(),
            updated_at=datetime.fromisoformat(self.updated_at.replace('Z', '+00:00')) if self.updated_at else datetime.utcnow()
        )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
