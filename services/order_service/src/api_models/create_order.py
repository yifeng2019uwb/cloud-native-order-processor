"""
Pydantic models specific to create order API
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Import proper enums from common package
from common.data.entities.order.enums import OrderType

# Import centralized field validation functions
from validation.field_validators import (
    validate_asset_id, validate_quantity, validate_price
)

ASSET_ID_FIELD = "asset_id"
ORDER_TYPE_FIELD = "order_type"
QUANTITY_FIELD = "quantity"
PRICE_FIELD = "price"

# Import shared data models
from .shared.data_models import OrderData


class CreateOrderRequest(BaseModel):
    """Request model for POST /orders"""

    order_type: OrderType = Field(..., description="Type of order: market_buy, market_sell, limit_buy, limit_sell")
    asset_id: str = Field(..., description="Asset identifier (e.g., BTC, ETH)")
    quantity: Decimal = Field(..., gt=0, description="Quantity to trade")
    price: Optional[Decimal] = Field(None, gt=0, description="Price for limit orders, None for market orders")

    @field_validator(ASSET_ID_FIELD)
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)

    @field_validator(QUANTITY_FIELD)
    @classmethod
    def validate_quantity_format(cls, v: Decimal) -> Decimal:
        """Layer 1: Basic format validation for quantity"""
        return validate_quantity(v)

    @field_validator(PRICE_FIELD)
    @classmethod
    def validate_price_format(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Layer 1: Basic format validation for price"""
        if v is not None:
            return validate_price(v)
        return v

    @field_validator(ORDER_TYPE_FIELD)
    @classmethod
    def validate_order_type_format(cls, v: OrderType) -> OrderType:
        """Layer 1: Basic format validation for order_type"""
        # Pydantic already validates against enum
        return v


class CreateOrderResponse(BaseModel):
    """Response model for POST /orders"""

    data: OrderData
