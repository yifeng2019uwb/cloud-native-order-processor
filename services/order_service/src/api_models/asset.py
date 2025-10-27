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
    asset_id: str
    transaction_type: AssetTransactionType
    quantity: Decimal
    price: Decimal
    status: AssetTransactionStatus
    timestamp: datetime

# ============================================================================
# RESPONSE MODELS
# ============================================================================
class GetAssetTransactionsResponse(BaseModel):
    """Response model for getting asset transactions"""

    data: List[AssetTransactionData]
    has_more: bool
