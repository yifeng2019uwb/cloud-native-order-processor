# services/common/src/database/__init__.py
from .dynamodb_connection import DynamoDBManager, get_dynamodb

__all__ = [
    "DynamoDBManager",
    "get_dynamodb"
]