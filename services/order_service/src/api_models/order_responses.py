"""
Order response models for the Order Service API
Path: services/order_service/src/api_models/order_responses.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Import proper enums from common package
from common.entities.order.enums import OrderType, OrderStatus


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
                "order_price": 2500.00,
                "total_amount": 22500.00,
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

    order_price: Optional[Decimal] = Field(
        None,
        description="Price for limit orders, None for market orders"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value"
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
                "order_price": 45000.00,
                "total_amount": 22500.00,
                "created_at": "2025-07-30T14:30:52Z",
                "expires_at": None
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

    order_price: Optional[Decimal] = Field(
        None,
        description="Price for limit orders, None for market orders"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )

    # Additional fields for limit orders only
    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
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
                    "order_price": 45000.00,
                    "total_amount": 22500.00,
                    "created_at": "2025-07-30T14:30:52Z",
                    "expires_at": None
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
                    "order_price": 45000.00,
                    "total_amount": 22500.00,
                    "created_at": "2025-07-30T14:30:52Z",
                    "expires_at": None
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
                        "order_price": 45000.00,
                        "total_amount": 22500.00,
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


class ErrorResponse(BaseModel):
    """
    Standard error response model
    Consistent error format across all endpoints
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Order not found",
                "error_code": "ORDER_NOT_FOUND",
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        default=False,
        description="Always false for error responses"
    )

    message: str = Field(
        ...,
        description="User-friendly error message"
    )

    error_code: str = Field(
        ...,
        description="Machine-readable error code"
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
                "order_price": 45000.00,
                "total_amount": 22500.00,
                "status": "completed",
                "created_at": "2025-07-30T14:30:52Z"
            }
        }
    )

    order_id: str = Field(..., description="Unique order identifier")
    order_type: OrderType = Field(..., description="Type of order")
    asset_id: str = Field(..., description="Asset identifier")
    quantity: Decimal = Field(..., description="Order quantity")
    order_price: Optional[Decimal] = Field(None, description="Order price (for limit orders)")
    total_amount: Decimal = Field(..., description="Total order value")
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
                        "order_price": 45000.00,
                        "total_amount": 22500.00,
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
