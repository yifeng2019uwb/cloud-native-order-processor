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
from tests.utils.dependency_constants import (
    MODEL_SAVE, MODEL_GET, MODEL_QUERY, BALANCE_DAO_GET_BALANCE, BALANCE_DAO_UPDATE_BALANCE)


# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test user data
TEST_USERNAME = "testuser123"
TEST_EMAIL = "test@example.com"

# Test financial data
TEST_BALANCE_AMOUNT_100 = Decimal("100.00")
TEST_DEPOSIT_AMOUNT_50 = Decimal("50.00")
TEST_WITHDRAWAL_AMOUNT_25 = Decimal("25.00")
TEST_LARGE_AMOUNT_1000 = Decimal("1000.00")
TEST_SMALL_AMOUNT_0_01 = Decimal("0.01")

# Test transaction data
TEST_REFERENCE_ID = "test_ref_123"
TEST_DESCRIPTION_DEPOSIT = "Test deposit"
TEST_DESCRIPTION_WITHDRAWAL = "Test withdrawal"

# Test transaction status and type
TEST_TRANSACTION_TYPE_DEPOSIT = "DEPOSIT"
TEST_TRANSACTION_TYPE_WITHDRAWAL = "WITHDRAWAL"
TEST_TRANSACTION_STATUS_COMPLETED = "COMPLETED"
TEST_TRANSACTION_STATUS_PENDING = "PENDING"

# Test UUID
TEST_TRANSACTION_ID = "12345678-1234-5678-9012-123456789012"

