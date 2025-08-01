"""
Order creation request model.
Simple DB constraints only - validation handled by service layer.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .enums import OrderType, OrderStatus


class OrderCreate(BaseModel):
    """Request model for creating new orders with simple DB constraints only"""

    order_type: OrderType = Field(
        ...,
        description="Type of order (market_buy, limit_sell, etc.)"
    )

    asset_id: str = Field(
        ...,
        max_length=10,
        description="Asset symbol to trade"
    )

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Amount of asset to trade"
    )

    order_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Price for limit orders, None for market orders"
    )

    currency: str = Field(
        default="USD",
        max_length=3,
        description="Order currency (default: USD)"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "currency": "USD"
            }
        }