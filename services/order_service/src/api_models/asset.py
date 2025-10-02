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
# DATA MODELS
# ============================================================================

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

# ============================================================================
# RESPONSE MODELS
# ============================================================================
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
