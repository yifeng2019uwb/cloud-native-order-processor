"""
Order update models for modifying existing orders.
Limited fields that can be updated after order creation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .enums import OrderStatus


class OrderUpdate(BaseModel):
    """Model for updating existing orders (limited fields)"""

    status: Optional[OrderStatus] = Field(
        None,
        description="Updated order status"
    )

    executed_quantity: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Updated executed quantity"
    )

    executed_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Updated execution price"
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="Order completion timestamp"
    )

    @field_validator("executed_quantity")
    @classmethod
    def validate_executed_quantity(cls, v):
        """Validate executed quantity is positive"""
        if v is not None and v <= 0:
            raise ValueError("Executed quantity must be greater than 0")
        return v

    @field_validator("executed_price")
    @classmethod
    def validate_executed_price(cls, v):
        """Validate executed price is positive"""
        if v is not None and v <= 0:
            raise ValueError("Executed price must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "executed_quantity": 0.5,
                "executed_price": 45000.00,
                "completed_at": "2025-07-30T10:35:00Z"
            }
        }