# Test primary keys - use entity methods directly in tests when needed
# Example: BalanceTransaction.build_pk(TEST_USERNAME)


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
            username=TEST_USERNAME,
            current_balance=TEST_BALANCE_AMOUNT_100,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing"""
        return BalanceTransaction(
            username=TEST_USERNAME,
            transaction_type=TransactionType.DEPOSIT,
            amount=TEST_DEPOSIT_AMOUNT_50,
            description=TEST_DESCRIPTION_DEPOSIT,
            status=TransactionStatus.COMPLETED,
            reference_id=TEST_REFERENCE_ID
        )

    # ==================== GET BALANCE TESTS ====================

    @patch.object(BalanceItem, MODEL_GET)
    def test_get_balance_success(self, mock_get, balance_dao, sample_balance):
        """Test successful balance retrieval"""
        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_balance_amount = TEST_BALANCE_AMOUNT_100

        # Expected values for assertions
        expected_username = test_username
        expected_balance = test_balance_amount

        # Mock BalanceItem.get to return a real BalanceItem
        balance_item = BalanceItem(
            username=test_username,
            current_balance=str(test_balance_amount),
            created_at=sample_balance.created_at,
            updated_at=sample_balance.updated_at
        )
        mock_get.return_value = balance_item

        result = balance_dao.get_balance(test_username)

        # Verify result using expected variables
        assert result is not None
        assert result.username == expected_username
        assert result.current_balance == expected_balance

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with(test_username, BalanceFields.SK_VALUE)

    @patch.object(BalanceItem, MODEL_GET)
    def test_get_balance_not_found(self, mock_get, balance_dao):
        """Test balance retrieval when not found"""
        # Mock BalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = BalanceItem.DoesNotExist()

        # Should raise BalanceNotFoundException
        with pytest.raises(CNOPBalanceNotFoundException) as exc_info:
            balance_dao.get_balance('nonexistent')

        assert "Balance for user 'nonexistent' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent', BalanceFields.SK_VALUE)

    @patch.object(BalanceItem, MODEL_GET)
    def test_get_balance_database_error(self, mock_get, balance_dao):
        """Test balance retrieval with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.get_balance(TEST_USERNAME)

        assert f"Failed to get balance for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_get.assert_called_once_with(TEST_USERNAME, BalanceFields.SK_VALUE)

    # ==================== CREATE BALANCE TESTS ====================

    @patch.object(BalanceItem, MODEL_SAVE)
    def test_create_balance_success(self, mock_save, balance_dao, sample_balance):
        """Test successful balance creation"""
        # Mock save to return None
        mock_save.return_value = None

        result = balance_dao.create_balance(sample_balance)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.current_balance == TEST_BALANCE_AMOUNT_100

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(BalanceItem, MODEL_SAVE)
    def test_create_balance_database_error(self, mock_save, balance_dao, sample_balance):
        """Test balance creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.create_balance(sample_balance)

        assert f"Database operation failed while creating balance for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_save.assert_called_once()

    # ==================== UPDATE BALANCE TESTS ====================

    @patch.object(BalanceItem, MODEL_GET)
    @patch.object(BalanceItem, MODEL_SAVE)
    def test_update_balance_success(self, mock_save, mock_get, balance_dao, sample_balance):
        """Test successful balance update"""
        # Mock BalanceItem.get to return existing balance
        existing_balance_item = BalanceItem(
            username=TEST_USERNAME,
            current_balance=str(TEST_BALANCE_AMOUNT_100),
            created_at=sample_balance.created_at,
            updated_at=sample_balance.updated_at
        )
        mock_get.return_value = existing_balance_item

        # Mock save to return None
        mock_save.return_value = None

        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_new_balance = Decimal('150.00')

        result = balance_dao.update_balance(test_username, test_new_balance)

        # Verify result
        assert result is not None
        assert result.username == test_username
        assert result.current_balance == test_new_balance

        # Verify get and save were called
        mock_get.assert_called_once_with(test_username, BalanceFields.SK_VALUE)
        mock_save.assert_called_once()

    @patch.object(BalanceItem, MODEL_GET)
    def test_update_balance_not_found(self, mock_get, balance_dao):
        """Test balance update when balance not found"""
        # Mock BalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = BalanceItem.DoesNotExist()

        with pytest.raises(CNOPBalanceNotFoundException) as exc_info:
            balance_dao.update_balance('nonexistent', Decimal('150.00'))

        assert "Balance for user 'nonexistent' not found" in str(exc_info.value)
        mock_get.assert_called_once_with('nonexistent', BalanceFields.SK_VALUE)

    # ==================== CREATE TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MODEL_SAVE)
    def test_create_transaction_success(self, mock_save, balance_dao, sample_transaction):
        """Test successful transaction creation"""
        # Mock save to return None
        mock_save.return_value = None

        result = balance_dao.create_transaction(sample_transaction)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.amount == TEST_DEPOSIT_AMOUNT_50
        assert result.transaction_type == TransactionType.DEPOSIT

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(BalanceTransactionItem, MODEL_SAVE)
    def test_create_transaction_database_error(self, mock_save, balance_dao, sample_transaction):
        """Test transaction creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.create_transaction(sample_transaction)

        assert f"Database operation failed while creating transaction for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_save.assert_called_once()

    # ==================== GET TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_get_transaction_success(self, mock_query, balance_dao, sample_transaction):
        """Test successful transaction retrieval"""
        # Mock query to return transaction
        transaction_item = BalanceTransactionItem(
            username=TEST_USERNAME,
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id=TEST_REFERENCE_ID,
            created_at=sample_transaction.created_at
        )
        mock_query.return_value = [transaction_item]

        result = balance_dao.get_transaction(TEST_USERNAME, sample_transaction.transaction_id)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.transaction_id == sample_transaction.transaction_id

        # Verify query was called
        mock_query.assert_called_once()

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_get_transaction_not_found(self, mock_query, balance_dao):
        """Test transaction retrieval when not found"""
        # Mock empty query result
        mock_query.return_value = []

        with pytest.raises(CNOPTransactionNotFoundException) as exc_info:
            balance_dao.get_transaction(TEST_USERNAME, UUID('12345678-1234-5678-9012-123456789012'))

        assert f"Transaction '{TEST_TRANSACTION_ID}' not found for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== GET USER TRANSACTIONS TESTS ====================

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_get_user_transactions_success(self, mock_query, balance_dao, sample_transaction):
        """Test successful user transactions retrieval"""
        # Mock query to return transactions
        transaction_item = BalanceTransactionItem(
            username=TEST_USERNAME,
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id=TEST_REFERENCE_ID,
            created_at=sample_transaction.created_at
        )
        mock_query.return_value = [transaction_item]

        transactions, last_key = balance_dao.get_user_transactions(TEST_USERNAME)

        # Verify result
        assert len(transactions) == 1
        assert transactions[0].username == TEST_USERNAME
        assert transactions[0].amount == TEST_DEPOSIT_AMOUNT_50

        # Verify query was called with correct parameters
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}{TEST_USERNAME}", limit=50, last_evaluated_key=None)

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_get_user_transactions_with_pagination(self, mock_query, balance_dao, sample_transaction):
        """Test user transactions retrieval with pagination"""
        # Mock query to return transactions with pagination
        transaction_item = BalanceTransactionItem(
            username=TEST_USERNAME,
            transaction_id=str(sample_transaction.transaction_id),
            transaction_type=TransactionType.DEPOSIT.value,
            amount='50.00',
            description='Test deposit',
            status=TransactionStatus.COMPLETED.value,
            reference_id=TEST_REFERENCE_ID,
            created_at=sample_transaction.created_at
        )

        # Create a mock query result with last_evaluated_key
        mock_query_result = Mock()
        mock_query_result.__iter__ = Mock(return_value=iter([transaction_item]))
        mock_query_result.last_evaluated_key = {'test': 'key'}
        mock_query.return_value = mock_query_result

        transactions, last_key = balance_dao.get_user_transactions(TEST_USERNAME, limit=10, start_key={'test': 'key'})

        # Verify result
        assert len(transactions) == 1
        assert last_key == {'test': 'key'}

        # Verify query was called with correct parameters
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}{TEST_USERNAME}", limit=10, last_evaluated_key={'test': 'key'})

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_get_user_transactions_database_error(self, mock_query, balance_dao):
        """Test user transactions retrieval with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.get_user_transactions(TEST_USERNAME)

        assert f"Database operation failed while retrieving transactions for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== CLEANUP TRANSACTION TESTS ====================

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_cleanup_failed_transaction_success(self, mock_query, balance_dao):
        """Test successful transaction cleanup"""
        # Mock query to return transaction
        transaction_item = Mock()
        transaction_item.transaction_id = '12345678-1234-5678-9012-123456789012'
        transaction_item.delete = Mock()
        mock_query.return_value = [transaction_item]

        balance_dao.cleanup_failed_transaction(TEST_USERNAME, UUID('12345678-1234-5678-9012-123456789012'))

        # Verify query and delete were called
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}{TEST_USERNAME}")
        transaction_item.delete.assert_called_once()

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_cleanup_failed_transaction_not_found(self, mock_query, balance_dao):
        """Test transaction cleanup when transaction not found"""
        # Mock empty query result
        mock_query.return_value = []

        # Should not raise exception, just log warning
        balance_dao.cleanup_failed_transaction(TEST_USERNAME, UUID('12345678-1234-5678-9012-123456789012'))

        # Verify query was called
        mock_query.assert_called_once_with(f"{TransactionFields.PK_PREFIX}{TEST_USERNAME}")

    @patch.object(BalanceTransactionItem, MODEL_QUERY)
    def test_cleanup_failed_transaction_database_error(self, mock_query, balance_dao):
        """Test transaction cleanup with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao.cleanup_failed_transaction(TEST_USERNAME, UUID('12345678-1234-5678-9012-123456789012'))

        assert f"Database operation failed while cleaning up transaction for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_query.assert_called_once()

    # ==================== UPDATE BALANCE FROM TRANSACTION TESTS ====================

    @patch.object(BalanceDAO, BALANCE_DAO_GET_BALANCE)
    @patch.object(BalanceDAO, BALANCE_DAO_UPDATE_BALANCE)
    def test_update_balance_from_transaction_success(self, mock_update, mock_get, balance_dao, sample_transaction, sample_balance):
        """Test successful balance update from transaction"""
        # Mock get_balance to return current balance
        mock_get.return_value = sample_balance

        # Mock update_balance to return updated balance
        test_username = TEST_USERNAME
        test_updated_balance = Decimal('150.00')

        updated_balance = Balance(
            username=test_username,
            current_balance=test_updated_balance,
            created_at=sample_balance.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        mock_update.return_value = updated_balance

        balance_dao._update_balance_from_transaction(sample_transaction)

        # Verify get_balance and update_balance were called
        mock_get.assert_called_once_with(TEST_USERNAME)
        mock_update.assert_called_once_with(TEST_USERNAME, Decimal('150.00'))

    @patch.object(BalanceDAO, BALANCE_DAO_GET_BALANCE)
    def test_update_balance_from_transaction_get_balance_failure(self, mock_get, balance_dao, sample_transaction):
        """Test balance update from transaction when get_balance fails"""
        # Mock get_balance to raise exception
        mock_get.side_effect = CNOPBalanceNotFoundException("Balance not found")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            balance_dao._update_balance_from_transaction(sample_transaction)

        assert f"Database operation failed while updating balance from transaction for user '{TEST_USERNAME}'" in str(exc_info.value)
        mock_get.assert_called_once_with(TEST_USERNAME)