"""
Portfolio Context Models - Data structures for LLM input
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List


class HoldingData(BaseModel):
    """User's asset holding with market data"""
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(..., ge=0, description="Quantity held")
    current_price: Decimal = Field(..., ge=0, description="Current price in USD")
    price_change_24h_pct: Decimal = Field(..., description="24h price change percentage")
    value_usd: Decimal = Field(..., ge=0, description="Total value in USD")
    allocation_pct: Decimal = Field(..., ge=0, le=100, description="Allocation percentage")


class OrderData(BaseModel):
    """Recent order summary"""
    order_type: str = Field(..., description="Order type (MARKET_BUY, etc.)")
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(..., ge=0, description="Order quantity")
    price: Decimal = Field(..., ge=0, description="Order price")
    created_at: datetime = Field(..., description="Order creation timestamp")


class PortfolioContext(BaseModel):
    """Aggregated data sent to LLM"""
    username: str = Field(..., description="Username")
    account_age_days: int = Field(..., ge=0, description="Account age in days")
    usd_balance: Decimal = Field(..., ge=0, description="USD balance")
    total_portfolio_value: Decimal = Field(..., ge=0, description="Total portfolio value")
    holdings: List[HoldingData] = Field(default_factory=list, description="Asset holdings")
    recent_orders: List[OrderData] = Field(default_factory=list, description="Recent orders")
