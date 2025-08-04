"""
Transaction Manager for Atomic Operations
Orchestrates complex transactions with proper locking for order and balance operations.
"""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional

from .lock_manager import UserLock, LOCK_TIMEOUTS
from ..dao.user import UserDAO, BalanceDAO
from ..dao.order import OrderDAO
from ..dao.inventory import AssetDAO
from ..entities.user import BalanceTransaction, TransactionType, TransactionStatus
from ..entities.order import Order, OrderStatus, OrderType
from ..exceptions import DatabaseOperationException, EntityNotFoundException, LockAcquisitionException, InsufficientBalanceException
from ..exceptions.shared_exceptions import UserValidationException

logger = logging.getLogger(__name__)


class TransactionResult:
    """Standardized result for transaction operations"""

    def __init__(self, success: bool, data: Optional[Dict] = None, error: Optional[str] = None, lock_duration: Optional[float] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.lock_duration = lock_duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "lock_duration": self.lock_duration
        }


class SimpleTransactionManager:
    """
    Simple transaction manager for personal project.
    Handles order and balance operations atomically with proper locking.
    """

    def __init__(self, user_dao: UserDAO, balance_dao: BalanceDAO, order_dao: OrderDAO, asset_dao: AssetDAO):
        self.user_dao = user_dao
        self.balance_dao = balance_dao
        self.order_dao = order_dao
        self.asset_dao = asset_dao

    async def deposit_funds(self, user_id: str, amount: Decimal) -> TransactionResult:
        """
        Deposit funds to user account with proper locking.

        Args:
            user_id: User ID (username)
            amount: Amount to deposit

        Returns:
            TransactionResult with deposit information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "deposit", LOCK_TIMEOUTS["deposit"]):
                # Create deposit transaction
                transaction = BalanceTransaction(
                    Pk=f"TRANS#{user_id}",
                    username=user_id,
                    Sk=datetime.utcnow().isoformat(),
                    transaction_type=TransactionType.DEPOSIT,
                    amount=amount,
                    description="Deposit",
                    status=TransactionStatus.COMPLETED,
                    entity_type="balance_transaction"
                )

                # Create transaction record
                created_transaction = self.balance_dao.create_transaction(transaction)

                # Update balance separately
                # Note: Balance records are created during user registration, so they should always exist
                try:
                    self.balance_dao._update_balance_from_transaction(created_transaction)
                except Exception as e:
                    # If balance update fails, clean up the transaction record to maintain consistency
                    logger.error(f"Balance update failed, cleaning up transaction: user={user_id}, error={str(e)}")
                    # TODO: Implement transaction cleanup method in balance_dao
                    raise DatabaseOperationException(f"Transaction failed: {str(e)}")

                # Get updated balance
                balance = self.balance_dao.get_balance(user_id)  # Use username directly

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Deposit successful: user={user_id}, amount={amount}, lock_duration={lock_duration}s")

                return TransactionResult(
                    success=True,
                    data={
                        "transaction": created_transaction,
                        "balance": balance,
                        "amount": amount
                    },
                    lock_duration=lock_duration
                )

        except LockAcquisitionException as e:
            logger.warning(f"Lock acquisition failed for deposit: user={user_id}, error={str(e)}")
            raise DatabaseOperationException("Service temporarily unavailable")
        except Exception as e:
            logger.error(f"Deposit failed: user={user_id}, amount={amount}, error={str(e)}")
            raise DatabaseOperationException(f"Deposit failed: {str(e)}")

    async def withdraw_funds(self, user_id: str, amount: Decimal) -> TransactionResult:
        """
        Withdraw funds from user account with proper locking.

        Args:
            user_id: User ID (username)
            amount: Amount to withdraw

        Returns:
            TransactionResult with withdrawal information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "withdraw", LOCK_TIMEOUTS["withdraw"]):
                # Check balance first
                balance = self.balance_dao.get_balance(user_id)  # Use username directly
                if not balance:
                    # CRITICAL: This should NEVER happen - balance is created during user registration
                    # If this occurs, it indicates a serious system issue (database corruption, race condition, or bug)
                    logger.critical(f"CRITICAL SYSTEM ERROR: User balance missing for user {user_id}. "
                                  f"This should NEVER happen as balance is created during user registration.")
                    raise DatabaseOperationException(
                        f"Critical system error: User balance missing for user {user_id}. "
                        f"This indicates a serious system issue. Please contact support immediately."
                    )

                if balance.current_balance < amount:
                    shortfall = amount - balance.current_balance
                    raise InsufficientBalanceException(
                        f"Insufficient balance for withdrawal. "
                        f"Current balance: ${balance.current_balance:.2f}, "
                        f"Required amount: ${amount:.2f}, "
                        f"Shortfall: ${shortfall:.2f}. "
                        f"Please deposit additional funds or reduce withdrawal amount."
                    )

                # Create withdrawal transaction
                transaction = BalanceTransaction(
                    Pk=f"TRANS#{user_id}",
                    username=user_id,
                    Sk=datetime.utcnow().isoformat(),
                    transaction_type=TransactionType.WITHDRAW,  # Use WITHDRAW not WITHDRAWAL
                    amount=-amount,  # Negative for withdrawal
                    description="Withdrawal",
                    status=TransactionStatus.COMPLETED,
                    entity_type="balance_transaction"
                )

                # Create transaction record
                created_transaction = self.balance_dao.create_transaction(transaction)

                # Update balance separately
                # Note: Balance records are created during user registration, so they should always exist
                try:
                    self.balance_dao._update_balance_from_transaction(created_transaction)
                except Exception as e:
                    # If balance update fails, clean up the transaction record to maintain consistency
                    logger.error(f"Balance update failed, cleaning up transaction: user={user_id}, error={str(e)}")
                    # TODO: Implement transaction cleanup method in balance_dao
                    raise DatabaseOperationException(f"Transaction failed: {str(e)}")

                # Get updated balance
                updated_balance = self.balance_dao.get_balance(user_id)  # Use username directly

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Withdrawal successful: user={user_id}, amount={amount}, lock_duration={lock_duration}s")

                return TransactionResult(
                    success=True,
                    data={
                        "transaction": created_transaction,
                        "balance": updated_balance,
                        "amount": amount
                    },
                    lock_duration=lock_duration
                )

        except LockAcquisitionException as e:
            logger.warning(f"Lock acquisition failed for withdrawal: user={user_id}, error={str(e)}")
            raise DatabaseOperationException("Service temporarily unavailable")
        except InsufficientBalanceException:
            # Re-raise InsufficientBalanceException directly
            raise
        except Exception as e:
            logger.error(f"Withdrawal failed: user={user_id}, amount={amount}, error={str(e)}")
            raise DatabaseOperationException(f"Withdrawal failed: {str(e)}")

    async def create_buy_order_with_balance_update(
        self,
        user_id: str,
        order_data: Dict[str, Any],
        total_cost: Decimal
    ) -> TransactionResult:
        """
        Create a buy order with atomic balance update.

        Args:
            user_id: User ID (username)
            order_data: Order data (asset_id, quantity, order_price)
            total_cost: Total cost of the order

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "buy_order", LOCK_TIMEOUTS["buy_order"]):
                # Phase 1: Validate prerequisites
                balance = self.balance_dao.get_balance(user_id)  # Use username directly
                if not balance:
                    # CRITICAL: This should NEVER happen - balance is created during user registration
                    # If this occurs, it indicates a serious system issue (database corruption, race condition, or bug)
                    logger.critical(f"CRITICAL SYSTEM ERROR: User balance missing for user {user_id}. "
                                  f"This should NEVER happen as balance is created during user registration.")
                    raise DatabaseOperationException(
                        f"Critical system error: User balance missing for user {user_id}. "
                        f"This indicates a serious system issue. Please contact support immediately."
                    )

                if balance.current_balance < total_cost:
                    shortfall = total_cost - balance.current_balance
                    raise InsufficientBalanceException(
                        f"Insufficient balance for buy order. "
                        f"Current balance: ${balance.current_balance:.2f}, "
                        f"Order cost: ${total_cost:.2f}, "
                        f"Asset: {order_data.get('asset_id', 'Unknown')}, "
                        f"Quantity: {order_data.get('quantity', 'Unknown')}, "
                        f"Shortfall: ${shortfall:.2f}. "
                        f"Please deposit additional funds or reduce order quantity."
                    )

                # Phase 2: Create order
                now = datetime.now(timezone.utc)
                order = Order(
                    order_id=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    user_id=user_id,  # Use username directly, no UUID conversion
                    order_type=OrderType.MARKET_BUY,
                    asset_id=order_data["asset_id"],
                    quantity=order_data["quantity"],
                    order_price=order_data["order_price"],
                    total_amount=total_cost,
                    status=OrderStatus.PENDING,
                    created_at=now,
                    updated_at=now
                )

                created_order = self.order_dao.create_order(order)

                # Phase 3: Create balance transaction
                now_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
                transaction = BalanceTransaction(
                    Pk=f"TRANS#{user_id}",
                    username=user_id,
                    Sk=now_timestamp,
                    transaction_type=TransactionType.ORDER_PAYMENT,
                    amount=-total_cost,  # Negative for payment
                    description=f"Payment for buy order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=created_order.order_id
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                # Update balance separately
                self.balance_dao._update_balance_from_transaction(created_transaction)

                # Get updated balance
                updated_balance = self.balance_dao.get_balance(user_id)  # Use username directly

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Buy order created successfully: user={user_id}, order_id={created_order.order_id}, "
                           f"total_cost={total_cost}, lock_duration={lock_duration}s")

                return TransactionResult(
                    success=True,
                    data={
                        "order": created_order,
                        "transaction": created_transaction,
                        "balance": updated_balance,
                        "total_cost": total_cost
                    },
                    lock_duration=lock_duration
                )

        except LockAcquisitionException as e:
            logger.warning(f"Lock acquisition failed for buy order: user={user_id}, error={str(e)}")
            raise DatabaseOperationException("Service temporarily unavailable")
        except InsufficientBalanceException:
            # Re-raise InsufficientBalanceException directly
            raise
        except Exception as e:
            logger.error(f"Buy order creation failed: user={user_id}, error={str(e)}")
            raise DatabaseOperationException(f"Order creation failed: {str(e)}")

    async def create_sell_order_with_balance_update(
        self,
        user_id: str,
        order_data: Dict[str, Any],
        asset_amount: Decimal
    ) -> TransactionResult:
        """
        Create a sell order with atomic balance update.

        Args:
            user_id: User ID (username)
            order_data: Order data (asset_id, quantity, order_price)
            asset_amount: Total amount from the sell order

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "sell_order", LOCK_TIMEOUTS["sell_order"]):
                # Phase 2: Create order
                now = datetime.now(timezone.utc)
                order = Order(
                    order_id=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    user_id=user_id,  # Use username directly, no UUID conversion
                    order_type=OrderType.MARKET_SELL,
                    asset_id=order_data["asset_id"],
                    quantity=order_data["quantity"],
                    order_price=order_data["order_price"],
                    total_amount=asset_amount,
                    status=OrderStatus.PENDING,
                    created_at=now,
                    updated_at=now
                )

                created_order = self.order_dao.create_order(order)

                # Phase 3: Create balance transaction
                now_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
                transaction = BalanceTransaction(
                    Pk=f"TRANS#{user_id}",
                    username=user_id,
                    Sk=now_timestamp,
                    transaction_type=TransactionType.DEPOSIT,  # Use DEPOSIT for sell order receipt
                    amount=asset_amount,  # Positive for receipt
                    description=f"Receipt for sell order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=created_order.order_id
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                # Update balance separately
                self.balance_dao._update_balance_from_transaction(created_transaction)

                # Get updated balance
                updated_balance = self.balance_dao.get_balance(user_id)  # Use username directly

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Sell order created successfully: user={user_id}, order_id={created_order.order_id}, "
                           f"asset_amount={asset_amount}, lock_duration={lock_duration}s")

                return TransactionResult(
                    success=True,
                    data={
                        "order": created_order,
                        "transaction": created_transaction,
                        "balance": updated_balance,
                        "asset_amount": asset_amount
                    },
                    lock_duration=lock_duration
                )

        except LockAcquisitionException as e:
            logger.warning(f"Lock acquisition failed for sell order: user={user_id}, error={str(e)}")
            raise DatabaseOperationException("Service temporarily unavailable")
        except Exception as e:
            logger.error(f"Sell order creation failed: user={user_id}, error={str(e)}")
            raise DatabaseOperationException(f"Order creation failed: {str(e)}")