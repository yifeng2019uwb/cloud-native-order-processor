"""
Order response models for the Order Service API
Path: services/order_service/src/api_models/order_responses.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class OrderSummary(BaseModel):
    """
    Order summary model for list responses
    Contains essential fields for quick overview
    """

    order_id: str = Field(
        ...,
        description="Unique order identifier"
    )

    status: str = Field(
        ...,
        description="Current order status: completed, pending, failed"
    )

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
        description="Quantity traded"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "status": "completed",
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "total_amount": 22500.00,
                "created_at": "2025-07-30T14:30:52Z"
            }
        }


class OrderData(BaseModel):
    """
    Order data model for API responses
    Contains only necessary fields for client consumption
    """

    order_id: str = Field(
        ...,
        description="Unique order identifier"
    )

    status: str = Field(
        ...,
        description="Current order status: completed, pending, failed"
    )

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
        description="Quantity traded"
    )

    order_price: Optional[Decimal] = Field(
        None,
        description="Order price (actual execution price for market orders, requested price for limit orders)"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value (market_price * quantity for market orders, order_price * quantity for limit orders)"
    )

    created_at: datetime = Field(
        ...,
        description="Order creation timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                "status": "completed",
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "order_price": 45000.00,
                "total_amount": 22500.00,
                "created_at": "2025-07-30T14:30:52Z"
            }
        }


class OrderCreateResponse(BaseModel):
    """
    Response model for order creation
    Simple response with order data and success status
    """

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

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Order created successfully",
                "data": {
                    "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                    "status": "completed",
                    "order_type": "market_buy",
                    "asset_id": "BTC",
                    "quantity": 0.5,
                    "order_price": 45000.00,
                    "total_amount": 22500.00,
                    "created_at": "2025-07-30T14:30:52Z"
                },
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }


class GetOrderResponse(BaseModel):
    """
    Response model for getting a single order
    Simple response with order data and success status
    """

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

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Order retrieved successfully",
                "data": {
                    "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                    "status": "completed",
                    "order_type": "market_buy",
                    "asset_id": "BTC",
                    "quantity": 0.5,
                    "order_price": 45000.00,
                    "total_amount": 22500.00,
                    "created_at": "2025-07-30T14:30:52Z"
                },
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }


class OrderListResponse(BaseModel):
    """
    Response model for order listing
    Simple response with list of order summaries and pagination info
    """

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )

    message: str = Field(
        ...,
        description="User-friendly message about the operation result"
    )

    data: list[OrderSummary] = Field(
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

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Orders retrieved successfully",
                "data": [
                    {
                        "order_id": "ord_20250730_143052_a1b2c3d4e5f6",
                        "status": "completed",
                        "order_type": "market_buy",
                        "asset_id": "BTC",
                        "quantity": 0.5,
                        "total_amount": 22500.00,
                        "created_at": "2025-07-30T14:30:52Z"
                    }
                ],
                "has_more": False,
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
