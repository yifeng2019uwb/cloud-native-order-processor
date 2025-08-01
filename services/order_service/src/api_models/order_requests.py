"""
Order Service API Request Models

Defines request models for order service endpoints.
Includes validation logic for order creation, retrieval, and listing.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

# Import custom exceptions
from exceptions import OrderValidationException


class OrderCreateRequest(BaseModel):
    """
    Request model for creating new orders
    Supports both market and limit orders
    """

    order_type: str = Field(
        ...,
        description="Type of order: market_buy, market_sell, limit_buy, limit_sell"
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Quantity to trade"
    )

    order_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Price for limit orders, None for market orders"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
    )

    @field_validator('order_type')
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        """Validate order type"""
        valid_types = ['market_buy', 'market_sell', 'limit_buy', 'limit_sell']
        if v not in valid_types:
            raise OrderValidationException(f"Invalid order_type. Must be one of: {valid_types}")
        return v

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v: str) -> str:
        """Validate asset ID"""
        if not v or not v.strip():
            raise OrderValidationException("Asset ID cannot be empty")
        return v.strip().upper()

    @field_validator('order_price')
    @classmethod
    def validate_order_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate order price based on order type"""
        order_type = info.data.get('order_type') if info.data else None

        if order_type in ['limit_buy', 'limit_sell']:
            if v is None:
                raise OrderValidationException(f"order_price is required for {order_type} orders")
        elif order_type in ['market_buy', 'market_sell']:
            if v is not None:
                raise OrderValidationException(f"order_price should not be specified for {order_type} orders")

        return v

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate expiration time"""
        if v is not None:
            if v <= datetime.utcnow():
                raise OrderValidationException("Expiration time must be in the future")
        return v

    @model_validator(mode='after')
    def validate_business_rules(self) -> 'OrderCreateRequest':
        """Additional business rule validations"""

        # Validate minimum order size
        if self.quantity < Decimal("0.001"):
            raise OrderValidationException("Order quantity below minimum threshold (0.001)")

        # Validate expiration time for limit orders
        if self.order_type in ['limit_buy', 'limit_sell']:
            if self.expires_at is None:
                raise OrderValidationException("expires_at is required for limit orders")

        return self

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5
            }
        }


class GetOrderRequest(BaseModel):
    """
    Request model for getting a single order by ID
    Simple path parameter model
    """

    order_id: str = Field(
        ...,
        description="Order ID to retrieve"
    )

    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Validate order ID format"""
        if not v or not v.strip():
            raise OrderValidationException("Order ID cannot be empty")
        return v.strip()

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6"
            }
        }


class OrderListRequest(BaseModel):
    """
    Request model for listing orders
    """

    status: Optional[str] = Field(
        None,
        description="Filter by order status"
    )

    asset_id: Optional[str] = Field(
        None,
        description="Filter by asset ID"
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of orders to return"
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Number of orders to skip"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status filter"""
        if v is not None:
            valid_statuses = ['pending', 'confirmed', 'processing', 'completed', 'cancelled', 'failed']
            if v not in valid_statuses:
                raise OrderValidationException(f"Invalid status. Must be one of: {valid_statuses}")
        return v

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate asset ID filter"""
        if v is not None and not v.strip():
            raise OrderValidationException("Asset ID cannot be empty")
        return v.strip().upper() if v else v

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "pending",
                "asset_id": "BTC",
                "limit": 20,
                "offset": 0
            }
        }
