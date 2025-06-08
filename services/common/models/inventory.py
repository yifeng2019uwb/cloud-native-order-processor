from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventoryUpdate(BaseModel):
    quantity_change: int
    reason: Optional[str] = None


class InventoryItem(BaseModel):
    product_id: str
    stock_quantity: int
    reserved_quantity: int
    min_stock_level: int
    warehouse_location: Optional[str] = None
    last_restocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @property
    def available_quantity(self) -> int:
        return max(0, self.stock_quantity - self.reserved_quantity)

    @property
    def is_low_stock(self) -> bool:
        return self.available_quantity <= self.min_stock_level

    @property
    def is_out_of_stock(self) -> bool:
        return self.available_quantity <= 0
