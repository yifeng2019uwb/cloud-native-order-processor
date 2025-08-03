from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from boto3.dynamodb.conditions import Key, Attr

from ..exceptions import DatabaseOperationException
from ..exceptions.shared_exceptions import EntityNotFoundException


class BaseDAO(ABC):
    """Base Data Access Object with common DynamoDB operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def _safe_get_item(self, table, key: Dict[str, Any]) -> Dict[str, Any]:
        """Safely get item from DynamoDB table"""
        try:
            response = table.get_item(Key=key)
            item = response.get('Item')
            if not item:
                logging.warning(f"Item not found with key {key}")
                raise EntityNotFoundException(f"Item not found with key {key}")
            return item
        except EntityNotFoundException:
            raise
        except Exception as e:
            logging.error(f"Failed to get item with key {key}: {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving item with key {key}: {str(e)}")

    def _safe_put_item(self, table, item: Dict[str, Any]) -> Dict[str, Any]:
        """Safely put item to DynamoDB table"""
        try:
            response = table.put_item(Item=item)
            return item
        except Exception as e:
            logging.error(f"Failed to put item: {e}")
            raise DatabaseOperationException(f"Database operation failed while creating item: {str(e)}")

    def _safe_update_item(self, table, key: Dict[str, Any],
                         update_expression: str,
                         expression_values: Dict[str, Any],
                         expression_names: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Safely update item in DynamoDB table"""
        try:
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ReturnValues': 'ALL_NEW'
            }

            if expression_names:
                kwargs['ExpressionAttributeNames'] = expression_names

            response = table.update_item(**kwargs)
            attributes = response.get('Attributes')
            if not attributes:
                raise DatabaseOperationException(f"Failed to update item with key {key}: No attributes returned")
            return attributes
        except Exception as e:
            logging.error(f"Failed to update item with key {key}: {e}")
            raise DatabaseOperationException(f"Database operation failed while updating item with key {key}: {str(e)}")

    def _safe_delete_item(self, table, key: Dict[str, Any]) -> bool:
        """Safely delete item from DynamoDB table"""
        try:
            response = table.delete_item(Key=key, ReturnValues='ALL_OLD')
            return 'Attributes' in response
        except Exception as e:
            logging.error(f"Failed to delete item with key {key}: {e}")
            raise DatabaseOperationException(f"Database operation failed while deleting item with key {key}: {str(e)}")

    def _safe_query(self, table, key_condition, filter_condition=None,
                   index_name=None, limit=None) -> List[Dict[str, Any]]:
        """Safely query DynamoDB table"""
        try:
            kwargs = {
                'KeyConditionExpression': key_condition
            }

            if filter_condition:
                kwargs['FilterExpression'] = filter_condition
            if index_name:
                kwargs['IndexName'] = index_name
            if limit:
                kwargs['Limit'] = limit

            response = table.query(**kwargs)
            return response.get('Items', [])
        except Exception as e:
            logging.error(f"Failed to query table: {e}")
            raise DatabaseOperationException(f"Database operation failed while querying table: {str(e)}")