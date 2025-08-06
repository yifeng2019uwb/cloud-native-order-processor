"""
Tests for TransactionManager class.
"""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID

from src.utils.transaction_manager import TransactionManager
from src.dao.user import UserDAO, BalanceDAO
from src.dao.order import OrderDAO
from src.dao.inventory import AssetDAO
from src.dao.asset import AssetBalanceDAO, AssetTransactionDAO
from src.entities.user import Balance, BalanceTransaction, TransactionType, TransactionStatus
from src.entities.order import Order, OrderStatus, OrderType
from src.exceptions import DatabaseOperationException, EntityNotFoundException, LockAcquisitionException, InsufficientBalanceException
from src.exceptions.shared_exceptions import UserValidationException


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
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO responses
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance

            result = await transaction_manager.deposit_funds(
                username="testuser123",
                amount=Decimal("50.00")
            )

            assert result is not None, "Transaction manager method returned None"
            assert result.success is True
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["amount"] == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_deposit_funds_database_error(self, transaction_manager, mock_daos):
        """Test deposit operation with database error"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO to raise exception
            balance_dao.create_transaction.side_effect = DatabaseOperationException("Database error")

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.deposit_funds(
                    username="testuser123",
                    amount=Decimal("50.00")
                )

    @pytest.mark.asyncio
    async def test_withdraw_funds_success(self, transaction_manager, mock_daos, mock_transaction, mock_balance):
        """Test successful withdraw operation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO responses
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance

            result = await transaction_manager.withdraw_funds(
                username="testuser123",
                amount=Decimal("25.00")
            )

            assert result.success is True
            assert result.data["transaction"] == mock_transaction
            assert result.data["balance"] == mock_balance
            assert result.data["amount"] == Decimal("25.00")

    @pytest.mark.asyncio
    async def test_withdraw_funds_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test withdraw operation with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock balance check
            balance_dao.get_balance.return_value = mock_balance

            with pytest.raises(InsufficientBalanceException):
                await transaction_manager.withdraw_funds(
                    username="testuser123",
                    amount=Decimal("150.00")  # More than available balance
                )

    @pytest.mark.asyncio
    async def test_withdraw_funds_balance_not_found(self, transaction_manager, mock_daos):
        """Test withdraw operation when balance not found"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock balance not found
            balance_dao.get_balance.side_effect = EntityNotFoundException("Balance not found")

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.withdraw_funds(
                    username="testuser123",
                    amount=Decimal("25.00")
                )

    @pytest.mark.asyncio
    async def test_create_buy_order_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful buy order creation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO responses - need sufficient balance
            mock_balance.current_balance = Decimal("100000.00")  # Sufficient balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance

            order_data = {
                "order_type": OrderType.MARKET_BUY,
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "price": Decimal("50000.00")
            }

            result = await transaction_manager.create_buy_order_with_balance_update(
                username="testuser123",
                order_data=order_data,
                total_cost=Decimal("50000.00")
            )

            assert result.success is True
            assert result.data["order"] == mock_order
            assert result.data["transaction"] == mock_transaction

    @pytest.mark.asyncio
    async def test_create_buy_order_insufficient_balance(self, transaction_manager, mock_daos, mock_balance):
        """Test buy order creation with insufficient balance"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock insufficient balance
            balance_dao.get_balance.return_value = mock_balance

            order_data = {
                "order_type": OrderType.MARKET_BUY,
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "price": Decimal("50000.00")
            }

            with pytest.raises(InsufficientBalanceException):
                await transaction_manager.create_buy_order_with_balance_update(
                    username="testuser123",
                    order_data=order_data,
                    total_cost=Decimal("100000.00")  # More than available balance
                )

    @pytest.mark.asyncio
    async def test_create_buy_order_rollback_on_error(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test buy order creation with rollback on error"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock sufficient balance but balance update failure
            mock_balance.current_balance = Decimal("100000.00")  # Sufficient balance
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance
            balance_dao._update_balance_from_transaction.side_effect = DatabaseOperationException("Balance update failed")

            order_data = {
                "order_type": OrderType.MARKET_BUY,
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "price": Decimal("50000.00")
            }

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.create_buy_order_with_balance_update(
                    username="testuser123",
                    order_data=order_data,
                    total_cost=Decimal("50000.00")
                )

    @pytest.mark.asyncio
    async def test_create_sell_order_success(self, transaction_manager, mock_daos, mock_order, mock_transaction, mock_balance):
        """Test successful sell order creation"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock DAO responses
            order_dao.create_order.return_value = mock_order
            balance_dao.create_transaction.return_value = mock_transaction
            balance_dao.get_balance.return_value = mock_balance

            order_data = {
                "order_type": OrderType.MARKET_SELL,
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "price": Decimal("50000.00")
            }

            result = await transaction_manager.create_sell_order_with_balance_update(
                username="testuser123",
                order_data=order_data,
                asset_amount=Decimal("50000.00")  # USD amount from sell
            )

            assert result.success is True
            assert result.data["order"] == mock_order

    @pytest.mark.asyncio
    async def test_create_sell_order_rollback_on_error(self, transaction_manager, mock_daos, mock_order, mock_transaction):
        """Test sell order creation with rollback on error"""
        user_dao, balance_dao, order_dao, asset_dao, asset_balance_dao, asset_transaction_dao = mock_daos

        # Mock lock functions
        with patch('src.utils.lock_manager.acquire_lock') as mock_acquire_lock, \
             patch('src.utils.lock_manager.release_lock') as mock_release_lock:

            mock_acquire_lock.return_value = "test-lock-id"
            mock_release_lock.return_value = True

            # Mock order creation failure
            order_dao.create_order.side_effect = DatabaseOperationException("Order creation failed")

            order_data = {
                "order_type": OrderType.MARKET_SELL,
                "asset_id": "BTC",
                "quantity": Decimal("1.0"),
                "price": Decimal("50000.00")
            }

            with pytest.raises(DatabaseOperationException):
                await transaction_manager.create_sell_order_with_balance_update(
                    username="testuser123",
                    order_data=order_data,
                    asset_amount=Decimal("50000.00")  # USD amount from sell
                )