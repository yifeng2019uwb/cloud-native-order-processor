from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str


class Product(BaseModel):
    product_id: str
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    created_at: datetime
    updated_at: datetime
