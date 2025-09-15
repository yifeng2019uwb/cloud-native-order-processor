from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re
from ..entity_constants import AssetFields, DatabaseFields, FieldConstraints


class Asset(BaseModel):
    """Asset domain model - pure business entity without database fields"""
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset symbol (primary key)")
    name: str = Field(..., max_length=FieldConstraints.ASSET_NAME_MAX_LENGTH, description="Asset full name")
    description: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DESCRIPTION_MAX_LENGTH, description="Asset description")
    category: str = Field(..., max_length=FieldConstraints.ASSET_CATEGORY_MAX_LENGTH, description="Asset category (major/altcoin/stablecoin)")
    amount: Decimal = Field(..., description="Available inventory amount")
    price_usd: Decimal = Field(..., description="Current USD price")
    is_active: bool = Field(default=True, description="Whether asset is available for trading")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # CoinGecko API fields - Comprehensive market data
    symbol: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_SYMBOL_MAX_LENGTH, description="Ticker symbol (e.g., BTC)")
    image: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_IMAGE_MAX_LENGTH, description="URL to coin logo")
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
    ath_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time high")
    atl: Optional[float] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[float] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time low")

    # Additional metadata
    last_updated: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_LAST_UPDATED_MAX_LENGTH, description="Last update timestamp from CoinGecko")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

    @model_validator(mode="before")
    @classmethod
    def trim_strings(cls, values):
        for field in ["asset_id", "name", "description", "category", "symbol", "image"]:
            if field in values and isinstance(values[field], str):
                values[field] = values[field].strip()
        return values


class AssetItem(BaseModel):
    """Asset database item - includes DynamoDB-specific fields"""
    # DynamoDB fields (using existing schema)
    product_id: str = Field(..., description="Product ID (primary key)")

    # Asset fields (same as Asset entity)
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset symbol")
    name: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_NAME_MAX_LENGTH, description="Asset full name")
    description: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DESCRIPTION_MAX_LENGTH, description="Asset description")
    category: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_CATEGORY_MAX_LENGTH, description="Asset category")
    amount: Optional[Decimal] = Field(None, description="Available inventory amount")
    price_usd: Decimal = Field(..., description="Current USD price")
    is_active: bool = Field(default=True, description="Whether asset is available for trading")
    created_at: Optional[str] = Field(None, description="Creation timestamp (ISO string)")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")

    # CoinGecko API fields
    symbol: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_SYMBOL_MAX_LENGTH, description="Ticker symbol")
    image: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_IMAGE_MAX_LENGTH, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Rank by market cap")
    current_price: Optional[float] = Field(None, description="Current price in USD")
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[float] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[float] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[float] = Field(None, description="Price change percentage in last 30 days")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    market_cap_change_24h: Optional[float] = Field(None, description="Market cap change in last 24h")
    market_cap_change_percentage_24h: Optional[float] = Field(None, description="Market cap change percentage in last 24h")
    total_volume_24h: Optional[float] = Field(None, description="Total trading volume in last 24h")
    volume_change_24h: Optional[float] = Field(None, description="Volume change in last 24h")
    ath: Optional[float] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time high")
    atl: Optional[float] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[float] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time low")
    last_updated: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_LAST_UPDATED_MAX_LENGTH, description="Last update timestamp")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

    @classmethod
    def from_entity(cls, asset: Asset) -> AssetItem:
        """Convert Asset entity to AssetItem for database storage"""
        return cls(
            product_id=asset.asset_id,
            asset_id=asset.asset_id,
            name=asset.name,
            description=asset.description,
            category=asset.category,
            amount=asset.amount,
            price_usd=asset.price_usd,
            is_active=asset.is_active,
            created_at=asset.created_at.isoformat(),
            updated_at=asset.updated_at.isoformat(),
            symbol=asset.symbol,
            image=asset.image,
            market_cap_rank=asset.market_cap_rank,
            current_price=asset.current_price,
            high_24h=asset.high_24h,
            low_24h=asset.low_24h,
            circulating_supply=asset.circulating_supply,
            total_supply=asset.total_supply,
            max_supply=asset.max_supply,
            price_change_24h=asset.price_change_24h,
            price_change_percentage_24h=asset.price_change_percentage_24h,
            price_change_percentage_7d=asset.price_change_percentage_7d,
            price_change_percentage_30d=asset.price_change_percentage_30d,
            market_cap=asset.market_cap,
            market_cap_change_24h=asset.market_cap_change_24h,
            market_cap_change_percentage_24h=asset.market_cap_change_percentage_24h,
            total_volume_24h=asset.total_volume_24h,
            volume_change_24h=asset.volume_change_24h,
            ath=asset.ath,
            ath_change_percentage=asset.ath_change_percentage,
            ath_date=asset.ath_date,
            atl=asset.atl,
            atl_change_percentage=asset.atl_change_percentage,
            atl_date=asset.atl_date,
            last_updated=asset.last_updated,
            sparkline_7d=asset.sparkline_7d
        )

    def to_entity(self) -> Asset:
        """Convert AssetItem to Asset entity"""
        return Asset(
            asset_id=self.asset_id,
            name=self.name or '',
            description=self.description,
            category=self.category or 'unknown',
            amount=self.amount or Decimal('0'),
            price_usd=self.price_usd,
            is_active=self.is_active,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow(),
            updated_at=datetime.fromisoformat(self.updated_at.replace('Z', '+00:00')) if self.updated_at else datetime.utcnow(),
            symbol=self.symbol,
            image=self.image,
            market_cap_rank=self.market_cap_rank,
            current_price=self.current_price,
            high_24h=self.high_24h,
            low_24h=self.low_24h,
            circulating_supply=self.circulating_supply,
            total_supply=self.total_supply,
            max_supply=self.max_supply,
            price_change_24h=self.price_change_24h,
            price_change_percentage_24h=self.price_change_percentage_24h,
            price_change_percentage_7d=self.price_change_percentage_7d,
            price_change_percentage_30d=self.price_change_percentage_30d,
            market_cap=self.market_cap,
            market_cap_change_24h=self.market_cap_change_24h,
            market_cap_change_percentage_24h=self.market_cap_change_percentage_24h,
            total_volume_24h=self.total_volume_24h,
            volume_change_24h=self.volume_change_24h,
            ath=self.ath,
            ath_change_percentage=self.ath_change_percentage,
            ath_date=self.ath_date,
            atl=self.atl,
            atl_change_percentage=self.atl_change_percentage,
            atl_date=self.atl_date,
            last_updated=self.last_updated,
            sparkline_7d=self.sparkline_7d
        )
