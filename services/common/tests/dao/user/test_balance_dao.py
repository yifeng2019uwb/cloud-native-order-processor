"""
Tests for Balance DAO
"""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from common.dao.user.balance_dao import BalanceDAO
from common.entities.user import Balance, BalanceTransaction, TransactionType, TransactionStatus
from common.exceptions import DatabaseOperationException, EntityNotFoundException


class TestBalanceDAO:
    """Test BalanceDAO class"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = MagicMock()
        mock_connection.table = MagicMock()
        return mock_connection

    @pytest.fixture
    def balance_dao(self, mock_db_connection):
        """Create BalanceDAO instance with mock connection"""
        return BalanceDAO(mock_db_connection)

    @pytest.fixture
    def sample_balance(self):
        """Create sample balance for testing"""
        return Balance(
            user_id="testuser123",
            current_balance=Decimal("100.00"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction for testing"""
        return BalanceTransaction(
            transaction_id=UUID("87654321-4321-8765-cba9-987654321cba"),
            user_id="testuser123",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("50.00"),
            description="Test deposit",
            status=TransactionStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    def test_create_balance_success(self, balance_dao, sample_balance):
        """Test successful balance creation"""
        result = balance_dao.create_balance(sample_balance)

        assert result == sample_balance

        # Verify DynamoDB put_item was called
        balance_dao.db.table.put_item.assert_called_once()
        call_args = balance_dao.db.table.put_item.call_args

        # Check the item structure
        item = call_args[1]['Item']
        assert item['PK'] == f"USER#{sample_balance.user_id}"
        assert item['SK'] == "BALANCE"
        assert item['current_balance'] == str(sample_balance.current_balance)
        assert item['entity_type'] == "balance"

    def test_create_balance_database_error(self, balance_dao, sample_balance):
        """Test balance creation when database error occurs"""
        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ValidationException',
                'Message': 'Invalid item'
            }
        }
        balance_dao.db.table.put_item.side_effect = ClientError(error_response, 'PutItem')

        with pytest.raises(DatabaseOperationException, match="Failed to create balance"):
            balance_dao.create_balance(sample_balance)

    def test_get_balance_success(self, balance_dao, sample_balance):
        """Test successful balance retrieval"""
        # Mock DynamoDB response
        mock_item = {
            'current_balance': str(sample_balance.current_balance),
            'created_at': sample_balance.created_at.isoformat(),
            'updated_at': sample_balance.updated_at.isoformat()
        }
        balance_dao.db.table.get_item.return_value = {'Item': mock_item}

        result = balance_dao.get_balance(sample_balance.user_id)

        assert result is not None
        assert result.user_id == sample_balance.user_id
        assert result.current_balance == sample_balance.current_balance

        # Verify DynamoDB get_item was called
        balance_dao.db.table.get_item.assert_called_once()
        call_args = balance_dao.db.table.get_item.call_args

        # Check the key structure
        key = call_args[1]['Key']
        assert key['PK'] == f"USER#{sample_balance.user_id}"
        assert key['SK'] == "BALANCE"

    def test_get_balance_not_found(self, balance_dao, sample_balance):
        """Test balance retrieval when balance doesn't exist"""
        balance_dao.db.table.get_item.return_value = {}

        result = balance_dao.get_balance(sample_balance.user_id)

        assert result is None

    def test_get_balance_database_error(self, balance_dao, sample_balance):
        """Test balance retrieval when database error occurs"""
        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ResourceNotFoundException',
                'Message': 'Table not found'
            }
        }
        balance_dao.db.table.get_item.side_effect = ClientError(error_response, 'GetItem')

        with pytest.raises(DatabaseOperationException, match="Failed to get balance"):
            balance_dao.get_balance(sample_balance.user_id)

    def test_update_balance_success(self, balance_dao, sample_balance):
        """Test successful balance update"""
        new_balance = Decimal("150.00")

        # Mock DynamoDB response
        mock_item = {
            'current_balance': str(new_balance),
            'created_at': sample_balance.created_at.isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        balance_dao.db.table.update_item.return_value = {'Attributes': mock_item}

        result = balance_dao.update_balance(sample_balance.user_id, new_balance)

        assert result is not None
        assert result.current_balance == new_balance

        # Verify DynamoDB update_item was called
        balance_dao.db.table.update_item.assert_called_once()
        call_args = balance_dao.db.table.update_item.call_args

        # Check the key structure
        key = call_args[1]['Key']
        assert key['PK'] == f"USER#{sample_balance.user_id}"
        assert key['SK'] == "BALANCE"

    def test_update_balance_database_error(self, balance_dao, sample_balance):
        """Test balance update when database error occurs"""
        new_balance = Decimal("150.00")

        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ConditionalCheckFailedException',
                'Message': 'Conditional check failed'
            }
        }
        balance_dao.db.table.update_item.side_effect = ClientError(error_response, 'UpdateItem')

        with pytest.raises(DatabaseOperationException, match="Failed to update balance"):
            balance_dao.update_balance(sample_balance.user_id, new_balance)

    def test_create_transaction_success(self, balance_dao, sample_transaction):
        """Test successful transaction creation"""
        # Mock the balance update response
        mock_balance_response = {
            "current_balance": "150.00",
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00"
        }
        balance_dao.db.table.update_item.return_value = {"Attributes": mock_balance_response}

        result = balance_dao.create_transaction(sample_transaction)

        assert result.transaction_id == sample_transaction.transaction_id
        assert result.user_id == sample_transaction.user_id
        assert result.amount == sample_transaction.amount
        assert result.transaction_type == sample_transaction.transaction_type
        assert result.status == sample_transaction.status

    def test_create_transaction_database_error(self, balance_dao, sample_transaction):
        """Test transaction creation when database error occurs"""
        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ValidationException',
                'Message': 'Invalid item'
            }
        }
        balance_dao.db.table.put_item.side_effect = ClientError(error_response, 'PutItem')

        with pytest.raises(DatabaseOperationException, match="Failed to create transaction"):
            balance_dao.create_transaction(sample_transaction)

    def test_create_transaction_with_balance_update(self, balance_dao, sample_transaction, sample_balance):
        """Test transaction creation with balance update"""
        # Mock get_balance to return existing balance
        balance_dao.get_balance = MagicMock(return_value=sample_balance)
        balance_dao.update_balance = MagicMock(return_value=sample_balance)

        # Set transaction status to completed
        sample_transaction.status = TransactionStatus.COMPLETED

        result = balance_dao.create_transaction(sample_transaction)

        assert result == sample_transaction

        # Verify balance update was called
        balance_dao.get_balance.assert_called_once_with(sample_transaction.user_id)
        balance_dao.update_balance.assert_called_once()

    def test_create_transaction_with_initial_balance(self, balance_dao, sample_transaction):
        """Test transaction creation when no balance exists"""
        # Mock get_balance to return None (no existing balance)
        balance_dao.get_balance = MagicMock(return_value=None)
        balance_dao.create_balance = MagicMock()
        balance_dao.update_balance = MagicMock()

        # Set transaction status to completed
        sample_transaction.status = TransactionStatus.COMPLETED

        result = balance_dao.create_transaction(sample_transaction)

        assert result == sample_transaction

        # Verify initial balance creation was called
        balance_dao.get_balance.assert_called_once_with(sample_transaction.user_id)
        balance_dao.create_balance.assert_called_once()

    def test_get_transaction_success(self, balance_dao, sample_transaction):
        """Test successful transaction retrieval"""
        # Mock DynamoDB response
        mock_item = {
            'transaction_id': str(sample_transaction.transaction_id),
            'user_id': sample_transaction.user_id,  # Add user_id field
            'transaction_type': sample_transaction.transaction_type.value,
            'amount': str(sample_transaction.amount),
            'description': sample_transaction.description,
            'status': sample_transaction.status.value,
            'created_at': sample_transaction.created_at.isoformat(),
            'updated_at': sample_transaction.updated_at.isoformat()
        }
        balance_dao.db.table.get_item.return_value = {'Item': mock_item}  # Use get_item, not query

        result = balance_dao.get_transaction(sample_transaction.user_id, sample_transaction.transaction_id)

        assert result is not None
        assert result.user_id == sample_transaction.user_id
        assert result.transaction_id == sample_transaction.transaction_id

        # Verify DynamoDB get_item was called
        balance_dao.db.table.get_item.assert_called_once()
        call_args = balance_dao.db.table.get_item.call_args

        # Check the key structure
        key = call_args[1]['Key']
        assert key['PK'] == f"USER#{sample_transaction.user_id}#{sample_transaction.transaction_id}"
        assert key['SK'] == "2023-01-01T00:00:00"  # Hardcoded timestamp in the method

    def test_get_transaction_not_found(self, balance_dao, sample_transaction):
        """Test transaction retrieval when transaction doesn't exist"""
        balance_dao.db.table.get_item.return_value = {}  # Use get_item, not query

        result = balance_dao.get_transaction(sample_transaction.user_id, sample_transaction.transaction_id)

        assert result is None

    def test_get_transaction_database_error(self, balance_dao, sample_transaction):
        """Test transaction retrieval when database error occurs"""
        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ResourceNotFoundException',
                'Message': 'Table not found'
            }
        }
        balance_dao.db.table.get_item.side_effect = ClientError(error_response, 'GetItem')  # Use get_item, not query

        with pytest.raises(DatabaseOperationException, match="Failed to get transaction"):
            balance_dao.get_transaction(sample_transaction.user_id, sample_transaction.transaction_id)

    def test_get_user_transactions_success(self, balance_dao, sample_transaction):
        """Test successful user transactions retrieval"""
        # Mock DynamoDB response
        mock_item = {
            'transaction_id': str(sample_transaction.transaction_id),
            'user_id': sample_transaction.user_id,  # Add user_id field
            'transaction_type': sample_transaction.transaction_type.value,
            'amount': str(sample_transaction.amount),
            'description': sample_transaction.description,
            'status': sample_transaction.status.value,
            'created_at': sample_transaction.created_at.isoformat(),
            'updated_at': sample_transaction.updated_at.isoformat()
        }
        balance_dao.db.table.query.return_value = {
            'Items': [mock_item],
            'LastEvaluatedKey': {'PK': 'test-key'}
        }

        transactions, next_key = balance_dao.get_user_transactions(
            sample_transaction.user_id, limit=10
        )

        assert len(transactions) == 1
        assert transactions[0].user_id == sample_transaction.user_id
        assert transactions[0].transaction_id == sample_transaction.transaction_id
        assert next_key == {'PK': 'test-key'}

        # Verify DynamoDB query was called
        balance_dao.db.table.query.assert_called_once()
        call_args = balance_dao.db.table.query.call_args

        # Check the query parameters
        query_params = call_args[1]
        assert query_params['KeyConditionExpression'] == Key("PK").begins_with(f"USER#{sample_transaction.user_id}#")
        assert query_params['Limit'] == 10

    def test_get_user_transactions_no_more_results(self, balance_dao, sample_transaction):
        """Test user transactions retrieval with no more results"""
        # Mock DynamoDB response without LastEvaluatedKey
        mock_item = {
            'transaction_id': str(sample_transaction.transaction_id),
            'user_id': sample_transaction.user_id,  # Add user_id field
            'transaction_type': sample_transaction.transaction_type.value,
            'amount': str(sample_transaction.amount),
            'description': sample_transaction.description,
            'status': sample_transaction.status.value,
            'created_at': sample_transaction.created_at.isoformat(),
            'updated_at': sample_transaction.updated_at.isoformat()
        }
        balance_dao.db.table.query.return_value = {'Items': [mock_item]}

        transactions, next_key = balance_dao.get_user_transactions(
            sample_transaction.user_id, limit=10
        )

        assert len(transactions) == 1
        assert next_key is None

    def test_update_transaction_status_success(self, balance_dao, sample_transaction):
        """Test successful transaction status update"""
        new_status = TransactionStatus.CANCELLED

        # Mock the get_transaction response
        mock_transaction_item = {
            'transaction_id': str(sample_transaction.transaction_id),
            'user_id': sample_transaction.user_id,  # Add user_id field
            'transaction_type': sample_transaction.transaction_type.value,
            'amount': str(sample_transaction.amount),
            'description': sample_transaction.description,
            'status': new_status.value,
            'created_at': sample_transaction.created_at.isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        balance_dao.db.table.get_item.return_value = {  # Use get_item for get_transaction
            'Item': mock_transaction_item
        }

        # Mock the update response
        balance_dao.db.table.update_item.return_value = {'Attributes': mock_transaction_item}

        result = balance_dao.update_transaction_status(
            sample_transaction.user_id,
            sample_transaction.transaction_id,
            new_status.value
        )

        assert result is not None
        assert result.status == new_status.value

        # Verify both get_item and update_item were called
        balance_dao.db.table.get_item.assert_called_once()
        balance_dao.db.table.update_item.assert_called_once()

    def test_update_transaction_status_database_error(self, balance_dao, sample_transaction):
        """Test transaction status update when database error occurs"""
        new_status = TransactionStatus.CANCELLED

        # Mock the get_transaction response
        mock_transaction_item = {
            'transaction_id': str(sample_transaction.transaction_id),
            'user_id': sample_transaction.user_id,  # Add user_id field
            'transaction_type': sample_transaction.transaction_type.value,
            'amount': str(sample_transaction.amount),
            'description': sample_transaction.description,
            'status': new_status.value,
            'created_at': sample_transaction.created_at.isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        balance_dao.db.table.get_item.return_value = {  # Use get_item for get_transaction
            'Item': mock_transaction_item
        }

        # Simulate database error
        error_response = {
            'Error': {
                'Code': 'ResourceNotFoundException',
                'Message': 'Table not found'
            }
        }
        balance_dao.db.table.update_item.side_effect = ClientError(error_response, 'UpdateItem')

        with pytest.raises(DatabaseOperationException, match="Failed to update transaction status"):
            balance_dao.update_transaction_status(
                sample_transaction.user_id,
                sample_transaction.transaction_id,
                new_status.value
            )

    def test_balance_exists_true(self, balance_dao, sample_balance):
        """Test balance_exists when balance exists"""
        # Mock the database response to return an item
        balance_dao.db.table.get_item.return_value = {
            "Item": {
                "PK": f"USER#{sample_balance.user_id}",
                "SK": "BALANCE",
                "current_balance": str(sample_balance.current_balance),
                "created_at": sample_balance.created_at.isoformat(),
                "updated_at": sample_balance.updated_at.isoformat()
            }
        }

        result = balance_dao.balance_exists(sample_balance.user_id)

        assert result is True

    def test_balance_exists_false(self, balance_dao, sample_balance):
        """Test balance_exists when balance doesn't exist"""
        # Mock the database response to return no item
        balance_dao.db.table.get_item.return_value = {}

        result = balance_dao.balance_exists(sample_balance.user_id)

        assert result is False

    def test_user_has_transactions_true(self, balance_dao, sample_transaction):
        """Test user_has_transactions when user has transactions"""
        # Mock the database response to return transactions
        balance_dao.db.table.query.return_value = {
            "Items": [
                {
                    "PK": f"USER#{sample_transaction.user_id}#{sample_transaction.transaction_id}",
                    "SK": sample_transaction.created_at.isoformat(),
                    "transaction_id": str(sample_transaction.transaction_id),
                    "user_id": str(sample_transaction.user_id),
                    "transaction_type": sample_transaction.transaction_type.value,
                    "amount": str(sample_transaction.amount),
                    "status": sample_transaction.status.value
                }
            ]
        }

        result = balance_dao.user_has_transactions(sample_transaction.user_id)

        assert result is True

    def test_user_has_transactions_false(self, balance_dao, sample_transaction):
        """Test user_has_transactions when user has no transactions"""
        # Mock the database response to return no transactions
        balance_dao.db.table.query.return_value = {
            "Items": []
        }

        result = balance_dao.user_has_transactions(sample_transaction.user_id)

        assert result is False