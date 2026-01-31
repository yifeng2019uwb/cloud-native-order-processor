"""
Price data entity for Redis cache
Path: services/common/src/data/entities/price_data.py
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Price data entity for Redis storage"""

    asset_id: str = Field(..., description="Asset symbol (e.g., BTC, ETH)")
    price: Decimal = Field(..., description="Current price in USD")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Price update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON string for Redis storage"""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> 'PriceData':
        """Create PriceData from JSON string"""
        return cls.model_validate_json(json_str)

    @property
    def redis_key(self) -> str:
        """Get Redis key for this price data"""
        return f"price:{self.asset_id}"
