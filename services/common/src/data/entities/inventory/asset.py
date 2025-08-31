from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re


class AssetCreate(BaseModel):
    """Request model for creating new crypto assets with comprehensive CoinGecko data"""
    asset_id: str = Field(..., description="Asset symbol (3-6 characters, uppercase)")
    name: str = Field(..., description="Asset full name")
    description: Optional[str] = Field(None, description="Asset description (optional)")
    category: str = Field(..., description="Asset category")
    amount: Decimal = Field(..., description="Available inventory amount")
    price_usd: Decimal = Field(..., description="Current USD price")

    # CoinGecko API fields - Comprehensive market data
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")

    # Price data
    current_price: Optional[float] = Field(None, description="Current price in USD")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")

    # Supply information
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")

    # Price changes
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[float] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[float] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[float] = Field(None, description="Price change percentage in last 30 days")

    # Market metrics
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    market_cap_change_24h: Optional[float] = Field(None, description="Market cap change in last 24h")
    market_cap_change_percentage_24h: Optional[float] = Field(None, description="Market cap change percentage in last 24h")

    # Volume and trading
    total_volume_24h: Optional[float] = Field(None, description="Total trading volume in last 24h")
    volume_change_24h: Optional[float] = Field(None, description="Volume change in last 24h")

    # Historical context
    ath: Optional[float] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, description="Date of all-time high")
    atl: Optional[float] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[float] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, description="Date of all-time low")

    # Additional metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp from CoinGecko")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

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
                "price_usd": 45000.50,
                "symbol": "BTC",
                "market_cap_rank": 1,
                "market_cap": 850000000000,
                "price_change_percentage_24h": 2.5,
                "total_volume_24h": 25000000000
            }
        }


class Asset(BaseModel):
    """Core asset entity model with comprehensive CoinGecko data"""

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

    # CoinGecko API fields - Comprehensive market data
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")

    # Price data
    current_price: Optional[float] = Field(None, description="Current price in USD")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")

    # Supply information
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")

    # Price changes
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[float] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[float] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[float] = Field(None, description="Price change percentage in last 30 days")

    # Market metrics
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    market_cap_change_24h: Optional[float] = Field(None, description="Market cap change in last 24h")
    market_cap_change_percentage_24h: Optional[float] = Field(None, description="Market cap change percentage in last 24h")

    # Volume and trading
    total_volume_24h: Optional[float] = Field(None, description="Total trading volume in last 24h")
    volume_change_24h: Optional[float] = Field(None, description="Volume change in last 24h")

    # Historical context
    ath: Optional[float] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, description="Date of all-time high")
    atl: Optional[float] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[float] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, description="Date of all-time low")

    # Additional metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp from CoinGecko")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

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
                "symbol": "BTC",
                "market_cap_rank": 1,
                "market_cap": 850000000000,
                "price_change_percentage_24h": 2.5,
                "total_volume_24h": 25000000000,
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
    """Model for updating existing assets with comprehensive CoinGecko data (asset_id and name cannot be changed)"""

    asset_id: Optional[str] = Field(None, description="Asset identifier (e.g., BTC, ETH)")
    description: Optional[str] = Field(None, description="Updated asset description")
    category: Optional[str] = Field(None, description="Updated asset category")
    amount: Optional[Decimal] = Field(None, description="Updated inventory amount")
    price_usd: Optional[Decimal] = Field(None, description="Updated USD price")
    is_active: Optional[bool] = Field(None, description="Updated active status")

    # CoinGecko API fields - Comprehensive market data
    symbol: Optional[str] = Field(None, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")

    # Price data
    current_price: Optional[Decimal] = Field(None, description="Current price in USD")
    high_24h: Optional[Decimal] = Field(None, description="24-hour high price")
    low_24h: Optional[Decimal] = Field(None, description="24-hour low price")

    # Supply information
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    max_supply: Optional[Decimal] = Field(None, description="Maximum supply")

    # Price changes
    price_change_24h: Optional[Decimal] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[Decimal] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[Decimal] = Field(None, description="Price change percentage in last 30 days")

    # Market metrics
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    market_cap_change_24h: Optional[Decimal] = Field(None, description="Market cap change in last 24h")
    market_cap_change_percentage_24h: Optional[Decimal] = Field(None, description="Market cap change percentage in last 24h")

    # Volume and trading
    total_volume_24h: Optional[Decimal] = Field(None, description="Total trading volume in last 24h")
    volume_change_24h: Optional[Decimal] = Field(None, description="Volume change in last 24h")

    # Historical context
    ath: Optional[Decimal] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[Decimal] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, description="Date of all-time high")
    atl: Optional[Decimal] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[Decimal] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, description="Date of all-time low")

    # Additional metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp from CoinGecko")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

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
                "is_active": True,
                "symbol": "BTC",
                "market_cap_rank": 1,
                "market_cap": 850000000000,
                "price_change_percentage_24h": 2.5,
                "total_volume_24h": 25000000000
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