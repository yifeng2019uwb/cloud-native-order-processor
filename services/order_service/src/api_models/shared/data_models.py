"""
Shared data models for order service responses
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

# Import proper enums from common package
from common.data.entities.order.enums import OrderType, OrderStatus


class OrderSummary(BaseModel):
    """Order summary model for list responses"""

    order_id: str
    order_type: OrderType
    asset_id: str
    quantity: Decimal
    price: Optional[Decimal]
    created_at: datetime


class OrderData(BaseModel):
    """Order data model for detailed order responses"""

    order_id: str
    order_type: OrderType
    asset_id: str
    quantity: Decimal
    price: Optional[Decimal]
    status: OrderStatus
    total_amount: Optional[Decimal]
    created_at: datetime
