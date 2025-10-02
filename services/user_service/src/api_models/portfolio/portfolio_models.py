"""
Portfolio API Models

Defines request and response models for portfolio endpoints.
Combines both request and response models in a single file for better organization.

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Portfolio models don't require field validation as they use simple data types


# ============================================================================
# REQUEST MODELS
# ============================================================================

class GetPortfolioRequest(BaseModel):
    """
    Request model for getting user portfolio
    No parameters needed - uses authenticated user
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {}
        }
    )


class GetAssetBalanceRequest(BaseModel):
    """
    Request model for getting single asset balance
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC"
            }
        }
    )

    asset_id: str = Field(
        ...,
        min_length=3,
        description="Asset identifier (e.g., BTC, ETH)"
    )


class GetAssetBalancesRequest(BaseModel):
    """
    Request model for getting all asset balances
    No parameters needed - uses authenticated user
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {}
        }
    )


# ============================================================================
# DATA MODELS
# ============================================================================

class AssetBalanceData(BaseModel):
    """
    Asset balance data model for API responses
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "asset_name": "Bitcoin",
                "quantity": 1.5,
                "current_price": 45000.50,
                "total_value": 67507.50,
                "created_at": "2025-01-10T14:30:52Z",
                "updated_at": "2025-01-10T15:45:30Z"
            }
        }
    )

    asset_id: str = Field(
        ...,
        min_length=3,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    asset_name: str = Field(
        ...,
        min_length=1,
        description="Asset display name (e.g., Bitcoin, Ethereum)"
    )

    quantity: Decimal = Field(
        ...,
        ge=0,
        description="Current balance quantity"
    )

    current_price: float = Field(
        ...,
        ge=0,
        description="Current market price in USD"
    )

    total_value: float = Field(
        ...,
        ge=0,
        description="Total value of this asset balance (quantity * current_price)"
    )

    created_at: datetime = Field(
        ...,
        description="Balance creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Balance last update timestamp"
    )


class PortfolioAssetData(BaseModel):
    """
    Portfolio asset data model for API responses
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "quantity": 1.5,
                "current_price": 45000.50,
                "market_value": 67507.50,
                "percentage": 25.5
            }
        }
    )

    asset_id: str = Field(
        ...,
        min_length=3,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    quantity: Decimal = Field(
        ...,
        ge=0,
        description="Current balance quantity"
    )

    current_price: Decimal = Field(
        ...,
        ge=0,
        description="Current market price in USD"
    )

    market_value: Decimal = Field(
        ...,
        ge=0,
        description="Total market value of this asset (quantity * current_price)"
    )

    percentage: Decimal = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of total portfolio value"
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class GetPortfolioResponse(BaseModel):
    """
    Response model for portfolio data
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Portfolio retrieved successfully",
                "data": {
                    "username": "john_doe",
                    "usd_balance": 10000.00,
                    "total_asset_value": 67507.50,
                    "total_portfolio_value": 77507.50,
                    "asset_count": 2,
                    "assets": [
                        {
                            "asset_id": "BTC",
                            "quantity": 1.5,
                            "current_price": 45000.50,
                            "market_value": 67507.50,
                            "percentage": 87.1
                        },
                        {
                            "asset_id": "ETH",
                            "quantity": 10.0,
                            "current_price": 3000.00,
                            "market_value": 30000.00,
                            "percentage": 38.7
                        }
                    ]
                },
                "timestamp": "2025-01-10T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Indicates if the request was successful"
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable message describing the result"
    )

    data: dict = Field(
        ...,
        description="Portfolio data containing user balances and asset information"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class GetAssetBalanceResponse(BaseModel):
    """
    Response model for single asset balance data
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Asset balance retrieved successfully",
                "data": {
                    "asset_id": "BTC",
                    "asset_name": "Bitcoin",
                    "quantity": 1.5,
                    "current_price": 45000.50,
                    "total_value": 67507.50,
                    "created_at": "2025-01-10T14:30:52Z",
                    "updated_at": "2025-01-10T15:45:30Z"
                },
                "timestamp": "2025-01-10T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        ...,
        description="Indicates if the request was successful"
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable message describing the result"
    )

    data: AssetBalanceData = Field(
        ...,
        description="Asset balance data"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )