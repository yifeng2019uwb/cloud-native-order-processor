"""
Order response models for API endpoints.
Safe models for external API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .enums import OrderType, OrderStatus


class OrderResponse(BaseModel):
    """Safe order model for API responses"""

    order_id: str = Field(
        ...,
        description="Unique order identifier"
    )

    user_id: str = Field(
        ...,
        description="User who placed the order"
    )

    order_type: OrderType = Field(
        ...,
        description="Type of order"
    )

    status: OrderStatus = Field(
        ...,
        description="Current order status"
    )

    asset_id: str = Field(
        ...,
        description="Asset symbol being traded"
    )

    quantity: Decimal = Field(
        ...,
        description="Amount of asset to trade"
    )

    price_per_unit: Optional[Decimal] = Field(
        None,
        description="Price per unit (None for market orders)"
    )

    limit_price: Optional[Decimal] = Field(
        None,
        description="Limit price for limit orders"
    )

    stop_price: Optional[Decimal] = Field(
        None,
        description="Stop price for stop orders"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value"
    )

    executed_quantity: Decimal = Field(
        ...,
        description="Amount of asset already executed"
    )

    executed_price: Optional[Decimal] = Field(
        None,
        description="Average execution price"
    )

    currency: str = Field(
        ...,
        description="Order currency"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="Order completion timestamp"
    )

    @property
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self.status == OrderStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.status in [OrderStatus.CANCELLED, OrderStatus.FAILED, OrderStatus.EXPIRED]

    @property
    def is_active(self) -> bool:
        """Check if order is still active"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.QUEUED, OrderStatus.TRIGGERED, OrderStatus.PROCESSING]

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity to execute"""
        return self.quantity - self.executed_quantity

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "order_id": "ord_123456789",
                "user_id": "user_123",
                "order_type": "market_buy",
                "status": "completed",
                "asset_id": "BTC",
                "quantity": 0.5,
                "total_amount": 22500.00,
                "executed_quantity": 0.5,
                "executed_price": 45000.00,
                "currency": "USD",
                "created_at": "2025-07-30T10:30:00Z",
                "updated_at": "2025-07-30T10:35:00Z",
                "completed_at": "2025-07-30T10:35:00Z"
            }
        }


class OrderListResponse(BaseModel):
    """Response model for order list endpoints"""

    orders: List[OrderResponse] = Field(
        ...,
        description="List of orders"
    )

    total_count: int = Field(
        ...,
        description="Total number of orders"
    )

    active_count: int = Field(
        ...,
        description="Number of active orders"
    )

    completed_count: int = Field(
        ...,
        description="Number of completed orders"
    )

    cancelled_count: int = Field(
        ...,
        description="Number of cancelled orders"
    )

    filters_applied: dict = Field(
        default_factory=dict,
        description="Filters applied to the query"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "orders": [
                    {
                        "order_id": "ord_123456789",
                        "user_id": "user_123",
                        "order_type": "market_buy",
                        "status": "completed",
                        "asset_id": "BTC",
                        "quantity": 0.5,
                        "total_amount": 22500.00,
                        "executed_quantity": 0.5,
                        "executed_price": 45000.00,
                        "currency": "USD",
                        "created_at": "2025-07-30T10:30:00Z",
                        "updated_at": "2025-07-30T10:35:00Z",
                        "completed_at": "2025-07-30T10:35:00Z"
                    }
                ],
                "total_count": 1,
                "active_count": 0,
                "completed_count": 1,
                "cancelled_count": 0,
                "filters_applied": {
                    "user_id": "user_123",
                    "status": "completed"
                }
            }
        }