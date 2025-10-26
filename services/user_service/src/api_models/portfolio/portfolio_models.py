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
from pydantic import BaseModel, Field

# Portfolio models don't require field validation as they use simple data types


# ============================================================================
# REQUEST MODELS
# ============================================================================

class GetPortfolioRequest(BaseModel):
    """Request model for getting user portfolio"""
    pass


class GetAssetBalanceRequest(BaseModel):
    """Request model for getting single asset balance"""
    asset_id: str = Field(..., min_length=3, description="Asset identifier")


class GetAssetBalancesRequest(BaseModel):
    """Request model for getting all asset balances"""
    pass


# ============================================================================
# DATA MODELS
# ============================================================================

class PortfolioAssetData(BaseModel):
    """Portfolio asset data model for API responses"""
    asset_id: str = Field(..., min_length=3, description="Asset identifier")
    quantity: Decimal = Field(..., ge=0, description="Current balance quantity")
    current_price: Decimal = Field(..., ge=0, description="Current market price in USD")
    market_value: Decimal = Field(..., ge=0, description="Total market value of this asset")
    percentage: Decimal = Field(..., ge=0, le=100, description="Percentage of total portfolio value")


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class GetPortfolioResponse(BaseModel):
    """Response model for portfolio data"""
    assets: List[PortfolioAssetData]


class GetAssetBalanceResponse(BaseModel):
    """Response model for single asset balance data"""
    asset_id: str
    asset_name: str
    quantity: Decimal
    current_price: float
    total_value: float
    created_at: datetime
    updated_at: datetime