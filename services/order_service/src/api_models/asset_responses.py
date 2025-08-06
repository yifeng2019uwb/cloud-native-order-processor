"""
Asset response models for the Order Service API
Path: services/order_service/src/api_models/asset_responses.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Import proper enums from common package
from common.entities.asset.enums import AssetTransactionType, AssetTransactionStatus


class AssetBalanceData(BaseModel):
    """
    Asset balance data model for API responses
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "quantity": 1.5,
                "created_at": "2025-07-30T14:30:52Z",
                "updated_at": "2025-07-30T15:45:30Z"
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