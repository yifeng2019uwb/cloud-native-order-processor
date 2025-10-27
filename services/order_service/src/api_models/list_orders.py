"""
Pydantic models specific to list orders API
"""
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# Import proper enums from common package
from common.data.entities.order.enums import OrderType

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_limit, validate_offset
)

ASSET_ID_FIELD = "asset_id"
ORDER_TYPE_FIELD = "order_type"
LIMIT_FIELD = "limit"
OFFSET_FIELD = "offset"

# Import shared data models
from .shared.data_models import OrderSummary


class ListOrdersRequest(BaseModel):
    """Request model for GET /orders"""

    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    order_type: Optional[OrderType] = Field(None, description="Filter by order type")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of orders to return")
    offset: int = Field(default=0, ge=0, description="Number of orders to skip")

    @field_validator(ASSET_ID_FIELD)
    @classmethod
    def validate_asset_id_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for asset_id"""
        if v is not None:
            return validate_asset_id(v)
        return v

    @field_validator(ORDER_TYPE_FIELD)
    @classmethod
    def validate_order_type_format(cls, v: Optional[OrderType]) -> Optional[OrderType]:
        """Layer 1: Basic format validation for order_type"""
        # Pydantic already validates against enum
        return v

    @field_validator(LIMIT_FIELD)
    @classmethod
    def validate_limit_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for limit"""
        return validate_limit(v)

    @field_validator(OFFSET_FIELD)
    @classmethod
    def validate_offset_format(cls, v: int) -> int:
        """Layer 1: Basic format validation for offset"""
        return validate_offset(v)


class ListOrdersResponse(BaseModel):
    """Response model for GET /orders"""

    data: List[OrderSummary]
    has_more: bool
