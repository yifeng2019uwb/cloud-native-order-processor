from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re


class AssetCreate(BaseModel):
    """Request model for creating new crypto assets"""
    asset_id: str = Field(..., description="Asset symbol (3-6 characters, uppercase)")
    name: str = Field(..., description="Asset full name")
    description: Optional[str] = Field(None, description="Asset description (optional)")
    category: str = Field(..., description="Asset category")
    amount: Decimal = Field(..., description="Available inventory amount")
    price_usd: Decimal = Field(..., description="Current USD price")
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    market_cap: Optional[float] = Field(None, description="Market capitalization")

    @model_validator(mode="before")
    @classmethod
    def trim_strings(cls, values):
        for field in ["asset_id", "name", "description", "category", "symbol", "image"]:
            if field in values and isinstance(values[field], str):
                values[field] = values[field].strip()
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50
            }
        }


class Asset(BaseModel):
    """Core asset entity model"""

    asset_id: str = Field(
        ...,
        description="Asset symbol (primary key)"
    )

    name: str = Field(
        ...,
        description="Asset full name"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description"
    )

    category: str = Field(
        ...,
        description="Asset category (major/altcoin/stablecoin)"
    )

    amount: Decimal = Field(
        ...,
        description="Available inventory amount"
    )

    price_usd: Decimal = Field(
        ...,
        description="Current USD price"
    )

    # New fields
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    market_cap: Optional[float] = Field(None, description="Market capitalization")

    is_active: bool = Field(
        default=True,
        description="Whether asset is available for trading"
    )

    created_at: datetime = Field(
        ...,
        description="Asset creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50,
                "is_active": True,
                "created_at": "2025-07-11T09:00:00Z",
                "updated_at": "2025-07-11T10:30:00Z"
            }
        }


class AssetResponse(BaseModel):
    """Safe asset model for API responses"""

    asset_id: str = Field(
        ...,
        description="Asset symbol"
    )

    name: str = Field(
        ...,
        description="Asset full name"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description"
    )

    category: str = Field(
        ...,
        description="Asset category"
    )

    amount: Decimal = Field(
        ...,
        description="Available inventory amount"
    )

    price_usd: Decimal = Field(
        ...,
        description="Current USD price"
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available for trading"
    )

    created_at: datetime = Field(
        ...,
        description="Asset creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50,
                "is_active": True,
                "created_at": "2025-07-11T09:00:00Z",
                "updated_at": "2025-07-11T10:30:00Z"
            }
        }


class AssetUpdate(BaseModel):
    """Model for updating existing assets (asset_id and name cannot be changed)"""

    description: Optional[str] = Field(None, description="Updated asset description")
    category: Optional[str] = Field(None, description="Updated asset category")
    amount: Optional[Decimal] = Field(None, description="Updated inventory amount")
    price_usd: Optional[Decimal] = Field(None, description="Updated USD price")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    market_cap: Optional[float] = Field(None, description="Market capitalization")

    @model_validator(mode="before")
    @classmethod
    def trim_strings(cls, values):
        for field in ["description", "category", "symbol", "image"]:
            if field in values and isinstance(values[field], str):
                values[field] = values[field].strip()
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description",
                "category": "major",
                "amount": 750.50,
                "price_usd": 47000.25,
                "is_active": True
            }
        }


# Asset list response for API endpoints
class AssetListResponse(BaseModel):
    """Response model for asset list endpoints"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of assets"
    )

    total_count: int = Field(
        ...,
        description="Total number of assets"
    )

    active_count: int = Field(
        ...,
        description="Number of active assets"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assets": [
                    {
                        "asset_id": "BTC",
                        "name": "Bitcoin",
                        "description": "Digital currency",
                        "category": "major",
                        "amount": 500.25,
                        "price_usd": 45000.50,
                        "is_active": True,
                        "created_at": "2025-07-11T09:00:00Z",
                        "updated_at": "2025-07-11T10:30:00Z"
                    }
                ],
                "total_count": 4,
                "active_count": 3
            }
        }