"""
Tests for Balance DAO
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from src.data.dao.user.balance_dao import BalanceDAO
from src.data.entities.user import Balance, BalanceTransaction, TransactionType, TransactionStatus
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPBalanceNotFoundException, CNOPTransactionNotFoundException


class TestBalanceDAO:
    """Test BalanceDAO class"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = MagicMock()
        mock_connection.table = MagicMock()
        mock_connection.users_table = MagicMock()
        return mock_connection

    @pytest.fixture
    def balance_dao(self, mock_db_connection):
        """Create BalanceDAO instance with mock connection"""
        return BalanceDAO(mock_db_connection)

    @pytest.fixture
    def sample_balance(self):
        """Sample balance for testing"""
        return Balance(
            username="testuser123",
            current_balance=Decimal('100.00'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing"""
        return BalanceTransaction(
            username="testuser123",
            transaction_id=UUID('12345678-1234-5678-9abc-123456789abc'),
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal('50.00'),
            description="Test deposit",
            status=TransactionStatus.COMPLETED,
            reference_id="ref123",
            created_at=datetime.utcnow()
        )

    @pytest.fixture
    def sample_balance_create(self):
        """Sample Balance for testing"""
        return Balance(
            username="testuser123",
            current_balance=Decimal('100.00')
        )

    def test_get_balance_success(self, balance_dao, sample_balance, mock_db_connection):
        """Test successful balance retrieval"""
        # Mock database response
        mock_item = {
            'Pk': 'testuser123',
            'Sk': 'BALANCE',
            'username': 'testuser123',
            'current_balance': '100.00',
            'created_at': sample_balance.created_at.isoformat(),
            'updated_at': sample_balance.updated_at.isoformat(),
            'entity_type': 'balance'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        result = balance_dao.get_balance('testuser123')

        # Verify result
        assert result is not None

        assert result.username == "testuser123"
        assert result.current_balance == Decimal('100.00')

        # Verify database was called
        mock_db_connection.users_table.get_item.assert_called_once_with(
            Key={'Pk': 'testuser123', 'Sk': 'BALANCE'}
        )

    def test_get_balance_not_found(self, balance_dao, mock_db_connection):
        """Test balance retrieval when not found"""
        # Mock empty database response
        mock_db_connection.users_table.get_item.return_value = {}

        # Should raise BalanceNotFoundException
        with pytest.raises(CNOPBalanceNotFoundException):
            balance_dao.get_balance('nonexistent')

    def test_get_balance_database_error(self, balance_dao, mock_db_connection):
        """Test balance retrieval with database error"""
        # Mock database error
        mock_db_connection.users_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'GetItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            balance_dao.get_balance('testuser123')

    def test_update_balance_success(self, balance_dao, sample_balance, mock_db_connection):
        """Test successful balance update"""
        # Mock the _safe_get_item method to return existing balance
        mock_existing_item = {
            'Pk': 'testuser123',
            'Sk': 'BALANCE',
            'username': 'testuser123',
            'current_balance': Decimal('100.00'),
            'created_at': sample_balance.created_at.isoformat(),
            'updated_at': sample_balance.updated_at.isoformat(),
            'entity_type': 'balance'
        }

        # Mock _safe_get_item to return the existing balance
        balance_dao._safe_get_item = MagicMock(return_value=mock_existing_item)

        # Mock put_item for the update
        mock_db_connection.users_table.put_item.return_value = None

        result = balance_dao.update_balance('testuser123', Decimal('150.00'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('150.00')

        # Verify database was called
        mock_db_connection.users_table.put_item.assert_called_once()

    def test_update_balance_database_error(self, balance_dao, mock_db_connection):
        """Test balance update with database error"""
        # Mock database error
        mock_db_connection.users_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'UpdateItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            balance_dao.update_balance('testuser123', Decimal('150.00'))

    def test_create_balance_success(self, balance_dao, sample_balance_create, mock_db_connection):
        """Test successful balance creation"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        result = balance_dao.create_balance(sample_balance_create)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('100.00')

        # Verify database was called
        mock_db_connection.users_table.put_item.assert_called_once()
        call_args = mock_db_connection.users_table.put_item.call_args[1]['Item']
        assert call_args['Pk'] == "testuser123"
        assert call_args['Sk'] == "BALANCE"
        assert call_args['username'] == "testuser123"
        assert call_args['current_balance'] == Decimal('100.00')
        assert call_args['entity_type'] == "balance"

    def test_create_balance_database_error(self, balance_dao, sample_balance_create, mock_db_connection):
        """Test balance creation with database error"""
        # Mock database error
        mock_db_connection.users_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'PutItem'
        )

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while creating balance"):
            balance_dao.create_balance(sample_balance_create)

    def test_create_balance_generic_exception(self, balance_dao, sample_balance_create, mock_db_connection):
        """Test balance creation with generic exception"""
        # Mock generic exception
        mock_db_connection.users_table.put_item.side_effect = Exception("Generic error")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while creating balance"):
            balance_dao.create_balance(sample_balance_create)

    def test_create_transaction_success(self, balance_dao, sample_transaction, mock_db_connection):
        """Test successful transaction creation"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        # Mock that balance exists (for completed transactions)
        mock_db_connection.users_table.get_item.return_value = {
            'Item': {
                'Pk': 'testuser123',
                'Sk': 'BALANCE',
                'username': 'testuser123',
                'current_balance': '100.00',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }

        # Mock update_item response for balance update
        mock_db_connection.users_table.update_item.return_value = {
            'Attributes': {
                'Pk': 'testuser123',
                'Sk': 'BALANCE',
                'username': 'testuser123',
                'current_balance': '150.00',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }

        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction
        assert result.username == "testuser123"

        # Verify database was called
        mock_db_connection.users_table.put_item.assert_called_once()
        call_args = mock_db_connection.users_table.put_item.call_args[1]['Item']
        assert call_args['Pk'] == "TRANS#testuser123"
        assert call_args['username'] == "testuser123"
        # The Sk timestamp is dynamic, so just check it exists and has the right format
        assert 'Sk' in call_args
        assert call_args['Sk'].startswith('2025-')  # Current year

    def test_create_transaction_database_error(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction creation with database error"""
        # Mock database error
        mock_db_connection.users_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'PutItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            balance_dao.create_transaction(sample_transaction)

    def test_create_transaction_generic_exception(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction creation with generic exception"""
        # Mock generic exception
        mock_db_connection.users_table.put_item.side_effect = Exception("Generic error")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while creating transaction"):
            balance_dao.create_transaction(sample_transaction)

    def test_create_transaction_with_balance_update(self, balance_dao, sample_transaction, sample_balance, mock_db_connection):
        """Test transaction creation (balance update is now handled separately)"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        # Create transaction with completed status
        sample_transaction.status = TransactionStatus.COMPLETED
        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction

        # Verify only transaction was created (balance update is now separate)
        assert mock_db_connection.users_table.put_item.call_count == 1

    def test_create_transaction_with_initial_balance(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction creation (balance existence is now handled separately)"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        # Create transaction with completed status
        sample_transaction.status = TransactionStatus.COMPLETED

        # Should succeed since create_transaction no longer checks balance
        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction

    def test_update_balance_from_transaction_success(self, balance_dao, sample_transaction, sample_balance, mock_db_connection):
        """Test successful balance update from transaction"""
        # Mock successful operations
        mock_db_connection.users_table.get_item.return_value = {
            'Item': {
                'Pk': 'testuser123',
                'Sk': 'BALANCE',
                'username': 'testuser123',
                'current_balance': '100.00',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }
        mock_db_connection.users_table.update_item.return_value = {
            'Attributes': {
                'Pk': 'testuser123',
                'Sk': 'BALANCE',
                'username': 'testuser123',
                'current_balance': '150.00',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }

        # Test the private method
        balance_dao._update_balance_from_transaction(sample_transaction)

        # Verify get_balance was called (twice: once directly, once from update_balance)
        assert mock_db_connection.users_table.get_item.call_count == 2
        # Verify update_balance was called
        mock_db_connection.users_table.put_item.assert_called_once()

    def test_update_balance_from_transaction_get_balance_failure(self, balance_dao, sample_transaction, mock_db_connection):
        """Test balance update from transaction when get_balance fails"""
        # Mock get_balance failure
        mock_db_connection.users_table.get_item.side_effect = CNOPBalanceNotFoundException("Balance not found")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while updating balance from transaction"):
            balance_dao._update_balance_from_transaction(sample_transaction)

    def test_update_balance_from_transaction_update_balance_failure(self, balance_dao, sample_transaction, sample_balance, mock_db_connection):
        """Test balance update from transaction when update_balance fails"""
        # Mock successful get_balance but failed update_balance
        mock_db_connection.users_table.get_item.return_value = {
            'Item': {
                'Pk': 'testuser123',
                'Sk': 'BALANCE',
                'username': 'testuser123',
                'current_balance': '100.00',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }
        mock_db_connection.users_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Update failed'}},
            'PutItem'
        )

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while updating balance from transaction"):
            balance_dao._update_balance_from_transaction(sample_transaction)

    def test_update_balance_from_transaction_generic_exception(self, balance_dao, sample_transaction, mock_db_connection):
        """Test balance update from transaction with generic exception"""
        # Mock generic exception
        mock_db_connection.users_table.get_item.side_effect = Exception("Generic error")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while updating balance from transaction"):
            balance_dao._update_balance_from_transaction(sample_transaction)

    def test_get_transaction_success(self, balance_dao, sample_transaction, mock_db_connection):
        """Test successful transaction retrieval"""
        # Mock get_user_transactions to return the sample transaction
        balance_dao.get_user_transactions = Mock(return_value=([sample_transaction], None))

        result = balance_dao.get_transaction('testuser123', sample_transaction.transaction_id)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"

    def test_get_transaction_not_found(self, balance_dao, mock_db_connection):
        """Test transaction retrieval when not found"""
        # Mock get_user_transactions to return empty list
        balance_dao.get_user_transactions = Mock(return_value=([], None))

        # Should raise DatabaseOperationException (wraps EntityNotFoundException)
        with pytest.raises(CNOPDatabaseOperationException):
            balance_dao.get_transaction('testuser123', UUID('12345678-1234-5678-9abc-123456789abc'))

    def test_get_transaction_database_error(self, balance_dao, mock_db_connection):
        """Test transaction retrieval with database error"""
        # Mock get_user_transactions to raise exception
        balance_dao.get_user_transactions = Mock(side_effect=CNOPDatabaseOperationException("Database error"))

        with pytest.raises(CNOPDatabaseOperationException):
            balance_dao.get_transaction('testuser123', UUID('12345678-1234-5678-9abc-123456789abc'))

    def test_get_transaction_generic_exception(self, balance_dao, mock_db_connection):
        """Test transaction retrieval with generic exception"""
        # Mock get_user_transactions to raise generic exception
        balance_dao.get_user_transactions = Mock(side_effect=Exception("Generic error"))

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while retrieving transaction"):
            balance_dao.get_transaction('testuser123', UUID('12345678-1234-5678-9abc-123456789abc'))

    def test_get_user_transactions_success(self, balance_dao, sample_transaction, mock_db_connection):
        """Test successful user transactions retrieval"""
        # Mock database response
        mock_items = [{
            'Pk': 'TRANS#testuser123',
            'Sk': '2023-01-01T00:00:00',
            'username': 'testuser123',
            'transaction_id': str(sample_transaction.transaction_id),
            'transaction_type': 'deposit',
            'amount': '50.00',
            'description': 'Test deposit',
            'status': 'completed',
            'reference_id': 'ref123',
            'created_at': sample_transaction.created_at.isoformat(),
            'entity_type': 'balance_transaction'
        }]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        transactions, last_key = balance_dao.get_user_transactions('testuser123')

        # Verify result
        assert len(transactions) == 1
        assert transactions[0].username == "testuser123"

        # Verify database was called
        mock_db_connection.users_table.query.assert_called_once()

    def test_get_user_transactions_with_pagination(self, balance_dao, sample_transaction, mock_db_connection):
        """Test user transactions retrieval with pagination"""
        # Mock database response with pagination
        mock_items = [{
            'Pk': 'TRANS#testuser123',
            'Sk': '2023-01-01T00:00:00',
            'username': 'testuser123',
            'transaction_id': str(sample_transaction.transaction_id),
            'transaction_type': 'deposit',
            'amount': '50.00',
            'description': 'Test deposit',
            'status': 'completed',
            'reference_id': 'ref123',
            'created_at': sample_transaction.created_at.isoformat(),
            'entity_type': 'balance_transaction'
        }]
        mock_last_key = {'Pk': 'TRANS#testuser123', 'Sk': '2023-01-01T00:00:00'}
        mock_db_connection.users_table.query.return_value = {
            'Items': mock_items,
            'LastEvaluatedKey': mock_last_key
        }

        transactions, last_key = balance_dao.get_user_transactions('testuser123', limit=10, start_key=mock_last_key)

        # Verify result
        assert len(transactions) == 1
        assert last_key == mock_last_key

        # Verify database was called with pagination parameters
        mock_db_connection.users_table.query.assert_called_once()
        call_args = mock_db_connection.users_table.query.call_args[1]
        assert call_args['Limit'] == 10
        assert call_args['ExclusiveStartKey'] == mock_last_key

    def test_get_user_transactions_no_more_results(self, balance_dao, mock_db_connection):
        """Test user transactions retrieval with no results"""
        # Mock empty response
        mock_db_connection.users_table.query.return_value = {'Items': []}

        transactions, last_key = balance_dao.get_user_transactions('testuser123')

        # Verify result
        assert len(transactions) == 0
        assert last_key is None

    def test_get_user_transactions_database_error(self, balance_dao, mock_db_connection):
        """Test user transactions retrieval with database error"""
        # Mock database error
        mock_db_connection.users_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'Query'
        )

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while retrieving transactions"):
            balance_dao.get_user_transactions('testuser123')

    def test_get_user_transactions_generic_exception(self, balance_dao, mock_db_connection):
        """Test user transactions retrieval with generic exception"""
        # Mock generic exception
        mock_db_connection.users_table.query.side_effect = Exception("Generic error")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while retrieving transactions"):
            balance_dao.get_user_transactions('testuser123')

    def test_get_user_transactions_with_custom_limit(self, balance_dao, sample_transaction, mock_db_connection):
        """Test user transactions retrieval with custom limit"""
        # Mock database response
        mock_items = [{
            'Pk': 'TRANS#testuser123',
            'Sk': '2023-01-01T00:00:00',
            'username': 'testuser123',
            'transaction_id': str(sample_transaction.transaction_id),
            'transaction_type': 'deposit',
            'amount': '50.00',
            'description': 'Test deposit',
            'status': 'completed',
            'reference_id': 'ref123',
            'created_at': sample_transaction.created_at.isoformat(),
            'entity_type': 'balance_transaction'
        }]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        transactions, last_key = balance_dao.get_user_transactions('testuser123', limit=25)

        # Verify result
        assert len(transactions) == 1

        # Verify database was called with custom limit
        mock_db_connection.users_table.query.assert_called_once()
        call_args = mock_db_connection.users_table.query.call_args[1]
        assert call_args['Limit'] == 25
