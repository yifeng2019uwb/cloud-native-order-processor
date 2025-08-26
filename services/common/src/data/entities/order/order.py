"""
Core order entity model.
Contains the main Order class and related models for database operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal

from .enums import OrderType, OrderStatus


class Order(BaseModel):
    """Core order entity model for DynamoDB storage

    Database Schema:
    - PK: order_id (Primary Key)
    - SK: ORDER (Sort Key)
    - GSI: UserOrdersIndex (PK: username, SK: ASSET_ID)

    Query Patterns:
    - Get specific order: PK = order_id
    - Get user's all orders: GSI PK = username
    - Get user's asset orders: GSI PK = username, GSI SK = ASSET_ID
    """

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

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class OrderCreate(BaseModel):
    """Request model for creating new orders"""

    order_type: OrderType = Field(..., description="Type of order")
    asset_id: str = Field(..., description="Asset symbol to trade")
    quantity: Decimal = Field(..., gt=0, description="Amount of asset to trade")
    price: Decimal = Field(..., gt=0, description="Price per unit in USD")

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}


class OrderUpdate(BaseModel):
    """Model for updating existing orders"""

    status: Optional[OrderStatus] = Field(None, description="Updated order status")

    class Config:
        pass


class OrderResponse(BaseModel):
    """Safe order model for API responses"""

    order_id: str = Field(..., description="Unique order identifier")
    username: str = Field(..., description="Username who placed the order")
    order_type: OrderType = Field(..., description="Type of order")
    status: OrderStatus = Field(..., description="Current order status")
    asset_id: str = Field(..., description="Asset symbol being traded")
    quantity: Decimal = Field(..., description="Amount of asset to trade")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total order value")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
