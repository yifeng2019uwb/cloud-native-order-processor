from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    price: float

    def to_dict(self):
        return asdict(self)
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.price