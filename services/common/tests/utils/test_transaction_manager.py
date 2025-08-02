"""
Tests for Transaction Manager
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID

from src.utils.transaction_manager import SimpleTransactionManager, TransactionResult
from src.utils.lock_manager import UserLock
from src.dao.user import UserDAO, BalanceDAO
from src.dao.order import OrderDAO
from src.dao.inventory import AssetDAO
from src.entities.user import Balance, BalanceTransaction, TransactionType, TransactionStatus
from src.entities.order import Order, OrderStatus, OrderType
from src.exceptions import DatabaseOperationException, EntityNotFoundException, LockAcquisitionException, InsufficientBalanceException
from src.exceptions.shared_exceptions import UserValidationException


class TestTransactionManager:
    """Test TransactionManager class"""

    @pytest.fixture
    def mock_daos(self):
        """Create mock DAOs"""
        user_dao = AsyncMock()
        balance_dao = AsyncMock()
        order_dao = AsyncMock()
        asset_dao = AsyncMock()
        return user_dao, balance_dao, order_dao, asset_dao

    @pytest.fixture
    def transaction_manager(self, mock_daos):
        """Create transaction manager with mock DAOs"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos
        return SimpleTransactionManager(user_dao, balance_dao, order_dao, asset_dao)

    @pytest.fixture
    def mock_transaction(self):
        """Create a mock balance transaction"""
        return BalanceTransaction(
            transaction_id=UUID('87654321-4321-8765-cba9-987654321cba'),
            user_id="testuser123",  # Use string instead of UUID
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal('50.00'),
            description='Test deposit',
            status=TransactionStatus.COMPLETED
        )

    @pytest.fixture
    def mock_balance(self):
        """Create a mock balance"""
        return Balance(
            user_id="testuser123",  # Use string instead of UUID
            current_balance=Decimal('100.00')
        )

    @pytest.fixture
    def mock_order(self):
        """Create a mock order"""
        return Order(
            order_id='test-order-123',
            user_id='testuser123',  # Use string instead of UUID
            order_type=OrderType.MARKET_BUY,
            status=OrderStatus.PENDING,
            asset_id='BTC',
            quantity=Decimal('1.0'),
            order_price=Decimal('50000.00'),
            total_amount=Decimal('50000.00'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            completed_at=None,
            status_history=[]
        )

    @pytest.mark.asyncio
    async def test_deposit_funds_success(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test successful deposit operation"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Mock both acquire_lock and release_lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO responses
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance

            result = await transaction_manager.deposit_funds(
                user_id="testuser123",  # Use valid username instead of UUID
                amount=Decimal("50.00")
            )

            assert result is not None, "Transaction manager method returned None"
            assert result.success is True
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["amount"] == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_deposit_funds_lock_acquisition_failure(self, transaction_manager, mock_daos):
        """Test deposit when lock acquisition fails"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock:
            mock_acquire_lock.side_effect = LockAcquisitionException("Lock failed")

            with pytest.raises(DatabaseOperationException, match="Service temporarily unavailable"):
                await transaction_manager.deposit_funds(
                    user_id="testuser123",  # Use valid username instead of UUID
                    amount=Decimal("50.00")
                )

    @pytest.mark.asyncio
    async def test_deposit_funds_database_error(self, transaction_manager, mock_daos):
        """Test deposit when database operation fails"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.create_transaction.side_effect = Exception("Database error")

            with pytest.raises(DatabaseOperationException, match="Deposit failed"):
                await transaction_manager.deposit_funds(
                    user_id="testuser123",  # Use valid username instead of UUID
                    amount=Decimal("50.00")
                )

    @pytest.mark.asyncio
    async def test_withdraw_funds_success(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test successful withdrawal operation"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Set sufficient balance
        mock_balance.current_balance = Decimal("100.00")

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = mock_balance
            balance_dao.create_transaction.return_value = mock_transaction

            result = await transaction_manager.withdraw_funds(
                user_id="testuser123",  # Use valid username instead of UUID
                amount=Decimal("50.00")
            )

            assert result is not None, "Transaction manager method returned None"
            assert result.success is True
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["amount"] == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_withdraw_funds_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test withdrawal with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Set insufficient balance
        mock_balance.current_balance = Decimal("25.00")

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = mock_balance

            with pytest.raises(InsufficientBalanceException):
                await transaction_manager.withdraw_funds(
                    user_id="testuser123",  # Use valid username instead of UUID
                    amount=Decimal("50.00")
                )

    @pytest.mark.asyncio
    async def test_withdraw_funds_balance_not_found(self, transaction_manager, mock_daos):
        """Test withdrawal when balance not found"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = None

            with pytest.raises(DatabaseOperationException, match="Critical system error"):
                await transaction_manager.withdraw_funds(
                    user_id="testuser123",  # Use valid username instead of UUID
                    amount=Decimal("50.00")
                )

    @pytest.mark.asyncio
    async def test_create_buy_order_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful buy order creation"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Set sufficient balance
        mock_balance.current_balance = Decimal("100000.00")

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = mock_balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction

            order_data = {
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "order_price": Decimal("50000.00")
            }

            result = await transaction_manager.create_buy_order_with_balance_update(
                user_id="testuser123",  # Use valid username instead of UUID
                order_data=order_data,
                total_cost=Decimal("50000.00")
            )

            assert result is not None, "Transaction manager method returned None"
            assert result.success is True
            assert result.data["order"] == mock_order
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["total_cost"] == Decimal("50000.00")

    @pytest.mark.asyncio
    async def test_create_buy_order_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test buy order with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Set insufficient balance
        mock_balance.current_balance = Decimal("25000.00")

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = mock_balance

            order_data = {
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "order_price": Decimal("50000.00")
            }

            with pytest.raises(InsufficientBalanceException):
                await transaction_manager.create_buy_order_with_balance_update(
                    user_id="testuser123",  # Use valid username instead of UUID
                    order_data=order_data,
                    total_cost=Decimal("50000.00")
                )

    @pytest.mark.asyncio
    async def test_create_buy_order_rollback_on_error(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test buy order rollback when error occurs"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        # Set sufficient balance
        mock_balance.current_balance = Decimal("100000.00")

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            balance_dao.get_balance.return_value = mock_balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.side_effect = Exception("Transaction creation failed")

            order_data = {
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "order_price": Decimal("50000.00")
            }

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.create_buy_order_with_balance_update(
                    user_id="testuser123",  # Use valid username instead of UUID
                    order_data=order_data,
                    total_cost=Decimal("50000.00")
                )

    @pytest.mark.asyncio
    async def test_create_sell_order_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful sell order creation"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            # Mock both get_balance calls (initial check and after transaction)
            balance_dao.get_balance.return_value = mock_balance

            order_data = {
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "order_price": Decimal("50000.00")
            }

            result = await transaction_manager.create_sell_order_with_balance_update(
                user_id="testuser123",  # Use valid username instead of UUID
                order_data=order_data,
                asset_amount=Decimal("50000.00")
            )

            assert result is not None, "Transaction manager method returned None"
            assert result.success is True
            assert result.data["order"] == mock_order
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["asset_amount"] == Decimal("50000.00")

    @pytest.mark.asyncio
    async def test_create_sell_order_rollback_on_error(self, transaction_manager, mock_daos, mock_order, mock_transaction):
        """Test sell order rollback when error occurs"""
        user_dao, balance_dao, order_dao, asset_dao = mock_daos

        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.side_effect = Exception("Transaction creation failed")

            order_data = {
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "order_price": Decimal("50000.00")
            }

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.create_sell_order_with_balance_update(
                    user_id="testuser123",  # Use valid username instead of UUID
                    order_data=order_data,
                    asset_amount=Decimal("50000.00")
                )