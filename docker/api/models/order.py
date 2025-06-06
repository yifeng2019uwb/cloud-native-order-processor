from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime

@dataclass
class Order:
    order_id: str
    customer_email: str
    customer_name: str
    items: List[Dict]
    total_amount: float
    status: str
    created_at: str
    updated_at: str = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self):
        return asdict(self)
    
    @property
    def item_count(self) -> int:
        return sum(item.get('quantity', 0) for item in self.items)
    
    def add_item(self, item_dict: Dict):
        """Add an item to the order"""
        self.items.append(item_dict)
        self._recalculate_total()
    
    def remove_item(self, product_id: str):
        """Remove an item from the order"""
        self.items = [item for item in self.items if item.get('product_id') != product_id]
        self._recalculate_total()
    
    def _recalculate_total(self):
        """Recalculate the total amount based on items"""
        self.total_amount = sum(
            item.get('quantity', 0) * item.get('price', 0) 
            for item in self.items
        )