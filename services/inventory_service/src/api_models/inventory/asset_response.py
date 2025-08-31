"""
Asset response models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_response.py
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AssetResponse(BaseModel):
    """Enhanced asset response model for frontend display with comprehensive market data"""

    asset_id: str = Field(
        ...,
        description="Asset symbol/identifier",
        example="BTC"
    )

    name: str = Field(
        ...,
        description="Asset display name",
        example="Bitcoin"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description",
        example="Digital currency and store of value"
    )

    category: str = Field(
        ...,
        description="Asset category",
        example="major"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price",
        example=45000.50
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available for viewing/ordering",
        example=True
    )

    # Enhanced fields for frontend display
    symbol: Optional[str] = Field(
        None,
        description="Ticker symbol for consistent icon display",
        example="BTC"
    )

    image: Optional[str] = Field(
        None,
        description="URL to coin logo/icon",
        example="https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
    )

    market_cap_rank: Optional[int] = Field(
        None,
        description="Market cap ranking for proper ordering",
        example=1
    )

    # Market metrics for enhanced display
    market_cap: Optional[float] = Field(
        None,
        description="Market capitalization in USD",
        example=850000000000
    )

    price_change_percentage_24h: Optional[float] = Field(
        None,
        description="24-hour price change percentage",
        example=2.5
    )

    total_volume_24h: Optional[float] = Field(
        None,
        description="24-hour trading volume in USD",
        example=25000000000
    )

    # Price range for trading context
    high_24h: Optional[float] = Field(
        None,
        description="24-hour high price",
        example=46000.00
    )

    low_24h: Optional[float] = Field(
        None,
        description="24-hour low price",
        example=44000.00
    )

    # Supply information
    circulating_supply: Optional[float] = Field(
        None,
        description="Circulating supply",
        example=19500000
    )

    # Additional context
    last_updated: Optional[datetime] = Field(
        None,
        description="Last time asset data was updated"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "price_usd": 45000.50,
                "is_active": True,
                "symbol": "BTC",
                "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                "market_cap_rank": 1,
                "market_cap": 850000000000,
                "price_change_percentage_24h": 2.5,
                "total_volume_24h": 25000000000,
                "high_24h": 46000.00,
                "low_24h": 44000.00,
                "circulating_supply": 19500000
            }
        }
    )


class AssetDetailResponse(BaseModel):
    """Comprehensive detailed asset response for individual asset lookup with full market data"""

    asset_id: str = Field(
        ...,
        description="Asset symbol/identifier"
    )

    name: str = Field(
        ...,
        description="Asset display name"
    )

    description: Optional[str] = Field(
        None,
        description="Detailed asset description"
    )

    category: str = Field(
        ...,
        description="Asset category"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price"
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available"
    )

    # Enhanced fields for detailed view
    symbol: Optional[str] = Field(
        None,
        description="Ticker symbol for consistent icon display"
    )

    image: Optional[str] = Field(
        None,
        description="URL to coin logo/icon"
    )

    market_cap_rank: Optional[int] = Field(
        None,
        description="Market cap ranking"
    )

    # For individual asset view, we can show availability status without exact amounts
    availability_status: str = Field(
        ...,
        description="Human-readable availability status",
        example="Available"
    )

    # Comprehensive market data
    market_cap: Optional[float] = Field(
        None,
        description="Market capitalization in USD"
    )

    price_change_24h: Optional[float] = Field(
        None,
        description="24-hour price change in USD"
    )

    price_change_percentage_24h: Optional[float] = Field(
        None,
        description="24-hour price change percentage"
    )

    price_change_percentage_7d: Optional[float] = Field(
        None,
        description="7-day price change percentage"
    )

    price_change_percentage_30d: Optional[float] = Field(
        None,
        description="30-day price change percentage"
    )

    # Price range analysis
    high_24h: Optional[float] = Field(
        None,
        description="24-hour high price"
    )

    low_24h: Optional[float] = Field(
        None,
        description="24-hour low price"
    )

    # Volume and trading metrics
    total_volume_24h: Optional[float] = Field(
        None,
        description="24-hour trading volume in USD"
    )

    # Supply analysis
    circulating_supply: Optional[float] = Field(
        None,
        description="Circulating supply"
    )

    total_supply: Optional[float] = Field(
        None,
        description="Total supply"
    )

    max_supply: Optional[float] = Field(
        None,
        description="Maximum supply"
    )

    # Historical context
    ath: Optional[float] = Field(
        None,
        description="All-time high price"
    )

    ath_change_percentage: Optional[float] = Field(
        None,
        description="% change from all-time high"
    )

    ath_date: Optional[str] = Field(
        None,
        description="Date of all-time high"
    )

    atl: Optional[float] = Field(
        None,
        description="All-time low price"
    )

    atl_change_percentage: Optional[float] = Field(
        None,
        description="% change from all-time low"
    )

    atl_date: Optional[str] = Field(
        None,
        description="Date of all-time low"
    )

    # Additional metadata for detailed view
    last_updated: datetime = Field(
        ...,
        description="Last time asset data was updated"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "price_usd": 45000.50,
                "is_active": True,
                "availability_status": "Available",
                "symbol": "BTC",
                "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                "market_cap_rank": 1,
                "market_cap": 850000000000,
                "price_change_percentage_24h": 2.5,
                "price_change_percentage_7d": 8.2,
                "total_volume_24h": 25000000000,
                "high_24h": 46000.00,
                "low_24h": 44000.00,
                "circulating_supply": 19500000,
                "total_supply": 21000000,
                "ath": 69000.00,
                "ath_change_percentage": -34.8,
                "last_updated": "2025-07-09T10:30:00Z"
            }
        }
    )


class AssetListResponse(BaseModel):
    """Response model for asset list endpoint with metadata"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of available assets"
    )

    total_count: int = Field(
        ...,
        description="Total number of assets"
    )

    active_count: int = Field(
        ...,
        description="Number of active assets"
    )

    categories: list[str] = Field(
        ...,
        description="Available categories for filtering"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assets": [
                    {
                        "asset_id": "BTC",
                        "name": "Bitcoin",
                        "description": "Digital currency and store of value",
                        "category": "major",
                        "price_usd": 45000.50,
                        "is_active": True
                    },
                    {
                        "asset_id": "ETH",
                        "name": "Ethereum",
                        "description": "Decentralized platform for smart contracts",
                        "category": "major",
                        "price_usd": 3000.25,
                        "is_active": True
                    }
                ],
                "total_count": 12,
                "active_count": 10,
                "categories": ["major", "altcoin", "stablecoin"]
            }
        }


