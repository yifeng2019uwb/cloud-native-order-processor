"""
Tests for TransactionManager class.
"""

# Standard library imports
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest

# Local imports
from src.core.utils import lock_manager
from src.core.utils.transaction_manager import (TransactionManager,
                                                TransactionResult)
from src.data.entities.user.balance import Balance, BalanceTransaction
from src.data.entities.user.balance_enums import TransactionStatus, TransactionType
from src.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from src.shared.logging import LogAction, LogField
from src.data.dao.asset.asset_transaction_dao import AssetTransactionDAO
from src.data.dao.inventory.asset_dao import AssetDAO
from src.data.dao.order.order_dao import OrderDAO
from src.data.dao.user.balance_dao import BalanceDAO
from tests.utils.dependency_constants import MODEL_SAVE, MODEL_GET, MODEL_QUERY, DOES_NOT_EXIST
from src.data.dao.user.user_dao import UserDAO
from src.data.entities.order import Order, OrderStatus, OrderType
# Remove duplicate imports - already imported above
from src.data.exceptions import (CNOPDatabaseOperationException,
                                 CNOPLockAcquisitionException)
from src.exceptions import CNOPEntityValidationException
from src.exceptions.shared_exceptions import (CNOPEntityNotFoundException,
                                              CNOPInsufficientBalanceException)


# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test user data
TEST_USERNAME = "testuser123"
TEST_EMAIL = "test@example.com"

# Test asset data
TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"

# Test financial data
TEST_DEPOSIT_AMOUNT_50 = Decimal("50.00")
TEST_WITHDRAWAL_AMOUNT_25 = Decimal("25.00")
TEST_BALANCE_AMOUNT_100 = Decimal("100.00")
TEST_LARGE_AMOUNT_150 = Decimal("150.00")
TEST_BTC_QUANTITY_1_0 = Decimal("1.0")
TEST_BTC_PRICE_50000 = Decimal("50000.00")
TEST_TOTAL_AMOUNT_50000 = Decimal("50000.00")

TEXT_SK_BALANCE = "BALANCE"
TEXT_SK_ORDER = "ORDER"

TEST_LOCK_ID = "test-lock-id"

TEST_CURRENT_TIMESTAMP = datetime.now(timezone.utc)


# Test primary keys - use entity methods directly in tests when needed
# Example: BalanceTransaction.build_pk(TEST_USERNAME)


