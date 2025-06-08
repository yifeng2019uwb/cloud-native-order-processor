from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Product ID cannot be empty")
        return v


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderCreate(BaseModel):
    customer_email: EmailStr
    customer_name: str
    items: List[OrderItemCreate]
    shipping_address: Optional[Dict[str, Any]] = None

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Order must contain at least one item")
        return v

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Customer name cannot be empty")
        return v


class Order(BaseModel):
    order_id: str
    customer_id: str
    customer_email: str
    customer_name: str
    status: OrderStatus
    total_amount: Decimal
    currency: str = "USD"
    shipping_address: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    order_id: str
    customer_email: str
    customer_name: str
    status: OrderStatus
    total_amount: Decimal
    currency: str
    items: List[OrderItem]
    shipping_address: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
