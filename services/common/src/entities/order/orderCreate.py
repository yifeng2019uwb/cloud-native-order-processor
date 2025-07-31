"""
Order creation request model.
Handles validation for creating new orders.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re

from .enums import OrderType, OrderStatus
from .utils import OrderBusinessRules


class OrderCreate(BaseModel):
    """Request model for creating new orders"""

    order_type: OrderType = Field(
        ...,
        description="Type of order (market_buy, limit_sell, etc.)"
    )

    asset_id: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Asset symbol to trade"
    )

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Amount of asset to trade"
    )

    price_per_unit: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Price per unit (required for limit orders)"
    )

    limit_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Limit price for limit orders"
    )

    stop_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Stop price for stop orders"
    )

    currency: str = Field(
        default="USD",
        description="Order currency (default: USD)"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
    )

    @field_validator("asset_id")
    @classmethod
    def validate_asset_id(cls, v):
        """Validate asset ID format"""
        if not v or not v.strip():
            raise ValueError("Asset ID cannot be empty")

        v = v.strip().upper()

        # Asset ID should be 1-10 characters, alphanumeric
        if not re.match(r'^[A-Z0-9]{1,10}$', v):
            raise ValueError("Asset ID must be 1-10 uppercase letters and numbers")

        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("price_per_unit")
    @classmethod
    def validate_price_per_unit(cls, v):
        """Validate price is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("Price per unit must be greater than 0")
        return v

    @field_validator("limit_price")
    @classmethod
    def validate_limit_price(cls, v):
        """Validate limit price is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("Limit price must be greater than 0")
        return v

    @field_validator("stop_price")
    @classmethod
    def validate_stop_price(cls, v):
        """Validate stop price is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError("Stop price must be greater than 0")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        """Validate currency format"""
        if not v or not v.strip():
            raise ValueError("Currency cannot be empty")

        v = v.strip().upper()

        # Simple currency validation (3 letters)
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError("Currency must be 3 uppercase letters (e.g., USD)")

        return v

    @model_validator(mode="after")
    def validate_business_rules(self):
        """Validate all business rules using utility functions"""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=self.order_type,
            quantity=self.quantity,
            limit_price=self.limit_price,
            price_per_unit=self.price_per_unit,
            stop_price=self.stop_price,
            expires_at=self.expires_at,
            currency=self.currency
        )

        if errors:
            raise ValueError("; ".join(errors))

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "order_type": "market_buy",
                "asset_id": "BTC",
                "quantity": 0.5,
                "currency": "USD"
            }
        }