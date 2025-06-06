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

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self):
        return asdict(self)
