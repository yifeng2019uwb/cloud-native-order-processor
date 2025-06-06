from dataclasses import dataclass, asdict
from typing import Dict
from datetime import datetime


@dataclass
class Customer:
    customer_id: str
    email: str
    name: str
    phone: str = None
    address: Dict = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.address is None:
            self.address = {}

    def to_dict(self):
        return asdict(self)
