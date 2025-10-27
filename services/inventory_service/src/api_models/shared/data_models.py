"""
Shared data models for inventory service responses
"""
from typing import Optional
from pydantic import BaseModel


class AssetData(BaseModel):
    """Simple asset model for list responses"""

    asset_id: str
    name: str
    description: Optional[str]
    category: str
    price_usd: float
    is_active: bool
    symbol: Optional[str]
    image: Optional[str]
    market_cap_rank: Optional[int]
    price_change_percentage_24h: Optional[float]


class AssetDetailData(BaseModel):
    """Detailed asset model for detail responses"""

    asset_id: str
    name: str
    description: Optional[str]
    category: str
    price_usd: float
    is_active: bool
    availability_status: str

    symbol: Optional[str]
    image: Optional[str]
    market_cap_rank: Optional[int]

    market_cap: Optional[float]
    price_change_24h: Optional[float]
    price_change_percentage_24h: Optional[float]
    price_change_percentage_7d: Optional[float]
    price_change_percentage_30d: Optional[float]

    high_24h: Optional[float]
    low_24h: Optional[float]

    total_volume_24h: Optional[float]

    circulating_supply: Optional[float]
    total_supply: Optional[float]
    max_supply: Optional[float]

    ath: Optional[float]
    ath_change_percentage: Optional[float]
    ath_date: Optional[str]
    atl: Optional[float]
    atl_change_percentage: Optional[float]
    atl_date: Optional[str]

    last_updated: Optional[str]
