from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("sku", "name", "category")
    @classmethod
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class Product(BaseModel):
    product_id: str
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    created_at: datetime
    updated_at: datetime

    @field_validator("product_id", "sku", "name", "category")
    @classmethod
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v
