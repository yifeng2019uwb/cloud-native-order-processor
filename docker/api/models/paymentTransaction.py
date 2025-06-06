from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict


@dataclass
class PaymentTransaction:
    transaction_id: str
    order_id: str
    amount: float
    status: str
    payment_method: str
    gateway_response: Dict
    created_at: str

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)
