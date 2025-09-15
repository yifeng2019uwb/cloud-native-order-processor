"""
Simple asset response models for inventory service API
Only 2 APIs, so keep it simple!
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class AssetResponse(BaseModel):
    """Simple asset model for both list and detail APIs"""
    asset_id: str = Field(..., description="Asset symbol/identifier")
    name: str = Field(..., description="Asset display name")
    description: Optional[str] = Field(None, description="Asset description")
    category: str = Field(..., description="Asset category")
    price_usd: float = Field(..., description="Current USD price")
    is_active: bool = Field(..., description="Whether asset is available")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    image: Optional[str] = Field(None, description="Asset image URL")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change %")


class AssetListResponse(BaseModel):
    """Simple response for asset list API"""
    assets: List[AssetResponse] = Field(..., description="List of assets")
    total_count: int = Field(..., description="Total number of assets")
    active_count: int = Field(..., description="Number of active assets")
    filters: dict = Field(..., description="Applied filters")


class AssetDetailResponse(BaseModel):
    """Detailed response for asset detail API with comprehensive market data"""
    asset_id: str = Field(..., description="Asset symbol/identifier")
    name: str = Field(..., description="Asset display name")
    description: Optional[str] = Field(None, description="Asset description")
    category: str = Field(..., description="Asset category")
    price_usd: float = Field(..., description="Current USD price")
    is_active: bool = Field(..., description="Whether asset is available")
    availability_status: str = Field(..., description="Current availability status")

    # Enhanced fields for detailed view
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    image: Optional[str] = Field(None, description="URL to coin logo")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")

    # Comprehensive market data
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    price_change_24h: Optional[float] = Field(None, description="Price change in last 24h (USD)")
    price_change_percentage_24h: Optional[float] = Field(None, description="Price change percentage in last 24h")
    price_change_percentage_7d: Optional[float] = Field(None, description="Price change percentage in last 7 days")
    price_change_percentage_30d: Optional[float] = Field(None, description="Price change percentage in last 30 days")

    # Price range analysis
    high_24h: Optional[float] = Field(None, description="24-hour high price")
    low_24h: Optional[float] = Field(None, description="24-hour low price")

    # Volume and trading metrics
    total_volume_24h: Optional[float] = Field(None, description="Total trading volume in last 24h")

    # Supply analysis
    circulating_supply: Optional[float] = Field(None, description="Circulating supply")
    total_supply: Optional[float] = Field(None, description="Total supply")
    max_supply: Optional[float] = Field(None, description="Maximum supply")

    # Historical context
    ath: Optional[float] = Field(None, description="All-time high price")
    ath_change_percentage: Optional[float] = Field(None, description="% change from all-time high")
    ath_date: Optional[str] = Field(None, description="Date of all-time high")
    atl: Optional[float] = Field(None, description="All-time low price")
    atl_change_percentage: Optional[float] = Field(None, description="% change from all-time low")
    atl_date: Optional[str] = Field(None, description="Date of all-time low")

    # Additional metadata
    last_updated: Optional[str] = Field(None, description="Last update timestamp")