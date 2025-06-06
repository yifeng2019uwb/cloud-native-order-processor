from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    price: float