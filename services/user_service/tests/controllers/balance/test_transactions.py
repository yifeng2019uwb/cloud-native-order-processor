"""
Tests for transactions controller
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.balance.transactions import get_user_transactions, router
from src.api_models.balance.balance_models import TransactionListResponse, TransactionResponse
from common.data.entities.user import UserResponse, BalanceTransaction
from common.data.entities.user.balance_enums import TransactionType, TransactionStatus

from common.exceptions.shared_exceptions import CNOPInternalServerException


class TestGetUserTransactions:
    """Test cases for get_user_transactions function"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        user = Mock(spec=UserResponse)
        user.username = "testuser123"
        return user

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO"""
        dao = Mock()
        return dao

    @pytest.fixture
    def sample_transactions(self):
        """Sample transaction data"""

        transactions = [
            Mock(spec=BalanceTransaction),
            Mock(spec=BalanceTransaction),
            Mock(spec=BalanceTransaction)
        ]

        # Configure first transaction
        transactions[0].transaction_id = "txn_001"
        transactions[0].transaction_type = TransactionType.DEPOSIT
        transactions[0].amount = Decimal('100.00')
        transactions[0].status = TransactionStatus.COMPLETED
        transactions[0].created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Configure second transaction
        transactions[1].transaction_id = "txn_002"
        transactions[1].transaction_type = TransactionType.WITHDRAW
        transactions[1].amount = Decimal('50.00')
        transactions[1].status = TransactionStatus.COMPLETED
        transactions[1].created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

        # Configure third transaction
        transactions[2].transaction_id = "txn_003"
        transactions[2].transaction_type = TransactionType.DEPOSIT
        transactions[2].amount = Decimal('75.00')
        transactions[2].status = TransactionStatus.PENDING
        transactions[2].created_at = datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc)

        return transactions

    def test_get_transactions_success(self, mock_current_user, mock_balance_dao, sample_transactions):
        """Test successful retrieval of transactions"""
        mock_balance_dao.get_user_transactions.return_value = (sample_transactions, 3)

        result = get_user_transactions(
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert len(result.transactions) == 3
        assert result.total_count == 3

        # Verify first transaction
        assert result.transactions[0].transaction_id == "txn_001"
        assert result.transactions[0].transaction_type == "deposit"
        assert result.transactions[0].amount == Decimal('100.00')
        assert result.transactions[0].status == "completed"
        assert result.transactions[0].created_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Verify second transaction
        assert result.transactions[1].transaction_id == "txn_002"
        assert result.transactions[1].transaction_type == "withdraw"
        assert result.transactions[1].amount == Decimal('50.00')
        assert result.transactions[1].status == "completed"

        # Verify third transaction
        assert result.transactions[2].transaction_id == "txn_003"
        assert result.transactions[2].transaction_type == "deposit"
        assert result.transactions[2].amount == Decimal('75.00')
        assert result.transactions[2].status == "pending"

        mock_balance_dao.get_user_transactions.assert_called_once_with("testuser123")

    def test_get_transactions_empty_list(self, mock_current_user, mock_balance_dao):
        """Test retrieval when user has no transactions"""
        mock_balance_dao.get_user_transactions.return_value = (None, 0)

        result = get_user_transactions(
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert len(result.transactions) == 0
        assert result.total_count == 0

    def test_get_transactions_empty_list_from_dao(self, mock_current_user, mock_balance_dao):
        """Test retrieval when DAO returns empty list"""
        mock_balance_dao.get_user_transactions.return_value = ([], 0)

        result = get_user_transactions(
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert len(result.transactions) == 0
        assert result.total_count == 0

    def test_get_transactions_exception_handling(self, mock_current_user, mock_balance_dao):
        """Test exception handling during transaction retrieval"""
        mock_balance_dao.get_user_transactions.side_effect = Exception("Database error")

        with pytest.raises(CNOPInternalServerException, match="Failed to get transactions: Database error"):
            get_user_transactions(
                current_user=mock_current_user,
                balance_dao=mock_balance_dao
            )

    def test_get_transactions_single_transaction(self, mock_current_user, mock_balance_dao):
        """Test retrieval of single transaction"""

        single_transaction = Mock(spec=BalanceTransaction)
        single_transaction.transaction_id = "txn_single"
        single_transaction.transaction_type = TransactionType.DEPOSIT
        single_transaction.amount = Decimal('25.00')
        single_transaction.status = TransactionStatus.COMPLETED
        single_transaction.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_user_transactions.return_value = ([single_transaction], 1)

        result = get_user_transactions(
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert len(result.transactions) == 1
        assert result.total_count == 1
        assert result.transactions[0].transaction_id == "txn_single"

    def test_get_transactions_large_list(self, mock_current_user, mock_balance_dao):
        """Test retrieval of large transaction list"""

        # Create 10 transactions
        large_transactions = []
        for i in range(10):
            transaction = Mock(spec=BalanceTransaction)
            transaction.transaction_id = f"txn_{i:03d}"
            transaction.transaction_type = TransactionType.DEPOSIT if i % 2 == 0 else TransactionType.WITHDRAW
            transaction.amount = Decimal(f'{10.00 + i}')
            transaction.status = TransactionStatus.COMPLETED
            transaction.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            large_transactions.append(transaction)

        mock_balance_dao.get_user_transactions.return_value = (large_transactions, 10)

        result = get_user_transactions(
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert len(result.transactions) == 10
        assert result.total_count == 10

        # Verify all transactions are properly converted
        for i, transaction in enumerate(result.transactions):
            assert transaction.transaction_id == f"txn_{i:03d}"
            assert transaction.amount == Decimal(f'{10.00 + i}')


class TestTransactionsRouter:
    """Test cases for transactions router configuration"""

    def test_router_tags(self):
        """Test router tags configuration"""
        assert router.tags == ["balance"]

    def test_router_endpoint_path(self):
        """Test router endpoint path"""
        assert router.routes[0].path == "/balance/transactions"

    def test_router_response_models(self):
        """Test router response models"""
        route = router.routes[0]
        assert route.response_model is not None

    def test_router_responses_documentation(self):
        """Test router responses documentation"""
        route = router.routes[0]
        assert route.responses is not None
        assert 200 in route.responses
        assert 401 in route.responses
        assert 404 in route.responses
        assert 503 in route.responses
