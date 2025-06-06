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
    
    def to_dict(self):
        return asdict(self)