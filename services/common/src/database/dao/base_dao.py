from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr


class BaseDAO(ABC):
    """Base Data Access Object with common DynamoDB patterns"""

    def __init__(self, db_connection):
        self.db = db_connection

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat()

    def _safe_get_item(self, table, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Safely get item from DynamoDB table"""
        try:
            response = table.get_item(Key=key)
            return response.get('Item')
        except Exception as e:
            logging.error(f"Failed to get item with key {key}: {e}")
            raise

    def _safe_put_item(self, table, item: Dict[str, Any]) -> Dict[str, Any]:
        """Safely put item to DynamoDB table"""
        try:
            response = table.put_item(Item=item)
            return item
        except Exception as e:
            logging.error(f"Failed to put item: {e}")
            raise

    def _safe_update_item(self, table, key: Dict[str, Any],
                         update_expression: str,
                         expression_values: Dict[str, Any],
                         expression_names: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
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
            return response.get('Attributes')
        except Exception as e:
            logging.error(f"Failed to update item with key {key}: {e}")
            raise

    def _build_update_expression(self, updates: Dict[str, Any]) -> tuple:
        """Build update expression from dict of field updates"""
        if not updates:
            raise ValueError("No updates provided")

        # Always add updated_at
        updates['updated_at'] = self._get_timestamp()

        set_clauses = []
        expression_values = {}
        expression_names = {}

        for field, value in updates.items():
            # Handle reserved keywords
            if field in ['name', 'status', 'type']:  # Common DynamoDB reserved words
                attr_name = f"#{field}"
                expression_names[attr_name] = field
                set_clauses.append(f"{attr_name} = :{field}")
            else:
                set_clauses.append(f"{field} = :{field}")

            expression_values[f":{field}"] = value

        update_expression = "SET " + ", ".join(set_clauses)

        return update_expression, expression_values, expression_names if expression_names else None

    def _validate_required_fields(self, item: Dict[str, Any], required_fields: List[str]):
        """Validate that required fields are present"""
        missing_fields = [field for field in required_fields if field not in item or not item[field]]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

    def _add_timestamps(self, item: Dict[str, Any], is_create: bool = True) -> Dict[str, Any]:
        """Add created_at and updated_at timestamps"""
        now = self._get_timestamp()

        if is_create:
            item['created_at'] = now
        item['updated_at'] = now

        return item

    @abstractmethod
    def _get_entity_type(self) -> str:
        """Return the entity type for this DAO (e.g., 'USER', 'ORDER')"""
        pass

    def _create_primary_key(self, entity_id: str) -> str:
        """Create primary key for entity"""
        return f"{self._get_entity_type()}#{entity_id}"