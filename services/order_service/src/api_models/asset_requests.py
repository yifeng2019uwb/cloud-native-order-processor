"""
Asset Service API Request Models

Defines request models for asset balance and transaction endpoints.
Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_quantity, validate_price
)


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


class GetAssetTransactionsRequest(BaseModel):
    """
    Request model for getting asset transaction history
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
        description="Asset identifier (e.g., BTC, ETH)"
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of transactions to return"
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Number of transactions to skip"
    )

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)


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