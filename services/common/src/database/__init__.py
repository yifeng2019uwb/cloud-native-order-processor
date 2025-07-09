# services/common/database/__init__.py
from .dynamodb_service import DynamoDBManager, get_dynamodb
from .dynamodb_service import OrderService, InventoryService

__all__ = [
    "DynamoDBManager",
    "get_dynamodb"
]