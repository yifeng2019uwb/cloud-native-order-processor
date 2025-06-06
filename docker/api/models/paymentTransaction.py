from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PaymentTransaction:
    transaction_id: str
    order_id: str
    amount: float
    status: str
    payment_method: str
    gateway_response: Dict
    created_at: str