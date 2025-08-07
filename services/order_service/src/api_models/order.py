"""
Order Service API Models - Consolidated

Defines all request and response models for order service endpoints.
Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import proper enums from common package
from common.entities.order.enums import OrderType, OrderStatus

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_quantity, validate_price,
    validate_order_id, validate_order_type, validate_order_status,
    validate_limit, validate_offset
)

# Import custom exceptions
from common.exceptions import OrderValidationException


# ============================================================================
# REQUEST MODELS
# ============================================================================

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
                "price": None
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

    price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Price for limit orders, None for market orders"
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

    @field_validator('price')
    @classmethod
    def validate_price_format(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Layer 1: Basic format validation for price"""
        if v is not None:
            return validate_price(v)
        return v

    @field_validator('order_type')
    @classmethod
    def validate_order_type_format(cls, v: OrderType) -> OrderType:
        """Layer 1: Basic format validation for order_type"""
        # Pydantic already validates against enum, but we can add custom logic if needed
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

    @field_validator('order_type')
    @classmethod
    def validate_order_type_format(cls, v: Optional[OrderType]) -> Optional[OrderType]:
        """Layer 1: Basic format validation for order_type"""
        # Pydantic already validates against enum
        return v

    @field_validator('limit')
    @classmethod
    def validate_limit_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for limit"""
        return validate_limit(v)

    @field_validator('offset')
    @classmethod
    def validate_offset_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for offset"""
        return validate_offset(v)


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

    @field_validator('status')
    @classmethod
    def validate_status_format(cls, v: Optional[OrderStatus]) -> Optional[OrderStatus]:
        """Layer 1: Basic format validation for status"""
        # Pydantic already validates against enum
        return v

    @field_validator('limit')
    @classmethod
    def validate_limit_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for limit"""
        return validate_limit(v)

    @field_validator('offset')
    @classmethod
    def validate_offset_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for offset"""
        return validate_offset(v)


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

    @field_validator('limit')
    @classmethod
    def validate_limit_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for limit"""
        return validate_limit(v)

    @field_validator('offset')
    @classmethod
    def validate_offset_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for offset"""
        return validate_offset(v)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class OrderSummary(BaseModel):
    """
    Order summary model for list responses
    Contains essential fields for quick overview
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "price": 45000.00,
                "created_at": "2025-07-30T14:30:52Z"
            }
        }
    )

    order_id: str = Field(
        ...,
        description="Unique order identifier"
    )

    order_type: OrderType = Field(
        ...,
        description="Type of order"
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    quantity: Decimal = Field(
        ...,
        description="Quantity traded"
    )

    price: Optional[Decimal] = Field(
        None,
        description="Price for limit orders, None for market orders"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )


class OrderData(BaseModel):
    """
    Order data model for API responses
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "price": 45000.00,
                "created_at": "2025-07-30T14:30:52Z"
            }
        }
    )

    order_id: str = Field(
        ...,
        description="Unique order identifier"
    )

    order_type: OrderType = Field(
        ...,
        description="Type of order"
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    quantity: Decimal = Field(
        ...,
        description="Quantity traded"
    )

    price: Optional[Decimal] = Field(
        None,
        description="Price for limit orders, None for market orders"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )


class OrderCreateResponse(BaseModel):
    """
    Response model for order creation
    Simple response with order data and success status
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Order created successfully",
                "data": {
                    "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                    "order_type": "market_buy",
                    "asset_id": "BTC",
                    "quantity": 0.5,
                    "price": 45000.00,
                    "created_at": "2025-07-30T14:30:52Z"
                },
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )

    message: str = Field(
        ...,
        description="User-friendly message about the operation result"
    )

    data: OrderData = Field(
        ...,
        description="Order data for successful creation"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class GetOrderResponse(BaseModel):
    """
    Response model for getting a single order
    Simple response with order data and success status
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Order retrieved successfully",
                "data": {
                    "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                    "order_type": "market_buy",
                    "asset_id": "BTC",
                    "quantity": 0.5,
                    "price": 45000.00,
                    "created_at": "2025-07-30T14:30:52Z"
                },
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )

    message: str = Field(
        ...,
        description="User-friendly message about the operation result"
    )

    data: OrderData = Field(
        ...,
        description="Order data for successful retrieval"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class OrderListResponse(BaseModel):
    """
    Response model for order listing
    Simple response with list of order summaries and pagination info
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Orders retrieved successfully",
                "data": [
                    {
                        "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                        "order_type": "market_buy",
                        "asset_id": "BTC",
                        "quantity": 0.5,
                        "price": 45000.00,
                        "created_at": "2025-07-30T14:30:52Z"
                    }
                ],
                "has_more": False,
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )

    message: str = Field(
        ...,
        description="User-friendly message about the operation result"
    )

    data: List[OrderSummary] = Field(
        ...,
        description="List of order summaries"
    )

    has_more: bool = Field(
        ...,
        description="Whether there are more orders available"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class OrderCancelResponse(BaseModel):
    """
    Response model for order cancellation
    Simple response with success status
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Order cancelled successfully",
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )

    message: str = Field(
        ...,
        description="User-friendly message about the operation result"
    )

    order_id: str = Field(
        ...,
        description="Order identifier that was cancelled"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class OrderHistoryItem(BaseModel):
    """
    Individual order item in history response
    Simplified version with only necessary information
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "price": 45000.00,
                "status": "completed",
                "created_at": "2025-07-30T14:30:52Z"
            }
        }
    )

    order_id: str = Field(..., description="Unique order identifier")
    order_type: OrderType = Field(..., description="Type of order")
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(..., description="Order quantity")
    price: Optional[Decimal] = Field(None, description="Order price (for limit orders)")
    status: OrderStatus = Field(..., description="Current order status")
    created_at: datetime = Field(..., description="Order creation timestamp")


class OrderHistoryResponse(BaseModel):
    """
    Response model for order history
    Contains list of orders for the specified asset
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "orders": [
                    {
                        "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                        "order_type": "market_buy",
                        "asset_id": "BTC",
                        "quantity": 0.5,
                        "price": 45000.00,
                        "status": "completed",
                        "created_at": "2025-07-30T14:30:52Z"
                    }
                ],
                "total_count": 1,
                "limit": 50,
                "offset": 0
            }
        }
    )

    asset_id: str = Field(..., description="Asset identifier")
    orders: List[OrderHistoryItem] = Field(..., description="List of orders")
    total_count: int = Field(..., description="Total number of orders for this asset")
    limit: int = Field(..., description="Number of orders returned")
    offset: int = Field(..., description="Number of orders skipped")