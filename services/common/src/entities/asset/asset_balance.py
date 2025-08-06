"""
Asset Balance Entity

This module contains the AssetBalance entity for managing user asset balances
in the multi-asset portfolio system.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal


class AssetBalance(BaseModel):
    """Asset Balance entity for DynamoDB storage

    Database Schema:
    - PK: username (Primary Key)
    - SK: ASSET#{asset_id} (Sort Key)

    Query Patterns:
    - Get specific asset balance: PK = username, SK = ASSET#{asset_id}
    - Get all asset balances for user: PK = username, SK begins_with "ASSET#"
    """

    Pk: str = Field(..., description="Primary Key - Username")
    Sk: str = Field(..., description="Sort Key - ASSET#{asset_id}")

    username: str = Field(..., description="Username for easy access")
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(default=Decimal('0.00'), description="Current asset quantity")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class AssetBalanceCreate(BaseModel):
    """Request model for creating an asset balance"""

    username: str = Field(..., description="Username")
    asset_id: str = Field(..., description="Asset identifier")
    initial_quantity: Decimal = Field(default=Decimal('0.00'), description="Initial asset quantity")

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}


class AssetBalanceResponse(BaseModel):
    """Response model for asset balance information"""

    username: str = Field(..., description="Username")
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(..., description="Current asset quantity")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }