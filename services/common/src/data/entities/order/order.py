"""
Core order entity model.
Contains the main Order class and related models for database operations.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from .enums import OrderStatus, OrderType
from ..datetime_utils import safe_parse_datetime, get_current_utc
from ..entity_constants import OrderFields, AWSConfig, TableNames, DatabaseFields


class Order(BaseModel):
    """Order domain entity - pure business entity without database fields"""

    order_id: str = Field(..., description="Unique order identifier")
    username: str = Field(..., description="Username who placed the order")
    order_type: OrderType = Field(..., description="Type of order")
    status: OrderStatus = Field(..., description="Current order status")
    asset_id: str = Field(..., description="Asset symbol being traded")
    quantity: Decimal = Field(..., description="Amount of asset to trade")
    price: Decimal = Field(..., description="Price per unit in USD")
    total_amount: Decimal = Field(..., description="Total order value")
    created_at: datetime = Field(default_factory=get_current_utc, description="Order creation timestamp")
    updated_at: datetime = Field(default_factory=get_current_utc, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


# ==================== PYNAMODB MODEL ====================

class UserOrdersIndex(GlobalSecondaryIndex):
    """Global Secondary Index for user orders lookups"""

    class Meta:
        """Meta class for UserOrdersIndex"""
        index_name = "UserOrdersIndex"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    GSI_PK = UnicodeAttribute(hash_key=True, attr_name=DatabaseFields.GSI_PK)  # username
    GSI_SK = UnicodeAttribute(range_key=True, attr_name=DatabaseFields.GSI_SK)  # asset_id


class OrderItem(Model):
    """Order PynamoDB model - handles DynamoDB operations"""

    # ==================== METADATA ====================

    class Meta:
        """Meta class for OrderItem"""
        table_name = os.getenv('ORDERS_TABLE', TableNames.ORDERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # ==================== ATTRIBUTES ====================

    # Primary Key
    Pk = UnicodeAttribute(hash_key=True)
    Sk = UnicodeAttribute(range_key=True, default=OrderFields.SK_VALUE)

    # GSI for user orders
    GSI_PK = UnicodeAttribute(null=True, attr_name=DatabaseFields.GSI_PK)  # username
    GSI_SK = UnicodeAttribute(null=True, attr_name=DatabaseFields.GSI_SK)  # asset_id

    # Order fields
    order_id = UnicodeAttribute()
    username = UnicodeAttribute()
    order_type = UnicodeAttribute()
    status = UnicodeAttribute()
    asset_id = UnicodeAttribute()
    quantity = UnicodeAttribute()  # Store as string for Decimal precision
    price = UnicodeAttribute()     # Store as string for Decimal precision
    total_amount = UnicodeAttribute()  # Store as string for Decimal precision
    status_reason = UnicodeAttribute(null=True)

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    # Index
    user_orders_index = UserOrdersIndex()

    # ==================== CONVERSION ====================

    @classmethod
    def from_order(cls, order: Order) -> 'OrderItem':
        """Create OrderItem from Order domain model"""
        # Create PynamoDB model instance and set attributes explicitly
        order_item = cls()
        order_item.Pk = order.order_id
        order_item.Sk = OrderFields.SK_VALUE
        order_item.GSI_PK = order.username
        order_item.GSI_SK = order.asset_id
        order_item.order_id = order.order_id
        order_item.username = order.username
        order_item.order_type = order.order_type.value
        order_item.status = order.status.value
        order_item.asset_id = order.asset_id
        order_item.quantity = str(order.quantity)
        order_item.price = str(order.price)
        order_item.total_amount = str(order.total_amount)
        order_item.created_at = order.created_at
        order_item.updated_at = order.updated_at
        return order_item

    def to_order(self) -> Order:
        """Convert OrderItem to Order domain model"""
        return Order(
            order_id=self.order_id,
            username=self.username,
            order_type=OrderType(self.order_type),
            status=OrderStatus(self.status),
            asset_id=self.asset_id,
            quantity=Decimal(self.quantity),
            price=Decimal(self.price),
            total_amount=Decimal(self.total_amount),
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    # ==================== DATABASE OPERATIONS ====================

    def get_key(self) -> dict:
        """Get database key for this order item"""
        return {
            'Pk': self.Pk,
            'Sk': self.Sk
        }

    @staticmethod
    def get_key_for_order_id(order_id: str) -> dict:
        """Get database key for an order ID (static method)"""
        return {
            'Pk': order_id,
            'Sk': OrderFields.SK_VALUE
        }

    # ==================== LIFECYCLE ====================

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = get_current_utc()
        return super().save(condition=condition, **kwargs)
