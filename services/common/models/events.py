from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    ORDER_STATUS_CHANGED = "order_status_changed"
    ORDER_CANCELLED = "order_cancelled"
    INVENTORY_UPDATED = "inventory_updated"
    INVENTORY_LOW_STOCK = "inventory_low_stock"
    PAYMENT_PROCESSED = "payment_processed"

class BaseEvent(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: datetime
    service_name: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class OrderEvent(BaseEvent):
    order_id: str
    customer_email: str

class InventoryEvent(BaseEvent):
    product_id: str
    warehouse_location: Optional[str] = None