class TestTransactionManager:
    """Test TransactionManager class"""

    # Define patch paths as class constants
    PATH_ACQUIRE_LOCK = f'{lock_manager.__name__}.acquire_lock'
    PATH_RELEASE_LOCK = f'{lock_manager.__name__}.release_lock'

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
        """Mock transaction for testing (transaction_id is timestamp-based str)."""
        return BalanceTransaction(
            username=TEST_USERNAME,
            transaction_id="20260225132158123456a1b2c3",
            transaction_type=TransactionType.DEPOSIT,
            amount=TEST_DEPOSIT_AMOUNT_50,
            description="Test transaction",
            status=TransactionStatus.COMPLETED,
            reference_id="ref123",
            created_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def mock_balance(self):
        """Mock balance for testing"""
        return Balance(
            username=TEST_USERNAME,
            current_balance=TEST_BALANCE_AMOUNT_100,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def mock_order(self):
        """Mock order for testing"""
        return Order(
            Pk="order_123",
            Sk=TEXT_SK_ORDER,
            order_id="order_123",
            username=TEST_USERNAME,
            order_type=OrderType.MARKET_BUY,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_BTC_QUANTITY_1_0,
            price=TEST_BTC_PRICE_50000,
            total_amount=TEST_TOTAL_AMOUNT_50000,
            status=OrderStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_deposit_funds_success(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test successful deposit operation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock both acquire_lock and release_lock functions
        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock balance update success
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            # Local test variables for this specific test
            test_username = TEST_USERNAME
            test_deposit_amount = TEST_DEPOSIT_AMOUNT_50

            result = await transaction_manager.deposit_funds(test_username, test_deposit_amount)

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == test_deposit_amount
            assert result.balance == mock_balance

    @pytest.mark.asyncio
    async def test_deposit_funds_balance_update_failure(self, transaction_manager, mock_daos):
        """Test deposit operation when balance update fails"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock balance update failure
            balance_dao._update_balance_from_transaction.side_effect = Exception("Balance update failed")
            balance_dao.create_transaction.return_value = MagicMock()

            # Local test variables for this specific test
            test_username = TEST_USERNAME
            test_deposit_amount = TEST_DEPOSIT_AMOUNT_50

            with pytest.raises(CNOPDatabaseOperationException, match="Transaction failed"):
                await transaction_manager.deposit_funds(test_username, test_deposit_amount)

    @pytest.mark.asyncio
    async def test_withdraw_funds_success(self, transaction_manager, mock_daos, mock_balance, mock_transaction):
        """Test successful withdrawal operation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock sufficient balance
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.create_transaction.return_value = mock_transaction

            # Local test variables for this specific test
            test_username = TEST_USERNAME
            test_withdrawal_amount = TEST_WITHDRAWAL_AMOUNT_25

            result = await transaction_manager.withdraw_funds(test_username, test_withdrawal_amount)

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == test_withdrawal_amount
            assert result.balance == mock_balance

    @pytest.mark.asyncio
    async def test_withdraw_funds_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test withdrawal with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock insufficient balance
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.side_effect = CNOPInsufficientBalanceException("Insufficient funds")

            # Local test variables for this specific test
            test_username = TEST_USERNAME
            test_large_amount = TEST_LARGE_AMOUNT_150

            with pytest.raises(CNOPInsufficientBalanceException):
                await transaction_manager.withdraw_funds(test_username, test_large_amount)

    @pytest.mark.asyncio
    async def test_withdraw_funds_user_not_found(self, transaction_manager, mock_daos):
        """Test withdrawal when user is not found"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock user not found
            balance_dao.get_balance.side_effect = CNOPEntityNotFoundException("User not found")

            with pytest.raises(CNOPDatabaseOperationException, match="Withdrawal failed"):
                await transaction_manager.withdraw_funds("nonexistent_user", Decimal('25.00'))

    @pytest.mark.asyncio
    async def test_create_buy_order_with_balance_update_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful buy order creation with balance update"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock successful operations - need sufficient balance for the order
            mock_balance.current_balance = Decimal('100000.00')  # Sufficient balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.return_value = None

            # Local test variables for this specific test
            test_username = TEST_USERNAME
            test_asset_id = TEST_ASSET_ID_BTC
            test_quantity = TEST_BTC_QUANTITY_1_0
            test_price = TEST_BTC_PRICE_50000
            test_total_cost = TEST_TOTAL_AMOUNT_50000

            result = await transaction_manager.create_buy_order_with_balance_update(
                username=test_username,
                asset_id=test_asset_id,
                quantity=test_quantity,
                price=test_price,
                order_type=OrderType.MARKET_BUY,
                total_cost=test_total_cost
            )

            assert result.status == TransactionStatus.COMPLETED
            assert result.transaction_amount == test_total_cost

    @pytest.mark.asyncio
    async def test_create_sell_order_with_balance_update_success(self, transaction_manager, mock_daos, mock_order, mock_transaction):
        """Test successful sell order creation with balance update"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock successful operations
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction

            result = await transaction_manager.create_sell_order_with_balance_update(
                username=TEST_USERNAME,
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
        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock:
            mock_acquire_lock.side_effect = CNOPLockAcquisitionException("Lock acquisition failed")

            with pytest.raises(CNOPDatabaseOperationException, match="Service temporarily unavailable"):
                await transaction_manager.deposit_funds(TEST_USERNAME, Decimal('50.00'))

    @pytest.mark.asyncio
    async def test_lock_release_failure(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test operations when lock release fails"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.side_effect = Exception("Lock release failed")

            # Mock successful operations
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            # When lock release fails, the transaction manager should raise an exception
            with pytest.raises(CNOPDatabaseOperationException, match="Deposit failed: Lock release failed"):
                await transaction_manager.deposit_funds(TEST_USERNAME, Decimal('50.00'))



    @pytest.mark.asyncio
    async def test_complex_transaction_scenario(self, transaction_manager, mock_daos, mock_balance, mock_transaction):
        """Test complex transaction scenario with multiple operations"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
            mock_release_lock.return_value = True

            # Mock successful operations
            balance_dao._update_balance_from_transaction.return_value = None
            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            # Test multiple operations
            deposit_result = await transaction_manager.deposit_funds(TEST_USERNAME, Decimal('100.00'))
            assert deposit_result.status == TransactionStatus.COMPLETED

            # Test withdrawal
            withdraw_result = await transaction_manager.withdraw_funds(TEST_USERNAME, Decimal('25.00'))
            assert withdraw_result.status == TransactionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_error_handling_in_transaction_operations(self, transaction_manager, mock_daos):
        """Test comprehensive error handling in transaction operations"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:

            mock_acquire_lock.return_value = TEST_LOCK_ID
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
                    await transaction_manager.deposit_funds(TEST_USERNAME, Decimal('50.00'))


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