# Helper function to convert DAO Asset model to API response model
def asset_to_response(asset) -> AssetResponse:
    """Convert common.entities.inventory.Asset to AssetResponse with enhanced market data"""
    return AssetResponse(
        asset_id=asset.asset_id,
        name=asset.name,
        description=asset.description,
        category=asset.category,
        price_usd=asset.price_usd,
        is_active=asset.is_active,

        # Enhanced fields for frontend display
        symbol=getattr(asset, 'symbol', None),
        image=getattr(asset, 'image', None),
        market_cap_rank=getattr(asset, 'market_cap_rank', None),

        # Market metrics
        market_cap=getattr(asset, 'market_cap', None),
        price_change_percentage_24h=getattr(asset, 'price_change_percentage_24h', None),
        total_volume_24h=getattr(asset, 'total_volume_24h', None),

        # Price range
        high_24h=getattr(asset, 'high_24h', None),
        low_24h=getattr(asset, 'low_24h', None),

        # Supply information
        circulating_supply=getattr(asset, 'circulating_supply', None),

        # Additional context
        last_updated=getattr(asset, 'updated_at', None)
    )


def asset_to_detail_response(asset) -> AssetDetailResponse:
    """Convert common.entities.inventory.Asset to AssetDetailResponse with comprehensive market data"""
    # Determine availability status based on amount and active status
    if not asset.is_active:
        availability_status = "unavailable"
    elif asset.amount <= 0:
        availability_status = "out_of_stock"
    elif asset.amount < 10:  # Arbitrary threshold for "limited"
        availability_status = "limited"
    else:
        availability_status = "available"

    # Use current time if asset doesn't have updated_at field
    from datetime import datetime, timezone
    last_updated = getattr(asset, 'updated_at', datetime.now(timezone.utc))

    return AssetDetailResponse(
        asset_id=asset.asset_id,
        name=asset.name,
        description=asset.description,
        category=asset.category,
        price_usd=asset.price_usd,
        is_active=asset.is_active,
        availability_status=availability_status,

        # Enhanced fields for detailed view
        symbol=getattr(asset, 'symbol', None),
        image=getattr(asset, 'image', None),
        market_cap_rank=getattr(asset, 'market_cap_rank', None),

        # Comprehensive market data
        market_cap=getattr(asset, 'market_cap', None),
        price_change_24h=getattr(asset, 'price_change_24h', None),
        price_change_percentage_24h=getattr(asset, 'price_change_percentage_24h', None),
        price_change_percentage_7d=getattr(asset, 'price_change_percentage_7d', None),
        price_change_percentage_30d=getattr(asset, 'price_change_percentage_30d', None),

        # Price range analysis
        high_24h=getattr(asset, 'high_24h', None),
        low_24h=getattr(asset, 'low_24h', None),

        # Volume and trading metrics
        total_volume_24h=getattr(asset, 'total_volume_24h', None),

        # Supply analysis
        circulating_supply=getattr(asset, 'circulating_supply', None),
        total_supply=getattr(asset, 'total_supply', None),
        max_supply=getattr(asset, 'max_supply', None),

        # Historical context
        ath=getattr(asset, 'ath', None),
        ath_change_percentage=getattr(asset, 'ath_change_percentage', None),
        ath_date=getattr(asset, 'ath_date', None),
        atl=getattr(asset, 'atl', None),
        atl_change_percentage=getattr(asset, 'atl_change_percentage', None),
        atl_date=getattr(asset, 'atl_date', None),

        # Additional metadata
        last_updated=last_updated
    )