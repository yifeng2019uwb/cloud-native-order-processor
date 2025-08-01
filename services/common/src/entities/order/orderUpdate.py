"""
Order update models for modifying existing orders.
Simple DB constraints only - validation handled by service layer.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .enums import OrderStatus


class OrderUpdate(BaseModel):
    """Model for updating existing orders with simple DB constraints only"""

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

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "executed_quantity": 0.5,
                "executed_price": 45000.00,
                "completed_at": "2025-07-30T10:35:00Z"
            }
        }