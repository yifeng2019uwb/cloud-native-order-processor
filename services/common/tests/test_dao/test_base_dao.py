import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os
# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.database.dao.base_dao import BaseDAO


class TestBaseDAO:
    """Test BaseDAO common functionality"""

    class ConcreteDAO(BaseDAO):
        """Concrete implementation for testing"""
        def _get_entity_type(self) -> str:
            return "TEST"

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.orders_table = Mock()
        return mock_connection

    @pytest.fixture
    def base_dao(self, mock_db_connection):
        """Create concrete DAO instance for testing"""
        return self.ConcreteDAO(mock_db_connection)

    def test_get_timestamp(self, base_dao):
        """Test timestamp generation"""
        timestamp = base_dao._get_timestamp()

        # Should be ISO format
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_safe_get_item_success(self, base_dao, mock_db_connection):
        """Test successful item retrieval"""
        # Mock successful response
        expected_item = {"PK": "TEST#123", "SK": "METADATA", "data": "test"}
        mock_db_connection.orders_table.get_item.return_value = {"Item": expected_item}

        # Call method
        result = base_dao._safe_get_item(mock_db_connection.orders_table, {"PK": "TEST#123"})

        # Verify result
        assert result == expected_item
        mock_db_connection.orders_table.get_item.assert_called_once_with(Key={"PK": "TEST#123"})

    def test_safe_get_item_not_found(self, base_dao, mock_db_connection):
        """Test item not found"""
        # Mock no item response
        mock_db_connection.orders_table.get_item.return_value = {}

        # Call method
        result = base_dao._safe_get_item(mock_db_connection.orders_table, {"PK": "TEST#123"})

        # Should return None
        assert result is None

    def test_safe_put_item_success(self, base_dao, mock_db_connection):
        """Test successful item creation"""
        item = {"PK": "TEST#123", "SK": "METADATA", "data": "test"}
        mock_db_connection.orders_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Call method
        result = base_dao._safe_put_item(mock_db_connection.orders_table, item)

        # Should return the item
        assert result == item
        mock_db_connection.orders_table.put_item.assert_called_once_with(Item=item)

    def test_safe_update_item_success(self, base_dao, mock_db_connection):
        """Test successful item update"""
        key = {"PK": "TEST#123", "SK": "METADATA"}
        update_expression = "SET #name = :name"
        expression_values = {":name": "Updated Name"}
        expression_names = {"#name": "name"}

        updated_item = {"PK": "TEST#123", "SK": "METADATA", "name": "Updated Name"}
        mock_db_connection.orders_table.update_item.return_value = {"Attributes": updated_item}

        # Call method
        result = base_dao._safe_update_item(
            mock_db_connection.orders_table,
            key,
            update_expression,
            expression_values,
            expression_names
        )

        # Verify result
        assert result == updated_item
        mock_db_connection.orders_table.update_item.assert_called_once()

    def test_safe_delete_item_success(self, base_dao, mock_db_connection):
        """Test successful item deletion"""
        key = {"PK": "TEST#123", "SK": "METADATA"}
        mock_db_connection.orders_table.delete_item.return_value = {"Attributes": {"PK": "TEST#123"}}

        # Call method
        result = base_dao._safe_delete_item(mock_db_connection.orders_table, key)

        # Should return True
        assert result is True
        mock_db_connection.orders_table.delete_item.assert_called_once_with(Key=key, ReturnValues='ALL_OLD')

    def test_safe_delete_item_not_found(self, base_dao, mock_db_connection):
        """Test deleting non-existent item"""
        key = {"PK": "TEST#123", "SK": "METADATA"}
        mock_db_connection.orders_table.delete_item.return_value = {}

        # Call method
        result = base_dao._safe_delete_item(mock_db_connection.orders_table, key)

        # Should return False
        assert result is False

    def test_safe_query_success(self, base_dao, mock_db_connection):
        """Test successful query"""
        from boto3.dynamodb.conditions import Key

        key_condition = Key('PK').eq('TEST#123')
        items = [
            {"PK": "TEST#123", "SK": "ITEM#1"},
            {"PK": "TEST#123", "SK": "ITEM#2"}
        ]
        mock_db_connection.orders_table.query.return_value = {"Items": items}

        # Call method
        result = base_dao._safe_query(mock_db_connection.orders_table, key_condition)

        # Verify result
        assert result == items
        mock_db_connection.orders_table.query.assert_called_once()

    def test_build_update_expression_simple(self, base_dao):
        """Test building simple update expression"""
        updates = {"name": "New Name", "email": "new@example.com"}

        expression, values, names = base_dao._build_update_expression(updates)

        # Should have SET clause
        assert expression.startswith("SET ")
        assert "name = :name" in expression
        assert "email = :email" in expression
        assert "updated_at = :updated_at" in expression

        # Should have values
        assert values[":name"] == "New Name"
        assert values[":email"] == "new@example.com"
        assert ":updated_at" in values

        # Should not have names for non-reserved words
        assert names is None

    def test_build_update_expression_reserved_words(self, base_dao):
        """Test building update expression with reserved words"""
        updates = {"name": "New Name", "status": "active", "type": "user"}

        expression, values, names = base_dao._build_update_expression(updates)

        # Should handle reserved words
        assert "#name = :name" in expression
        assert "#status = :status" in expression
        assert "#type = :type" in expression

        # Should have expression names
        assert names is not None
        assert names["#name"] == "name"
        assert names["#status"] == "status"
        assert names["#type"] == "type"

    def test_build_update_expression_empty(self, base_dao):
        """Test building update expression with no updates"""
        with pytest.raises(ValueError) as exc_info:
            base_dao._build_update_expression({})

        assert "No updates provided" in str(exc_info.value)

    def test_validate_required_fields_success(self, base_dao):
        """Test required fields validation - success"""
        item = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required = ["field1", "field2"]

        # Should not raise
        base_dao._validate_required_fields(item, required)

    def test_validate_required_fields_missing(self, base_dao):
        """Test required fields validation - missing fields"""
        item = {"field1": "value1"}
        required = ["field1", "field2", "field3"]

        with pytest.raises(ValueError) as exc_info:
            base_dao._validate_required_fields(item, required)

        assert "Missing required fields" in str(exc_info.value)
        assert "field2" in str(exc_info.value)
        assert "field3" in str(exc_info.value)

    def test_validate_required_fields_empty_values(self, base_dao):
        """Test required fields validation - empty values"""
        item = {"field1": "", "field2": None, "field3": "value3"}
        required = ["field1", "field2", "field3"]

        with pytest.raises(ValueError) as exc_info:
            base_dao._validate_required_fields(item, required)

        assert "Missing required fields" in str(exc_info.value)
        assert "field1" in str(exc_info.value)
        assert "field2" in str(exc_info.value)

    def test_add_timestamps_create(self, base_dao):
        """Test adding timestamps for creation"""
        item = {"data": "test"}

        result = base_dao._add_timestamps(item, is_create=True)

        # Should add both timestamps
        assert "created_at" in result
        assert "updated_at" in result
        assert result["data"] == "test"

        # Timestamps should be ISO format
        datetime.fromisoformat(result["created_at"])
        datetime.fromisoformat(result["updated_at"])

    def test_add_timestamps_update(self, base_dao):
        """Test adding timestamps for update"""
        item = {"data": "test", "created_at": "2023-01-01T00:00:00"}

        result = base_dao._add_timestamps(item, is_create=False)

        # Should only update updated_at
        assert result["created_at"] == "2023-01-01T00:00:00"  # Unchanged
        assert "updated_at" in result
        assert result["data"] == "test"

        # updated_at should be ISO format
        datetime.fromisoformat(result["updated_at"])

    def test_create_primary_key(self, base_dao):
        """Test primary key creation"""
        entity_id = "user123"

        pk = base_dao._create_primary_key(entity_id)

        assert pk == "TEST#user123"

    def test_get_entity_type(self, base_dao):
        """Test entity type method"""
        assert base_dao._get_entity_type() == "TEST"

    def test_error_handling_get_item(self, base_dao, mock_db_connection):
        """Test error handling in safe_get_item"""
        # Mock exception
        mock_db_connection.orders_table.get_item.side_effect = Exception("DynamoDB error")

        with pytest.raises(Exception) as exc_info:
            base_dao._safe_get_item(mock_db_connection.orders_table, {"PK": "TEST#123"})

        assert "DynamoDB error" in str(exc_info.value)

    def test_error_handling_put_item(self, base_dao, mock_db_connection):
        """Test error handling in safe_put_item"""
        # Mock exception
        mock_db_connection.orders_table.put_item.side_effect = Exception("DynamoDB error")

        with pytest.raises(Exception) as exc_info:
            base_dao._safe_put_item(mock_db_connection.orders_table, {"PK": "TEST#123"})

        assert "DynamoDB error" in str(exc_info.value)

    def test_error_handling_update_item(self, base_dao, mock_db_connection):
        """Test error handling in safe_update_item"""
        # Mock exception
        mock_db_connection.orders_table.update_item.side_effect = Exception("DynamoDB error")

        with pytest.raises(Exception) as exc_info:
            base_dao._safe_update_item(
                mock_db_connection.orders_table,
                {"PK": "TEST#123"},
                "SET #name = :name",
                {":name": "test"}
            )

        assert "DynamoDB error" in str(exc_info.value)

    def test_safe_query_with_options(self, base_dao, mock_db_connection):
        """Test query with additional options"""
        from boto3.dynamodb.conditions import Key, Attr

        key_condition = Key('PK').eq('TEST#123')
        filter_condition = Attr('status').eq('active')

        items = [{"PK": "TEST#123", "SK": "ITEM#1", "status": "active"}]
        mock_db_connection.orders_table.query.return_value = {"Items": items}

        # Call with options
        result = base_dao._safe_query(
            mock_db_connection.orders_table,
            key_condition,
            filter_condition=filter_condition,
            index_name="StatusIndex",
            limit=10
        )

        # Verify result
        assert result == items

        # Verify call was made with options
        call_kwargs = mock_db_connection.orders_table.query.call_args[1]
        assert 'FilterExpression' in call_kwargs
        assert 'IndexName' in call_kwargs
        assert 'Limit' in call_kwargs
        assert call_kwargs['IndexName'] == "StatusIndex"
        assert call_kwargs['Limit'] == 10