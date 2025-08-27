"""
Asset Service API Models

Defines request and response models for asset balance and transaction endpoints.
Combines both request and response models in a single file for better organization.

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_quantity, validate_price
)

# Import proper enums from common package
from common.data.entities.asset.enums import AssetTransactionType, AssetTransactionStatus


# ============================================================================
# REQUEST MODELS
# ============================================================================

class GetAssetBalanceRequest(BaseModel):
    """
    Request model for getting asset balance
    Simple path parameter model
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
        description="Asset identifier (e.g., BTC, ETH)"
    )

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)


class GetAssetBalancesRequest(BaseModel):
    """
    Request model for getting all asset balances for a user
    No parameters needed - uses authenticated user
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {}
        }
    )


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
                "created_at": "2025-07-30T14:30:52Z",
                "updated_at": "2025-07-30T15:45:30Z"
            }
        }
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    asset_name: str = Field(
        ...,
        description="Asset display name (e.g., Bitcoin, Litecoin)"
    )

    quantity: Decimal = Field(
        ...,
        description="Current balance quantity"
    )

    current_price: float = Field(
        ...,
        description="Current market price in USD"
    )

    total_value: float = Field(
        ...,
        description="Total value of this asset balance (quantity * current_price)"
    )

    created_at: datetime = Field(
        ...,
        description="Balance creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )


class AssetTransactionData(BaseModel):
    """
    Asset transaction data model for API responses
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "transaction_type": "buy",
                "quantity": 0.5,
                "price": 45000.00,
                "status": "completed",
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    transaction_type: AssetTransactionType = Field(
        ...,
        description="Type of transaction (buy/sell)"
    )

    quantity: Decimal = Field(
        ...,
        description="Transaction quantity"
    )

    price: Decimal = Field(
        ...,
        description="Transaction price per unit"
    )

    status: AssetTransactionStatus = Field(
        ...,
        description="Transaction status"
    )

    timestamp: datetime = Field(
        ...,
        description="Transaction timestamp"
    )


class PortfolioAssetData(BaseModel):
    """
    Portfolio asset data with calculated market value
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "quantity": 1.5,
                "current_price": 45000.00,
                "market_value": 67500.00,
                "percentage": 75.0
            }
        }
    )

    asset_id: str = Field(
        ...,
        description="Asset identifier (e.g., BTC, ETH)"
    )

    quantity: Decimal = Field(
        ...,
        description="Current balance quantity"
    )

    current_price: Optional[Decimal] = Field(
        None,
        description="Current market price (if available)"
    )

    market_value: Optional[Decimal] = Field(
        None,
        description="Calculated market value (if price available)"
    )

    percentage: Optional[Decimal] = Field(
        None,
        description="Percentage of total portfolio (if calculated)"
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class GetAssetBalanceResponse(BaseModel):
    """
    Response model for getting asset balance
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Asset balance retrieved successfully",
                "data": {
                    "asset_id": "BTC",
                    "quantity": 1.5,
                    "created_at": "2025-07-30T14:30:52Z",
                    "updated_at": "2025-07-30T15:45:30Z"
                },
                "timestamp": "2025-07-30T15:45:30Z"
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

    data: AssetBalanceData = Field(
        ...,
        description="Asset balance data"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class GetAssetBalancesResponse(BaseModel):
    """
    Response model for getting all asset balances
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Asset balances retrieved successfully",
                "data": [
                    {
                        "asset_id": "BTC",
                        "quantity": 1.5,
                        "created_at": "2025-07-30T14:30:52Z",
                        "updated_at": "2025-07-30T15:45:30Z"
                    }
                ],
                "timestamp": "2025-07-30T15:45:30Z"
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

    data: List[AssetBalanceData] = Field(
        ...,
        description="List of asset balances"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class GetAssetTransactionsResponse(BaseModel):
    """
    Response model for getting asset transactions
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Asset transactions retrieved successfully",
                "data": [
                    {
                        "asset_id": "BTC",
                        "transaction_type": "buy",
                        "quantity": 0.5,
                        "price": 45000.00,
                        "status": "completed",
                        "timestamp": "2025-07-30T14:30:52Z"
                    }
                ],
                "has_more": False,
                "timestamp": "2025-07-30T15:45:30Z"
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

    data: List[AssetTransactionData] = Field(
        ...,
        description="List of asset transactions"
    )

    has_more: bool = Field(
        ...,
        description="Whether there are more transactions available"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )


class GetPortfolioResponse(BaseModel):
    """
    Response model for getting user portfolio
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Portfolio retrieved successfully",
                "data": {
                    "total_value": 67500.00,
                    "assets": [
                        {
                            "asset_id": "BTC",
                            "quantity": 1.5,
                            "current_price": 45000.00,
                            "market_value": 67500.00,
                            "percentage": 100.0
                        }
                    ]
                },
                "timestamp": "2025-07-30T15:45:30Z"
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

    data: dict = Field(
        ...,
        description="Portfolio data with total value and assets"
    )

    timestamp: datetime = Field(
        ...,
        description="Response timestamp"
    )