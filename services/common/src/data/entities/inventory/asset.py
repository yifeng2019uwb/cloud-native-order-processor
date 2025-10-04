from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from pynamodb.attributes import (
    UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute, BooleanAttribute)
from pynamodb.models import Model

from ..entity_constants import AssetFields, FieldConstraints, AWSConfig, TableNames, UserConstants
from ..datetime_utils import safe_parse_datetime, get_current_utc


class Asset(BaseModel):
    """Asset domain model - pure business entity without database fields"""
    asset_id: str = Field(..., max_length=FieldConstraints.ASSET_ID_MAX_LENGTH, description="Asset symbol (primary key)")
    name: str = Field(..., max_length=FieldConstraints.ASSET_NAME_MAX_LENGTH, description="Asset full name")
    description: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DESCRIPTION_MAX_LENGTH, description="Asset description")
    category: str = Field(..., max_length=FieldConstraints.ASSET_CATEGORY_MAX_LENGTH, description="Asset category (major/altcoin/stablecoin)")
    amount: Decimal = Field(..., description="Available inventory amount")
    price_usd: Decimal = Field(..., description="Current USD price")
    is_active: bool = Field(default=True, description="Whether asset is available for trading")
    created_at: datetime = Field(default_factory=get_current_utc)
    updated_at: datetime = Field(default_factory=get_current_utc)

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
        """Trim whitespace from string fields"""
        string_fields = [
            AssetFields.ASSET_ID, AssetFields.NAME, AssetFields.DESCRIPTION,
            AssetFields.CATEGORY, AssetFields.SYMBOL, AssetFields.IMAGE
        ]
        for field in string_fields:
            if field in values and isinstance(values[field], str):
                values[field] = values[field].strip()
        return values


class AssetData(BaseModel):
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
    current_price: Optional[Decimal] = Field(None, description="Current price in USD")
    high_24h: Optional[Decimal] = Field(None, description="24-hour high price")
    low_24h: Optional[Decimal] = Field(None, description="24-hour low price")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    max_supply: Optional[Decimal] = Field(None, description="Maximum supply")
    price_change_24h: Optional[Decimal] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[Decimal] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[Decimal] = Field(None, description="Price change percentage in last 30 days")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    market_cap_change_24h: Optional[Decimal] = Field(None, description="Market cap change in last 24h")
    market_cap_change_percentage_24h: Optional[Decimal] = Field(None, description="Market cap change percentage in last 24h")
    total_volume_24h: Optional[Decimal] = Field(None, description="Total trading volume in last 24h")
    volume_change_24h: Optional[Decimal] = Field(None, description="Volume change in last 24h")
    ath: Optional[Decimal] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[Decimal] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time high")
    atl: Optional[Decimal] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[Decimal] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_DATE_MAX_LENGTH, description="Date of all-time low")
    last_updated: Optional[str] = Field(None, max_length=FieldConstraints.ASSET_LAST_UPDATED_MAX_LENGTH, description="Last update timestamp")
    sparkline_7d: Optional[dict] = Field(None, description="7-day price sparkline data")

    @model_validator(mode="before")
    @classmethod
    def convert_floats_to_decimal(cls, values):
        """Convert float values to Decimal for DynamoDB compatibility"""
        if isinstance(values, dict):
            decimal_fields = [
                AssetFields.CURRENT_PRICE, AssetFields.HIGH_24H, AssetFields.LOW_24H,
                AssetFields.CIRCULATING_SUPPLY, AssetFields.TOTAL_SUPPLY, AssetFields.MAX_SUPPLY,
                AssetFields.PRICE_CHANGE_24H, AssetFields.PRICE_CHANGE_PERCENTAGE_24H,
                AssetFields.PRICE_CHANGE_PERCENTAGE_7D, AssetFields.PRICE_CHANGE_PERCENTAGE_30D,
                AssetFields.MARKET_CAP, AssetFields.MARKET_CAP_CHANGE_24H,
                AssetFields.MARKET_CAP_CHANGE_PERCENTAGE_24H, AssetFields.TOTAL_VOLUME_24H,
                AssetFields.VOLUME_CHANGE_24H, AssetFields.ATH, AssetFields.ATH_CHANGE_PERCENTAGE,
                AssetFields.ATL, AssetFields.ATL_CHANGE_PERCENTAGE
            ]
            for field in decimal_fields:
                if field in values and values[field] is not None and isinstance(values[field], (int, float)):
                    values[field] = Decimal(str(values[field]))
        return values

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
            created_at=safe_parse_datetime(self.created_at),
            updated_at=safe_parse_datetime(self.updated_at),
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


# ==================== PYNAMODB MODEL ====================

class AssetItem(Model):
    """Asset PynamoDB model - handles DynamoDB operations for assets"""

    class Meta:
        """Meta class for AssetItem"""
        table_name = os.getenv(UserConstants.INVENTORY_TABLE_ENV_VAR, TableNames.INVENTORY)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary Key - using existing schema with product_id
    product_id = UnicodeAttribute(hash_key=True)  # asset_id (primary key)

    # Asset fields
    asset_id = UnicodeAttribute()
    name = UnicodeAttribute()
    description = UnicodeAttribute(null=True)
    category = UnicodeAttribute()
    amount = NumberAttribute()  # Store as number for Decimal precision
    price_usd = NumberAttribute()  # Store as number for Decimal precision
    is_active = BooleanAttribute(default=True)

    # CoinGecko API fields
    symbol = UnicodeAttribute(null=True)
    image = UnicodeAttribute(null=True)
    market_cap_rank = NumberAttribute(null=True)
    current_price = NumberAttribute(null=True)  # Store as number for Decimal precision
    high_24h = NumberAttribute(null=True)
    low_24h = NumberAttribute(null=True)
    circulating_supply = NumberAttribute(null=True)
    total_supply = NumberAttribute(null=True)
    max_supply = NumberAttribute(null=True)
    price_change_24h = NumberAttribute(null=True)
    price_change_percentage_24h = NumberAttribute(null=True)
    price_change_percentage_7d = NumberAttribute(null=True)
    price_change_percentage_30d = NumberAttribute(null=True)
    market_cap = NumberAttribute(null=True)
    market_cap_change_24h = NumberAttribute(null=True)
    market_cap_change_percentage_24h = NumberAttribute(null=True)
    total_volume_24h = NumberAttribute(null=True)
    volume_change_24h = NumberAttribute(null=True)
    ath = NumberAttribute(null=True)
    ath_change_percentage = NumberAttribute(null=True)
    ath_date = UnicodeAttribute(null=True)
    atl = NumberAttribute(null=True)
    atl_change_percentage = NumberAttribute(null=True)
    atl_date = UnicodeAttribute(null=True)
    last_updated = UnicodeAttribute(null=True)
    sparkline_7d = UnicodeAttribute(null=True)  # Store as JSON string

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_asset(cls, asset: Asset) -> AssetItem:
        """Create AssetItem from Asset domain model"""
        asset_item = cls()
        asset_item.product_id = asset.asset_id
        asset_item.asset_id = asset.asset_id
        asset_item.name = asset.name
        asset_item.description = asset.description
        asset_item.category = asset.category
        asset_item.amount = float(asset.amount)
        asset_item.price_usd = float(asset.price_usd)
        asset_item.is_active = asset.is_active
        asset_item.symbol = asset.symbol
        asset_item.image = asset.image
        asset_item.market_cap_rank = asset.market_cap_rank
        asset_item.current_price = asset.current_price
        asset_item.high_24h = asset.high_24h
        asset_item.low_24h = asset.low_24h
        asset_item.circulating_supply = asset.circulating_supply
        asset_item.total_supply = asset.total_supply
        asset_item.max_supply = asset.max_supply
        asset_item.price_change_24h = asset.price_change_24h
        asset_item.price_change_percentage_24h = asset.price_change_percentage_24h
        asset_item.price_change_percentage_7d = asset.price_change_percentage_7d
        asset_item.price_change_percentage_30d = asset.price_change_percentage_30d
        asset_item.market_cap = asset.market_cap
        asset_item.market_cap_change_24h = asset.market_cap_change_24h
        asset_item.market_cap_change_percentage_24h = asset.market_cap_change_percentage_24h
        asset_item.total_volume_24h = asset.total_volume_24h
        asset_item.volume_change_24h = asset.volume_change_24h
        asset_item.ath = asset.ath
        asset_item.ath_change_percentage = asset.ath_change_percentage
        asset_item.ath_date = asset.ath_date
        asset_item.atl = asset.atl
        asset_item.atl_change_percentage = asset.atl_change_percentage
        asset_item.atl_date = asset.atl_date
        asset_item.last_updated = asset.last_updated
        asset_item.sparkline_7d = json.dumps(asset.sparkline_7d) if asset.sparkline_7d else None
        asset_item.created_at = asset.created_at
        asset_item.updated_at = asset.updated_at
        return asset_item

    def to_asset(self) -> Asset:
        """Convert AssetItem to Asset domain model"""
        return Asset(
            asset_id=self.asset_id,
            name=self.name,
            description=self.description,
            category=self.category,
            amount=self.amount,
            price_usd=self.price_usd,
            is_active=self.is_active,
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
            sparkline_7d=json.loads(self.sparkline_7d) if self.sparkline_7d else None,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = get_current_utc()
        return super().save(condition=condition, **kwargs)
