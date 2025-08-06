"""
Asset Transaction Entity

This module contains the AssetTransaction entity for managing asset transactions
in the multi-asset portfolio system.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal

from .enums import AssetTransactionType, AssetTransactionStatus


class AssetTransaction(BaseModel):
    """Asset Transaction entity for DynamoDB storage

    Database Schema:
    - PK: TRANS#{username}#{asset_id} (Primary Key)
    - SK: timestamp (Sort Key - ISO format string)

    Query Patterns:
    - Get specific transaction: PK = TRANS#{username}#{asset_id}, SK = timestamp
    - Get all transactions for user/asset: PK = TRANS#{username}#{asset_id}
    - Get transactions by date range: PK = TRANS#{username}#{asset_id}, SK between dates
    """

    Pk: str = Field(..., description="Primary Key - TRANS#{username}#{asset_id}")
    Sk: str = Field(..., description="Sort Key - timestamp (ISO format string)")

    username: str = Field(..., description="Username for easy access")
    asset_id: str = Field(..., description="Asset identifier")
    transaction_type: AssetTransactionType = Field(..., description="Type of transaction (BUY/SELL)")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total transaction value")
    order_id: Optional[str] = Field(None, description="Reference to order")
    status: AssetTransactionStatus = Field(default=AssetTransactionStatus.COMPLETED, description="Transaction status")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class AssetTransactionCreate(BaseModel):
    """Request model for creating an asset transaction"""

    username: str = Field(..., description="Username")
    asset_id: str = Field(..., description="Asset identifier")
    transaction_type: AssetTransactionType = Field(..., description="Type of transaction")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Price per unit in USD")
    order_id: Optional[str] = Field(None, description="Reference to order")

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}


class AssetTransactionResponse(BaseModel):
    """Response model for asset transaction information"""

    username: str = Field(..., description="Username")
    asset_id: str = Field(..., description="Asset identifier")
    transaction_type: AssetTransactionType = Field(..., description="Type of transaction")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total transaction value")
    order_id: Optional[str] = Field(None, description="Reference to order")
    status: AssetTransactionStatus = Field(..., description="Transaction status")
    created_at: datetime = Field(..., description="Transaction creation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }