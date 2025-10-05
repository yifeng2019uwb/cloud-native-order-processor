"""
Tests for TransactionManager class.
"""

# Standard library imports
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

# Third-party imports
import pytest

# Local imports
from src.core.utils import lock_manager
from src.core.utils.transaction_manager import (TransactionManager,
                                                TransactionResult)
from src.data.entities.user.balance import Balance
from src.data.entities.user.balance_enums import TransactionStatus, TransactionType
from src.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from src.data.dao.asset.asset_transaction_dao import AssetTransactionDAO
from src.data.dao.inventory.asset_dao import AssetDAO
from src.data.dao.order.order_dao import OrderDAO
from src.data.dao.user.balance_dao import BalanceDAO
from src.data.dao.user.user_dao import UserDAO
from src.data.entities.order import Order, OrderStatus, OrderType
from src.data.entities.user import (Balance, BalanceTransaction,
                                    TransactionStatus, TransactionType)
from src.data.exceptions import (CNOPDatabaseOperationException,
                                 CNOPLockAcquisitionException)
from src.exceptions import CNOPEntityValidationException
from src.exceptions.shared_exceptions import (CNOPEntityNotFoundException,
                                              CNOPInsufficientBalanceException)



class TestTransactionManager:
    """Test TransactionManager class"""

    @pytest.fixture
    def mock_daos(self):
        """Create mock DAOs"""
        user_dao = MagicMock()
        balance_dao = MagicMock()
        order_dao = MagicMock()
        asset_dao = MagicMock()
        asset_balance_dao = MagicMock()
        asset_transaction_dao = MagicMock()
        return user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao

    @pytest.fixture
    def transaction_manager(self, mock_daos):
        """Create transaction manager with mock DAOs"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos
        return TransactionManager(user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao)

    @pytest.fixture
    def mock_transaction(self):
        """Mock transaction for testing"""
        return BalanceTransaction(
            Pk="TRANS#testuser123",
            username="testuser123",
            Sk="2023-01-01T00:00:00",
            transaction_id=UUID('12345678-1234-5678-9abc-123456789abc'),
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal('50.00'),
            description="Test transaction",
            status=TransactionStatus.COMPLETED,
            reference_id="ref123",
            created_at=datetime.utcnow(),
            entity_type="balance_transaction"
        )

    @pytest.fixture
    def mock_balance(self):
        """Mock balance for testing"""
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
    def mock_order(self):
        """Mock order for testing"""
        return Order(
            Pk="order_123",
            Sk="ORDER",
            order_id="order_123",
            username="testuser123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal('1.0'),
            price=Decimal('50000.00'),
            total_amount=Decimal('50000.00'),
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_deposit_funds_success(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test successful deposit operation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock both acquire_lock and release_lock functions
        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock balance update success
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            result = await transaction_manager.deposit_funds("testuser123", Decimal('50.00'))

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == Decimal('50.00')
            assert result.balance == mock_balance

    @pytest.mark.asyncio
    async def test_deposit_funds_balance_update_failure(self, transaction_manager, mock_daos):
        """Test deposit operation when balance update fails"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock balance update failure
            balance_dao._update_balance_from_transaction.side_effect = Exception("Balance update failed")
            balance_dao.create_transaction.return_value = MagicMock()

            with pytest.raises(CNOPDatabaseOperationException, match="Transaction failed"):
                await transaction_manager.deposit_funds("testuser123", Decimal('50.00'))

    @pytest.mark.asyncio
    async def test_withdraw_funds_success(self, transaction_manager, mock_daos, mock_balance, mock_transaction):
        """Test successful withdrawal operation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock sufficient balance
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.create_transaction.return_value = mock_transaction

            result = await transaction_manager.withdraw_funds("testuser123", Decimal('25.00'))

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == Decimal('25.00')
            assert result.balance == mock_balance

    @pytest.mark.asyncio
    async def test_withdraw_funds_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test withdrawal with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock insufficient balance
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.side_effect = CNOPInsufficientBalanceException("Insufficient funds")

            with pytest.raises(CNOPInsufficientBalanceException):
                await transaction_manager.withdraw_funds("testuser123", Decimal('150.00'))

    @pytest.mark.asyncio
    async def test_withdraw_funds_user_not_found(self, transaction_manager, mock_daos):
        """Test withdrawal when user is not found"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock user not found
            balance_dao.get_balance.side_effect = CNOPEntityNotFoundException("User not found")

            with pytest.raises(CNOPDatabaseOperationException, match="Withdrawal failed"):
                await transaction_manager.withdraw_funds("nonexistent_user", Decimal('25.00'))

    @pytest.mark.asyncio
    async def test_create_buy_order_with_balance_update_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful buy order creation with balance update"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock successful operations - need sufficient balance for the order
            mock_balance.current_balance = Decimal('100000.00')  # Sufficient balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.return_value = None

            result = await transaction_manager.create_buy_order_with_balance_update(
                username="testuser123",
                asset_id="BTC",
                quantity=Decimal('1.0'),
                price=Decimal('50000.00'),
                order_type=OrderType.MARKET_BUY,
                total_cost=Decimal('50000.00')
            )

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == Decimal('50000.00')

    @pytest.mark.asyncio
    async def test_create_sell_order_with_balance_update_success(self, transaction_manager, mock_daos, mock_order, mock_transaction):
        """Test successful sell order creation with balance update"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock successful operations
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction

            result = await transaction_manager.create_sell_order_with_balance_update(
                username="testuser123",
                asset_id="BTC",
                quantity=Decimal('1.0'),
                price=Decimal('500.00'),
                order_type=OrderType.MARKET_SELL,
                asset_amount=Decimal('5000.00')  # USD amount from sell
            )

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == Decimal('2500000.00')  # asset_amount * price = 50000 * 50000

    @pytest.mark.asyncio
    async def test_lock_acquisition_failure(self, transaction_manager, mock_daos):
        """Test operations when lock acquisition fails"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        with patch(path_acquire_lock) as mock_acquire_lock:
            mock_acquire_lock.side_effect = CNOPLockAcquisitionException("Lock acquisition failed")

            with pytest.raises(CNOPDatabaseOperationException, match="Service temporarily unavailable"):
                await transaction_manager.deposit_funds("testuser123", Decimal('50.00'))

    @pytest.mark.asyncio
    async def test_lock_release_failure(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test operations when lock release fails"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.side_effect = Exception("Lock release failed")

            # Mock successful operations
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            # When lock release fails, the transaction manager should raise an exception
            with pytest.raises(CNOPDatabaseOperationException, match="Deposit failed: Lock release failed"):
                await transaction_manager.deposit_funds("testuser123", Decimal('50.00'))



    @pytest.mark.asyncio
    async def test_complex_transaction_scenario(self, transaction_manager, mock_daos, mock_balance, mock_transaction):
        """Test complex transaction scenario with multiple operations"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock successful operations
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            # Test multiple operations
            deposit_result = await transaction_manager.deposit_funds("testuser123", Decimal('100.00'))
            assert deposit_result.status == TransactionStatus.COMPLETED

            # Test withdrawal
            withdraw_result = await transaction_manager.withdraw_funds("testuser123", Decimal('25.00'))
            assert withdraw_result.status == TransactionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_error_handling_in_transaction_operations(self, transaction_manager, mock_daos):
        """Test comprehensive error handling in transaction operations"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        path_acquire_lock = f'{lock_manager.__name__}.acquire_lock'
        path_release_lock = f'{lock_manager.__name__}.release_lock'
        with patch(path_acquire_lock) as mock_acquire_lock, \
             patch(path_release_lock) as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Test various error conditions
            test_cases = [
                (CNOPDatabaseOperationException("Database error"), "Transaction failed"),
                (CNOPEntityValidationException("Validation error"), "Transaction failed"),
                (Exception("Unknown error"), "Transaction failed")
            ]

            for exception, expected_message in test_cases:
                balance_dao._update_balance_from_transaction.side_effect = exception
                balance_dao.create_transaction.return_value = MagicMock()

                with pytest.raises(CNOPDatabaseOperationException, match=expected_message):
                    await transaction_manager.deposit_funds("testuser123", Decimal('50.00'))


class TestTransactionResult:
    """Test TransactionResult class"""

    def test_transaction_result_creation(self):
        """Test TransactionResult creation with all parameters"""
        result = TransactionResult(
            status=TransactionStatus.COMPLETED,
            transaction_type=TransactionType.DEPOSIT,
            transaction_amount=Decimal("100.00"),
            balance=Balance(username="test", current_balance=Decimal("100.00"))
        )

        assert result.status == TransactionStatus.COMPLETED
        assert result.transaction_type == TransactionType.DEPOSIT
        assert result.transaction_amount == Decimal("100.00")
        assert result.balance.current_balance == Decimal("100.00")

    def test_transaction_result_defaults(self):
        """Test TransactionResult creation with defaults"""
        result = TransactionResult(
            status=TransactionStatus.FAILED,
            transaction_type=TransactionType.DEPOSIT,
            transaction_amount=Decimal("0.00"),
            balance=Balance(username="test", current_balance=Decimal("0.00")),
            error="Test error"
        )

        assert result.status == TransactionStatus.FAILED
        assert result.transaction_type == TransactionType.DEPOSIT
        assert result.transaction_amount == Decimal("0.00")
        assert result.error == "Test error"
