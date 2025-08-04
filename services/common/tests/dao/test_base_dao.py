import pytest
from unittest.mock import Mock
import sys
import os

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.dao.base_dao import BaseDAO
from src.exceptions.shared_exceptions import EntityNotFoundException
from src.exceptions.exceptions import DatabaseOperationException


class TestBaseDAO:
    """Test BaseDAO safe DynamoDB operations"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.users_table = Mock()
        return mock_connection

    @pytest.fixture
    def base_dao(self, mock_db_connection):
        """Create BaseDAO instance for testing"""
        return BaseDAO(mock_db_connection)

    def test_safe_get_item_success(self, base_dao, mock_db_connection):
        """Test successful item retrieval"""
        # Mock successful response
        expected_item = {"PK": "test_user", "SK": "PROFILE", "name": "Test User"}
        mock_db_connection.users_table.get_item.return_value = {"Item": expected_item}

        # Call method
        result = base_dao._safe_get_item(mock_db_connection.users_table, {"PK": "test_user", "SK": "PROFILE"})

        # Verify result
        assert result == expected_item
        mock_db_connection.users_table.get_item.assert_called_once_with(Key={"PK": "test_user", "SK": "PROFILE"})

    def test_safe_get_item_not_found(self, base_dao, mock_db_connection):
        """Test _safe_get_item when item not found"""
        # Mock empty response
        mock_db_connection.test_table.get_item.return_value = {}

        # Should return None when item not found
        result = base_dao._safe_get_item(mock_db_connection.test_table, {'PK': 'nonexistent', 'SK': 'PROFILE'})
        assert result is None

    def test_safe_get_item_exception(self, base_dao, mock_db_connection):
        """Test exception handling in safe_get_item"""
        # Mock exception
        mock_db_connection.users_table.get_item.side_effect = Exception("DynamoDB error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            base_dao._safe_get_item(mock_db_connection.users_table, {"PK": "test_user"})

        assert "DynamoDB error" in str(exc_info.value)

    def test_safe_put_item_success(self, base_dao, mock_db_connection):
        """Test successful item creation"""
        item = {"PK": "test_user", "SK": "PROFILE", "name": "Test User"}
        mock_db_connection.users_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Call method
        result = base_dao._safe_put_item(mock_db_connection.users_table, item)

        # Should return the item
        assert result == item
        mock_db_connection.users_table.put_item.assert_called_once_with(Item=item)

    def test_safe_put_item_exception(self, base_dao, mock_db_connection):
        """Test exception handling in safe_put_item"""
        # Mock exception
        mock_db_connection.users_table.put_item.side_effect = Exception("DynamoDB error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            base_dao._safe_put_item(mock_db_connection.users_table, {"PK": "test"})

        assert "DynamoDB error" in str(exc_info.value)

    def test_safe_update_item_success(self, base_dao, mock_db_connection):
        """Test successful item update"""
        key = {"PK": "test_user", "SK": "PROFILE"}
        update_expression = "SET #name = :name"
        expression_values = {":name": "Updated Name"}
        expression_names = {"#name": "name"}

        updated_item = {"PK": "test_user", "SK": "PROFILE", "name": "Updated Name"}
        mock_db_connection.users_table.update_item.return_value = {"Attributes": updated_item}

        # Call method
        result = base_dao._safe_update_item(
            mock_db_connection.users_table,
            key,
            update_expression,
            expression_values,
            expression_names
        )

        # Verify result
        assert result == updated_item
        mock_db_connection.users_table.update_item.assert_called_once_with(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues='ALL_NEW'
        )

    def test_safe_update_item_without_names(self, base_dao, mock_db_connection):
        """Test update item without expression names"""
        key = {"PK": "test_user", "SK": "PROFILE"}
        update_expression = "SET email = :email"
        expression_values = {":email": "new@example.com"}

        updated_item = {"PK": "test_user", "SK": "PROFILE", "email": "new@example.com"}
        mock_db_connection.users_table.update_item.return_value = {"Attributes": updated_item}

        # Call method without expression_names
        result = base_dao._safe_update_item(
            mock_db_connection.users_table,
            key,
            update_expression,
            expression_values
        )

        # Verify result
        assert result == updated_item
        mock_db_connection.users_table.update_item.assert_called_once_with(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )

    def test_safe_update_item_exception(self, base_dao, mock_db_connection):
        """Test exception handling in safe_update_item"""
        # Mock exception
        mock_db_connection.users_table.update_item.side_effect = Exception("DynamoDB error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            base_dao._safe_update_item(
                mock_db_connection.users_table,
                {"PK": "test_user"},
                "SET #name = :name",
                {":name": "test"}
            )

        assert "DynamoDB error" in str(exc_info.value)

    def test_safe_delete_item_success(self, base_dao, mock_db_connection):
        """Test successful item deletion"""
        key = {"PK": "test_user", "SK": "PROFILE"}
        mock_db_connection.users_table.delete_item.return_value = {"Attributes": {"PK": "test_user"}}

        # Call method
        result = base_dao._safe_delete_item(mock_db_connection.users_table, key)

        # Should return True
        assert result is True
        mock_db_connection.users_table.delete_item.assert_called_once_with(Key=key, ReturnValues='ALL_OLD')

    def test_safe_delete_item_not_found(self, base_dao, mock_db_connection):
        """Test deleting non-existent item"""
        key = {"PK": "nonexistent", "SK": "PROFILE"}
        mock_db_connection.users_table.delete_item.return_value = {}

        # Call method
        result = base_dao._safe_delete_item(mock_db_connection.users_table, key)

        # Should return False
        assert result is False

    def test_safe_delete_item_exception(self, base_dao, mock_db_connection):
        """Test exception handling in safe_delete_item"""
        # Mock exception
        mock_db_connection.users_table.delete_item.side_effect = Exception("DynamoDB error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            base_dao._safe_delete_item(mock_db_connection.users_table, {"PK": "test"})

        assert "DynamoDB error" in str(exc_info.value)

    def test_safe_query_success(self, base_dao, mock_db_connection):
        """Test successful query"""
        from boto3.dynamodb.conditions import Key

        key_condition = Key('PK').eq('test_user')
        items = [
            {"PK": "test_user", "SK": "PROFILE"},
            {"PK": "test_user", "SK": "SETTINGS"}
        ]
        mock_db_connection.users_table.query.return_value = {"Items": items}

        # Call method
        result = base_dao._safe_query(mock_db_connection.users_table, key_condition)

        # Verify result
        assert result == items
        mock_db_connection.users_table.query.assert_called_once_with(
            KeyConditionExpression=key_condition
        )

    def test_safe_query_with_filter(self, base_dao, mock_db_connection):
        """Test query with filter condition"""
        from boto3.dynamodb.conditions import Key, Attr

        key_condition = Key('PK').eq('test_user')
        filter_condition = Attr('status').eq('active')

        items = [{"PK": "test_user", "SK": "PROFILE", "status": "active"}]
        mock_db_connection.users_table.query.return_value = {"Items": items}

        # Call method with filter
        result = base_dao._safe_query(
            mock_db_connection.users_table,
            key_condition,
            filter_condition=filter_condition
        )

        # Verify result
        assert result == items
        mock_db_connection.users_table.query.assert_called_once_with(
            KeyConditionExpression=key_condition,
            FilterExpression=filter_condition
        )

    def test_safe_query_with_index(self, base_dao, mock_db_connection):
        """Test query with GSI index"""
        from boto3.dynamodb.conditions import Key

        key_condition = Key('email').eq('test@example.com')
        items = [{"PK": "test_user", "email": "test@example.com"}]
        mock_db_connection.users_table.query.return_value = {"Items": items}

        # Call method with index
        result = base_dao._safe_query(
            mock_db_connection.users_table,
            key_condition,
            index_name="EmailIndex"
        )

        # Verify result
        assert result == items
        mock_db_connection.users_table.query.assert_called_once_with(
            KeyConditionExpression=key_condition,
            IndexName="EmailIndex"
        )

    def test_safe_query_with_limit(self, base_dao, mock_db_connection):
        """Test query with limit"""
        from boto3.dynamodb.conditions import Key

        key_condition = Key('PK').eq('test_user')
        items = [{"PK": "test_user", "SK": "PROFILE"}]
        mock_db_connection.users_table.query.return_value = {"Items": items}

        # Call method with limit
        result = base_dao._safe_query(
            mock_db_connection.users_table,
            key_condition,
            limit=10
        )

        # Verify result
        assert result == items
        mock_db_connection.users_table.query.assert_called_once_with(
            KeyConditionExpression=key_condition,
            Limit=10
        )

    def test_safe_query_with_all_options(self, base_dao, mock_db_connection):
        """Test query with all options"""
        from boto3.dynamodb.conditions import Key, Attr

        key_condition = Key('email').eq('test@example.com')
        filter_condition = Attr('status').eq('active')

        items = [{"PK": "test_user", "email": "test@example.com", "status": "active"}]
        mock_db_connection.users_table.query.return_value = {"Items": items}

        # Call method with all options
        result = base_dao._safe_query(
            mock_db_connection.users_table,
            key_condition,
            filter_condition=filter_condition,
            index_name="EmailIndex",
            limit=5
        )

        # Verify result
        assert result == items
        mock_db_connection.users_table.query.assert_called_once_with(
            KeyConditionExpression=key_condition,
            FilterExpression=filter_condition,
            IndexName="EmailIndex",
            Limit=5
        )

    def test_safe_query_empty_result(self, base_dao, mock_db_connection):
        """Test query with no results"""
        from boto3.dynamodb.conditions import Key

        key_condition = Key('PK').eq('nonexistent')
        mock_db_connection.users_table.query.return_value = {"Items": []}

        # Call method
        result = base_dao._safe_query(mock_db_connection.users_table, key_condition)

        # Should return empty list
        assert result == []

    def test_safe_query_exception(self, base_dao, mock_db_connection):
        """Test exception handling in safe_query"""
        from boto3.dynamodb.conditions import Key

        # Mock exception
        mock_db_connection.users_table.query.side_effect = Exception("DynamoDB error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            base_dao._safe_query(mock_db_connection.users_table, Key('PK').eq('test'))

        assert "DynamoDB error" in str(exc_info.value)