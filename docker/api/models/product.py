from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Product:
    product_id: str
    name: str
    description: str
    price: float
    category: str
    created_at: str = None
    updated_at: str = None