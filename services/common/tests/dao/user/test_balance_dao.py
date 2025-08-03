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
        """Sample balance for testing"""
        return Balance(
            Pk="BALANCE#testuser123",
            Sk="BALANCE",
            username="testuser123",
            current_balance=Decimal('100.00'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            entity_type="balance"
        )

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing"""
        return BalanceTransaction(
            Pk="TRANS#testuser123",
            Sk="2023-01-01T00:00:00",
            username="testuser123",
            transaction_id=UUID('12345678-1234-5678-9abc-123456789abc'),
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal('50.00'),
            description="Test deposit",
            status=TransactionStatus.COMPLETED,
            reference_id="ref123",
            created_at=datetime.utcnow(),
            entity_type="balance_transaction"
        )

    def test_create_balance_success(self, balance_dao, sample_balance, mock_db_connection):
        """Test successful balance creation"""
        # Mock successful database operation
        mock_db_connection.users_table.put_item.return_value = None

        result = balance_dao.create_balance(sample_balance)

        # Verify result
        assert result == sample_balance
        assert result.Pk == "BALANCE#testuser123"
        assert result.username == "testuser123"

        # Verify database was called
        mock_db_connection.users_table.put_item.assert_called_once()
        call_args = mock_db_connection.users_table.put_item.call_args[1]['Item']
        assert call_args['Pk'] == "BALANCE#testuser123"
        assert call_args['username'] == "testuser123"

    def test_create_balance_database_error(self, balance_dao, sample_balance, mock_db_connection):
        """Test balance creation with database error"""
        # Mock database error
        mock_db_connection.users_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'PutItem'
        )

        with pytest.raises(DatabaseOperationException):
            balance_dao.create_balance(sample_balance)

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
        assert result.Pk == "testuser123"
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('100.00')

        # Verify database was called
        mock_db_connection.users_table.get_item.assert_called_once_with(
            Key={'Pk': 'testuser123', 'Sk': 'BALANCE'}
        )

    def test_get_balance_not_found(self, balance_dao, mock_db_connection):
        """Test balance retrieval when not found"""
        # Mock empty response
        mock_db_connection.users_table.get_item.return_value = {}

        # Should raise EntityNotFoundException
        with pytest.raises(EntityNotFoundException) as exc_info:
            balance_dao.get_balance('nonexistent')

        assert "Balance for user 'nonexistent' not found" in str(exc_info.value)

    def test_get_balance_database_error(self, balance_dao, mock_db_connection):
        """Test balance retrieval with database error"""
        # Mock database error
        mock_db_connection.users_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'GetItem'
        )

        with pytest.raises(DatabaseOperationException):
            balance_dao.get_balance('testuser123')

    def test_update_balance_success(self, balance_dao, sample_balance, mock_db_connection):
        """Test successful balance update"""
        # Mock database response
        mock_updated_item = {
            'Pk': 'BALANCE#testuser123',
            'Sk': 'BALANCE',
            'username': 'testuser123',
            'current_balance': '150.00',
            'created_at': sample_balance.created_at.isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'entity_type': 'balance'
        }
        mock_db_connection.users_table.update_item.return_value = {'Attributes': mock_updated_item}

        result = balance_dao.update_balance('testuser123', Decimal('150.00'))

        # Verify result
        assert result is not None
        assert result.Pk == "BALANCE#testuser123"
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('150.00')

        # Verify database was called
        mock_db_connection.users_table.update_item.assert_called_once()

    def test_update_balance_database_error(self, balance_dao, mock_db_connection):
        """Test balance update with database error"""
        # Mock database error
        mock_db_connection.users_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'UpdateItem'
        )

        with pytest.raises(DatabaseOperationException):
            balance_dao.update_balance('testuser123', Decimal('150.00'))

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

        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction
        assert result.Pk == "TRANS#testuser123"
        assert result.username == "testuser123"
        assert result.Sk == "2023-01-01T00:00:00"

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

        with pytest.raises(DatabaseOperationException):
            balance_dao.create_transaction(sample_transaction)

    def test_create_transaction_with_balance_update(self, balance_dao, sample_transaction, sample_balance, mock_db_connection):
        """Test transaction creation with balance update"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        # Mock balance retrieval
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

        # Create transaction with completed status
        sample_transaction.status = TransactionStatus.COMPLETED
        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction

        # Verify balance was updated (should be called twice: once for get, once for update)
        assert mock_db_connection.users_table.get_item.call_count >= 1
        assert mock_db_connection.users_table.put_item.call_count >= 1

    def test_create_transaction_with_initial_balance(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction creation when balance doesn't exist"""
        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = None

        # Mock balance retrieval returns empty (balance doesn't exist)
        mock_db_connection.users_table.get_item.return_value = {}

        # Create transaction with completed status
        sample_transaction.status = TransactionStatus.COMPLETED
        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result == sample_transaction

        # Verify initial balance was created (should be called for balance creation)
        assert mock_db_connection.users_table.put_item.call_count >= 1

    def test_get_transaction_success(self, balance_dao, sample_transaction, mock_db_connection):
        """Test successful transaction retrieval"""
        # Mock get_user_transactions to return the sample transaction
        balance_dao.get_user_transactions = Mock(return_value=([sample_transaction], None))

        result = balance_dao.get_transaction('testuser123', sample_transaction.transaction_id)

        # Verify result
        assert result is not None
        assert result.Pk == "TRANS#testuser123"
        assert result.username == "testuser123"
        assert result.Sk == "2023-01-01T00:00:00"

    def test_get_transaction_not_found(self, balance_dao, mock_db_connection):
        """Test transaction retrieval when not found"""
        # Mock get_user_transactions to return empty list
        balance_dao.get_user_transactions = Mock(return_value=([], None))

        # Should raise EntityNotFoundException
        with pytest.raises(EntityNotFoundException) as exc_info:
            balance_dao.get_transaction('testuser123', UUID('12345678-1234-5678-9abc-123456789abc'))

        assert "Transaction '12345678-1234-5678-9abc-123456789abc' not found for user 'testuser123'" in str(exc_info.value)

    def test_get_transaction_database_error(self, balance_dao, mock_db_connection):
        """Test transaction retrieval with database error"""
        # Mock get_user_transactions to raise exception
        balance_dao.get_user_transactions = Mock(side_effect=DatabaseOperationException("Database error"))

        with pytest.raises(DatabaseOperationException):
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
        assert transactions[0].Pk == "TRANS#testuser123"
        assert transactions[0].username == "testuser123"
        assert transactions[0].Sk == "2023-01-01T00:00:00"

        # Verify database was called
        mock_db_connection.users_table.query.assert_called_once()

    def test_get_user_transactions_no_more_results(self, balance_dao, mock_db_connection):
        """Test user transactions retrieval with no results"""
        # Mock empty response
        mock_db_connection.users_table.query.return_value = {'Items': []}

        transactions, last_key = balance_dao.get_user_transactions('testuser123')

        # Verify result
        assert len(transactions) == 0
        assert last_key is None

    def test_update_transaction_status_success(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction status update (not supported in current design)"""
        # Transaction status updates are not supported in the current design
        with pytest.raises(DatabaseOperationException) as exc_info:
            balance_dao.update_transaction_status('testuser123', sample_transaction.transaction_id, 'pending')

        assert "Transaction status updates not supported" in str(exc_info.value)

    def test_update_transaction_status_database_error(self, balance_dao, sample_transaction, mock_db_connection):
        """Test transaction status update with database error (not supported in current design)"""
        # Transaction status updates are not supported in the current design
        with pytest.raises(DatabaseOperationException) as exc_info:
            balance_dao.update_transaction_status('testuser123', sample_transaction.transaction_id, 'pending')

        assert "Transaction status updates not supported" in str(exc_info.value)

    def test_balance_exists_true(self, balance_dao, sample_balance, mock_db_connection):
        """Test balance exists check when balance exists"""
        # Mock balance retrieval returns balance
        balance_dao.get_balance = Mock(return_value=sample_balance)

        result = balance_dao.balance_exists('testuser123')

        # Verify result
        assert result is True

    def test_balance_exists_false(self, balance_dao, mock_db_connection):
        """Test balance exists check when balance doesn't exist"""
        # Mock balance retrieval returns None
        balance_dao.get_balance = Mock(return_value=None)

        result = balance_dao.balance_exists('testuser123')

        # Verify result
        assert result is False

    def test_user_has_transactions_true(self, balance_dao, sample_transaction, mock_db_connection):
        """Test user has transactions check when transactions exist"""
        # Mock transactions retrieval returns transactions
        balance_dao.get_user_transactions = Mock(return_value=([sample_transaction], None))

        result = balance_dao.user_has_transactions('testuser123')

        # Verify result
        assert result is True

    def test_user_has_transactions_false(self, balance_dao, mock_db_connection):
        """Test user has transactions check when no transactions exist"""
        # Mock transactions retrieval returns empty list
        balance_dao.get_user_transactions = Mock(return_value=([], None))

        result = balance_dao.user_has_transactions('testuser123')

        # Verify result
        assert result is False