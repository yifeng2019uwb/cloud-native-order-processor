"""
Order Service API Request Models

Defines request models for order service endpoints.
Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import proper enums from common package
from common.entities.order.enums import OrderType, OrderStatus

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_quantity, validate_price,
    validate_expires_at, validate_order_id
)

# Import custom exceptions
from exceptions import OrderValidationException


class OrderCreateRequest(BaseModel):
    """
    Request model for creating new orders
    Supports both market and limit orders

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "order_price": None,
                "expires_at": None
            }
        }
    )

    order_type: OrderType = Field(
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

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)

    @field_validator('quantity')
    @classmethod
    def validate_quantity_format(cls, v: Decimal) -> Decimal:
        """Layer 1: Basic format validation for quantity"""
        return validate_quantity(v)

    @field_validator('order_price')
    @classmethod
    def validate_price_format(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Layer 1: Basic format validation for price"""
        if v is not None:
            return validate_price(v)
        return v

    @field_validator('expires_at')
    @classmethod
    def validate_expires_at_format(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Layer 1: Basic format validation for expiration time"""
        if v is not None:
            return validate_expires_at(v)
        return v


class OrderCancelRequest(BaseModel):
    """
    Request model for cancelling orders
    Only limit orders can be cancelled by users

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6"
            }
        }
    )

    order_id: str = Field(
        ...,
        description="Order ID to cancel"
    )

    @field_validator('order_id')
    @classmethod
    def validate_order_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for order_id"""
        return validate_order_id(v)


class OrderFilterRequest(BaseModel):
    """
    Request model for filtering orders
    Simple filtering by asset_id and order_type

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "order_type": "market_buy",
                "limit": 50,
                "offset": 0
            }
        }
    )

    asset_id: Optional[str] = Field(
        None,
        description="Filter by asset ID"
    )

    order_type: Optional[OrderType] = Field(
        None,
        description="Filter by order type"
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

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for asset_id"""
        if v is not None:
            return validate_asset_id(v)
        return v


class GetOrderRequest(BaseModel):
    """
    Request model for getting a single order by ID
    Simple path parameter model

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6"
            }
        }
    )

    order_id: str = Field(
        ...,
        description="Order ID to retrieve"
    )

    @field_validator('order_id')
    @classmethod
    def validate_order_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for order_id"""
        return validate_order_id(v)


class OrderListRequest(BaseModel):
    """
    Request model for listing orders

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "pending",
                "asset_id": "BTC",
                "limit": 50,
                "offset": 0
            }
        }
    )

    status: Optional[OrderStatus] = Field(
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

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for asset_id"""
        if v is not None:
            return validate_asset_id(v)
        return v


class OrderHistoryRequest(BaseModel):
    """
    Request model for getting order history for a specific asset
    Simple API to list all orders for a specific asset

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "limit": 50,
                "offset": 0
            }
        }
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier to get history for (e.g., BTC, ETH)"
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

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)
