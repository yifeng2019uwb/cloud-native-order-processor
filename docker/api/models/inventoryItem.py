from dataclasses import asdict
from datetime import datetime


class InventoryItem:
    product_id: str
    stock_quantity: int
    reserved_quantity: int
    min_stock_level: int = 10
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    @property
    def available_quantity(self) -> int:
        return max(0, self.stock_quantity - self.reserved_quantity)

    @property
    def is_low_stock(self) -> bool:
        return self.available_quantity <= self.min_stock_level

    @property
    def is_out_of_stock(self) -> bool:
        return self.available_quantity <= 0

    def to_dict(self):
        return asdict(self)
