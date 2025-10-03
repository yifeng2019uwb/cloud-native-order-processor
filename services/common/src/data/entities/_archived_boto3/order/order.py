"""
Core order entity model.
Contains the main Order class and related models for database operations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal

from .enums import OrderType, OrderStatus


class Order(BaseModel):
    """Order domain entity - pure business entity without database fields"""

    order_id: str = Field(..., description="Unique order identifier")
    username: str = Field(..., description="Username who placed the order")
    order_type: OrderType = Field(..., description="Type of order")
    status: OrderStatus = Field(..., description="Current order status")
    asset_id: str = Field(..., description="Asset symbol being traded")
    quantity: Decimal = Field(..., description="Amount of asset to trade")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total order value")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Order creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


class OrderItem(BaseModel):
    """Order database item - includes DynamoDB-specific fields"""

    Pk: str = Field(..., description="Primary Key - order_id")
    Sk: str = Field(..., description="Sort Key - ORDER")
    order_id: str = Field(..., description="Unique order identifier")
    username: str = Field(..., description="Username who placed the order")
    order_type: OrderType = Field(..., description="Type of order")
    status: OrderStatus = Field(..., description="Current order status")
    asset_id: str = Field(..., description="Asset symbol being traded")
    quantity: Decimal = Field(..., description="Amount of asset to trade")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total order value")
    created_at: str = Field(..., description="Order creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")

    @classmethod
    def from_entity(cls, order: Order) -> OrderItem:
        """Convert Order entity to OrderItem for database storage"""
        return cls(
            Pk=order.order_id,
            Sk="ORDER",
            order_id=order.order_id,
            username=order.username,
            order_type=order.order_type,
            status=order.status,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )

    def to_entity(self) -> Order:
        """Convert OrderItem to Order entity"""
        return Order(
            order_id=self.order_id,
            username=self.username,
            order_type=self.order_type,
            status=self.status,
            asset_id=self.asset_id,
            quantity=self.quantity,
            price=self.price,
            total_amount=self.total_amount,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow(),
            updated_at=datetime.fromisoformat(self.updated_at.replace('Z', '+00:00')) if self.updated_at else datetime.utcnow()
        )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )
