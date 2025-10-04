"""
Tests for Balance DAO
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from src.data.dao.user.balance_dao import BalanceDAO
from src.data.entities.user.balance import (Balance, BalanceItem, BalanceTransaction,
                                           BalanceTransactionItem, TransactionStatus, TransactionType)
from src.data.entities.entity_constants import BalanceFields, TransactionFields
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import (CNOPBalanceNotFoundException,
                                              CNOPTransactionNotFoundException)
from tests.data.dao.mock_constants import MockDatabaseMethods


class TestBalanceDAO:
    """Test BalanceDAO class"""

    @pytest.fixture
    def balance_dao(self):
        """Create BalanceDAO instance (PynamoDB doesn't need db_connection)"""
        return BalanceDAO()

    @pytest.fixture
    def sample_balance(self):
        """Sample balance for testing"""
        return Balance(
            username="testuser123",
            current_balance=Decimal('100.00'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing"""
        return BalanceTransaction(
            username="testuser123",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal('50.00'),
            description="Test deposit",
            status=TransactionStatus.COMPLETED,
            reference_id="test_ref_123"
        )

    # ==================== GET BALANCE TESTS ====================

    @patch.object(BalanceItem, MockDatabaseMethods.GET)
    def test_get_balance_success(self, mock_get, balance_dao, sample_balance):
        """Test successful balance retrieval"""
        # Mock BalanceItem.get to return a real BalanceItem
        balance_item = BalanceItem(
            username='testuser123',
            current_balance='100.00',
            created_at=sample_balance.created_at,
            updated_at=sample_balance.updated_at
        )
        mock_get.return_value = balance_item

        result = balance_dao.get_balance('testuser123')

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('100.00')

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('testuser123', BalanceFields.SK_VALUE)

    @patch.object(BalanceItem, MockDatabaseMethods.GET)
    def test_get_balance_not_found(self, mock_get, balance_dao):
        """Test balance retrieval when not found"""
        # Mock BalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = BalanceItem.DoesNotExist()

        # Should raise BalanceNotFoundException
        with pytest.raises(CNOPBalanceNotFoundException) as exc_info:
            balance_dao.get_balance('nonexistent')

        assert "Balance for user 'nonexistent' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent', BalanceFields.SK_VALUE)

    @patch.object(BalanceItem, MockDatabaseMethods.GET)
    def test_get_balance_database_error(self, mock_get, balance_dao):
        """Test balance retrieval with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.get_balance('testuser123')

        assert "Failed to get balance for user 'testuser123'" in str(exc_info.value)
        mock_get.assert_called_once_with('testuser123', BalanceFields.SK_VALUE)

    # ==================== CREATE BALANCE TESTS ====================

    @patch.object(BalanceItem, MockDatabaseMethods.SAVE)
    def test_create_balance_success(self, mock_save, balance_dao, sample_balance):
        """Test successful balance creation"""
        # Mock save to return None
        mock_save.return_value = None

        result = balance_dao.create_balance(sample_balance)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('100.00')

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(BalanceItem, MockDatabaseMethods.SAVE)
    def test_create_balance_database_error(self, mock_save, balance_dao, sample_balance):
        """Test balance creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.create_balance(sample_balance)

        assert "Database operation failed while creating balance for user 'testuser123'" in str(exc_info.value)
        mock_save.assert_called_once()

    # ==================== UPDATE BALANCE TESTS ====================

    @patch.object(BalanceItem, MockDatabaseMethods.GET)
    @patch.object(BalanceItem, MockDatabaseMethods.SAVE)
    def test_update_balance_success(self, mock_save, mock_get, balance_dao, sample_balance):
        """Test successful balance update"""
        # Mock BalanceItem.get to return existing balance
        existing_balance_item = BalanceItem(
            username='testuser123',
            current_balance='100.00',
            created_at=sample_balance.created_at,
            updated_at=sample_balance.updated_at
        )
        mock_get.return_value = existing_balance_item

        # Mock save to return None
        mock_save.return_value = None

        result = balance_dao.update_balance('testuser123', Decimal('150.00'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.current_balance == Decimal('150.00')

        # Verify get and save were called
        mock_get.assert_called_once_with('testuser123', BalanceFields.SK_VALUE)
        mock_save.assert_called_once()

    @patch.object(BalanceItem, MockDatabaseMethods.GET)
    def test_update_balance_not_found(self, mock_get, balance_dao):
        """Test balance update when balance not found"""
        # Mock BalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = BalanceItem.DoesNotExist()

        with pytest.raises(CNOPBalanceNotFoundException) as exc_info:
            balance_dao.update_balance('nonexistent', Decimal('150.00'))

        assert "Balance for user 'nonexistent' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent', BalanceFields.SK_VALUE)

    # ==================== CREATE TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_transaction_success(self, mock_save, balance_dao, sample_transaction):
        """Test successful transaction creation"""
        # Mock save to return None
        mock_save.return_value = None

        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.amount == Decimal('50.00')
        assert result.transaction_type == TransactionType.DEPOSIT

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_transaction_database_error(self, mock_save, balance_dao, sample_transaction):
        """Test transaction creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.create_transaction(sample_transaction)

        assert "Database operation failed while creating transaction for user 'testuser123'" in str(exc_info.value)
        mock_save.assert_called_once()

    # ==================== GET TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_transaction_success(self, mock_query, balance_dao, sample_transaction):
        """Test successful transaction retrieval"""
        # Mock query to return transaction
        transaction_item = BalanceTransactionItem(
            username='testuser123',
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id='test_ref_123',
            created_at=sample_transaction.created_at
        )
        mock_query.return_value = [transaction_item]

        result = balance_dao.get_transaction('testuser123', sample_transaction.transaction_id)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.transaction_id == sample_transaction.transaction_id

        # Verify query was called
        mock_query.assert_called_once()

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_transaction_not_found(self, mock_query, balance_dao):
        """Test transaction retrieval when not found"""
        # Mock empty query result
        mock_query.return_value = []

        with pytest.raises(CNOPTransactionNotFoundException) as exc_info:
            balance_dao.get_transaction('testuser123', UUID('12345678-1234-5678-9012-123456789012'))

        assert "Transaction '12345678-1234-5678-9012-123456789012' not found for user 'testuser123'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== GET USER TRANSACTIONS TESTS ====================

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_transactions_success(self, mock_query, balance_dao, sample_transaction):
        """Test successful user transactions retrieval"""
        # Mock query to return transactions
        transaction_item = BalanceTransactionItem(
            username='testuser123',
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id='test_ref_123',
            created_at=sample_transaction.created_at
        )
        mock_query.return_value = [transaction_item]

        transactions, last_key = balance_dao.get_user_transactions('testuser123')

        # Verify result
        assert len(transactions) == 1
        assert transactions[0].username == "testuser123"
        assert transactions[0].amount == Decimal('50.00')

        # Verify query was called with correct parameters
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}testuser123", limit=50, last_evaluated_key=None)

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_transactions_with_pagination(self, mock_query, balance_dao, sample_transaction):
        """Test user transactions retrieval with pagination"""
        # Mock query to return transactions with pagination
        transaction_item = BalanceTransactionItem(
            username='testuser123',
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id='test_ref_123',
            created_at=sample_transaction.created_at
        )

        # Create a mock query result with last_evaluated_key
        mock_query_result = Mock()
        mock_query_result.__iter__ = Mock(return_value=iter([transaction_item]))
        mock_query_result.last_evaluated_key = {'test': 'key'}
        mock_query.return_value = mock_query_result

        transactions, last_key = balance_dao.get_user_transactions('testuser123', limit=10, start_key={'test': 'key'})

        # Verify result
        assert len(transactions) == 1
        assert last_key == {'test': 'key'}

        # Verify query was called with correct parameters
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}testuser123", limit=10, last_evaluated_key={'test': 'key'})

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_transactions_database_error(self, mock_query, balance_dao):
        """Test user transactions retrieval with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.get_user_transactions('testuser123')

        assert "Database operation failed while retrieving transactions for user 'testuser123'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== CLEANUP TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_cleanup_failed_transaction_success(self, mock_query, balance_dao):
        """Test successful transaction cleanup"""
        # Mock query to return transaction
        transaction_item = Mock()
        transaction_item.transaction_id = '12345678-1234-5678-9012-123456789012'
        transaction_item.delete = Mock()
        mock_query.return_value = [transaction_item]

        balance_dao.cleanup_failed_transaction('testuser123', UUID('12345678-1234-5678-9012-123456789012'))

        # Verify query and delete were called
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}testuser123")
        transaction_item.delete.assert_called_once()

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_cleanup_failed_transaction_not_found(self, mock_query, balance_dao):
        """Test transaction cleanup when transaction not found"""
        # Mock empty query result
        mock_query.return_value = []

        # Should not raise exception, just log warning
        balance_dao.cleanup_failed_transaction('testuser123', UUID('12345678-1234-5678-9012-123456789012'))

        # Verify query was called
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}testuser123")

    @patch.object(BalanceTransactionItem, MockDatabaseMethods.QUERY)
    def test_cleanup_failed_transaction_database_error(self, mock_query, balance_dao):
        """Test transaction cleanup with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.cleanup_failed_transaction('testuser123', UUID('12345678-1234-5678-9012-123456789012'))

        assert "Database operation failed while cleaning up transaction for user 'testuser123'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== UPDATE BALANCE FROM TRANSACTION TESTS ====================

    @patch.object(BalanceDAO, 'get_balance')
    @patch.object(BalanceDAO, 'update_balance')
    def test_update_balance_from_transaction_success(self, mock_update, mock_get, balance_dao, sample_transaction, sample_balance):
        """Test successful balance update from transaction"""
        # Mock get_balance to return current balance
        mock_get.return_value = sample_balance

        # Mock update_balance to return updated balance
        updated_balance = Balance(
            username="testuser123",
            current_balance=Decimal('150.00'),
            created_at=sample_balance.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_update.return_value = updated_balance

        balance_dao._update_balance_from_transaction(sample_transaction)

        # Verify get_balance and update_balance were called
        mock_get.assert_called_once_with('testuser123')
        mock_update.assert_called_once_with('testuser123', Decimal('150.00'))

    @patch.object(BalanceDAO, 'get_balance')
    def test_update_balance_from_transaction_get_balance_failure(self, mock_get, balance_dao, sample_transaction):
        """Test balance update from transaction when get_balance fails"""
        # Mock get_balance to raise exception
        mock_get.side_effect = CNOPBalanceNotFoundException("Balance not found")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao._update_balance_from_transaction(sample_transaction)

        assert "Database operation failed while updating balance from transaction for user 'testuser123'" in str(exc_info.value)
        mock_get.assert_called_once_with('testuser123')