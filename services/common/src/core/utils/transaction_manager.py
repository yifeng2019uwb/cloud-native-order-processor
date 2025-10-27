"""
Transaction Manager for database operations.

Provides centralized transaction management with rollback support
and proper error handling for all database operations.
"""

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from enum import Enum

from ...data.entities.asset import AssetTransaction, AssetTransactionType, AssetBalance
from ...data.entities.order import Order, OrderStatus, OrderType
from ...data.entities.entity_constants import OrderFields
from ...data.entities.user import (BalanceTransaction, TransactionStatus,
                                   TransactionType, Balance)
from ...data.entities.entity_constants import TransactionFields
from ...data.exceptions import (CNOPDatabaseOperationException,
                                CNOPLockAcquisitionException)
from ...exceptions.shared_exceptions import CNOPInsufficientBalanceException
from ...shared.logging import BaseLogger, LogAction, LoggerName, LogField, LogDefault
from .lock_manager import LockType, UserLock

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class TransactionResult:
    """Unified result for all transaction operations"""

    def __init__(
        self,
        status: TransactionStatus,
        transaction_type: TransactionType,
        transaction_amount: Decimal,  # The amount involved in the transaction
        balance: Balance,  # Final balance after transaction
        # Asset-related fields (Required for orders, None for deposit/withdraw)
        asset_id: Optional[str] = None,
        asset_quantity: Optional[Decimal] = None,  # Asset quantity involved
        asset_balance: Optional[AssetBalance] = None,  # Final asset balance
        # Order information (Required for order operations, None for deposit/withdraw)
        order: Optional[Order] = None,
        # Transaction information (Required for deposit/withdraw, None for orders)
        transaction: Optional[BalanceTransaction] = None,
        # Error details (Only when status is FAILED)
        error: Optional[str] = None
    ):
        self.status = status
        self.transaction_type = transaction_type
        self.transaction_amount = transaction_amount
        self.balance = balance

        # Asset-related (Required for orders, None for deposit/withdraw)
        self.asset_id = asset_id
        self.asset_quantity = asset_quantity
        self.asset_balance = asset_balance

        # Order information (Required for order operations, None for deposit/withdraw)
        self.order = order

        # Transaction information (Required for deposit/withdraw, None for orders)
        self.transaction = transaction

        # Error details (Only when status is FAILED)
        self.error = error


class TransactionManager:
    """
    Simple transaction manager for personal project.
    Handles order and balance operations atomically with proper locking.
    """

    def __init__(self, user_dao, balance_dao, order_dao, asset_dao,
                 asset_balance_dao, asset_transaction_dao):
        self.user_dao = user_dao
        self.balance_dao = balance_dao
        self.order_dao = order_dao
        self.asset_dao = asset_dao
        self.asset_balance_dao = asset_balance_dao
        self.asset_transaction_dao = asset_transaction_dao

    async def deposit_funds(self, username: str, amount: Decimal) -> TransactionResult:
        """
        Deposit funds to user account with proper locking.

        Args:
            username: Username
            amount: Amount to deposit

        Returns:
            TransactionResult with deposit information
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Log transaction start
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Deposit transaction started for user {username}",
                user=username
            )

            async with UserLock(username, LockType.DEPOSIT):
                # Log lock acquisition
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Lock acquired for deposit operation: user={username}",
                    user=username
                )

                transaction = BalanceTransaction(
                    Pk=f"{TransactionFields.PK_PREFIX}{username}",
                    username=username,
                    Sk=datetime.now(timezone.utc).isoformat(),
                    transaction_type=TransactionType.DEPOSIT,
                    amount=amount,
                    description="deposit",
                    status=TransactionStatus.COMPLETED,
                    entity_type=TransactionFields.DEFAULT_ENTITY_TYPE
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                try:
                    self.balance_dao._update_balance_from_transaction(created_transaction)
                    # Log balance update success
                    logger.info(
                        action=LogAction.DB_OPERATION,
                        message=f"Balance updated successfully for user {username}",
                        user=username
                    )
                except Exception as e:
                    logger.error(
                        action=LogAction.ERROR,
                        message=f"Balance update failed, cleaning up transaction: user={username}, error={str(e)}",
                        user=username
                    )
                    self.balance_dao.cleanup_failed_transaction(username, created_transaction.transaction_id)
                    raise CNOPDatabaseOperationException(f"Transaction failed: {str(e)}")

                balance = self.balance_dao.get_balance(username)
                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                # Log successful completion
                logger.info(
                    action=LogAction.DEPOSIT_SUCCESS,
                    message=f"Deposit completed successfully: user={username}, amount={amount}, new_balance={balance.current_balance}",
                    user=username
                )

                return TransactionResult(
                    status=TransactionStatus.COMPLETED,
                    transaction_type=TransactionType.DEPOSIT,
                    transaction_amount=amount,
                    balance=balance,
                    transaction=created_transaction
                )

        except CNOPLockAcquisitionException as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Lock acquisition failed for deposit: user={username}, error={str(e)}",
                user=username
            )
            raise CNOPDatabaseOperationException("Service temporarily unavailable")
        except Exception as e:
            logger.error(
                action=LogAction.DEPOSIT_FAILED,
                message=f"Deposit failed: user={username}, amount={amount}, error={str(e)}",
                user=username
            )
            raise CNOPDatabaseOperationException(f"Deposit failed: {str(e)}")

    async def withdraw_funds(self, username: str, amount: Decimal) -> TransactionResult:
        """
        Withdraw funds from user account with proper locking.

        Args:
            username: Username
            amount: Amount to withdraw

        Returns:
            TransactionResult with withdrawal information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(username, LockType.WITHDRAW):
                balance = self.balance_dao.get_balance(username)
                if not balance:
                    logger.critical(f"CRITICAL SYSTEM ERROR: User balance missing for user {username}. "
                                  f"This should NEVER happen as balance is created during user registration.")
                    raise CNOPDatabaseOperationException(
                        f"Critical system error: User balance missing for user {username}. "
                        f"This indicates a serious system issue. Please contact support immediately."
                    )

                if balance.current_balance < amount:
                    shortfall = amount - balance.current_balance
                    raise CNOPInsufficientBalanceException(
                        f"Insufficient balance for withdrawal. "
                        f"Current balance: ${balance.current_balance:.2f}, "
                        f"Required amount: ${amount:.2f}, "
                        f"Shortfall: ${shortfall:.2f}. "
                        f"Please deposit additional funds or reduce withdrawal amount."
                    )

                transaction = BalanceTransaction(
                    Pk=f"{TransactionFields.PK_PREFIX}{username}",
                    username=username,
                    Sk=datetime.now(timezone.utc).isoformat(),
                    transaction_type=TransactionType.WITHDRAW,
                    amount=-amount,
                    description="Withdrawal",
                    status=TransactionStatus.COMPLETED,
                    entity_type=TransactionFields.DEFAULT_ENTITY_TYPE
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                try:
                    self.balance_dao._update_balance_from_transaction(created_transaction)
                except Exception as e:
                    # If balance update fails, clean up the transaction record to maintain consistency
                    logger.error(
                action=LogAction.ERROR,
                message=f"Balance update failed, cleaning up transaction: user={username}, error={str(e)}"
            )
                    # Clean up the failed transaction
                    self.balance_dao.cleanup_failed_transaction(username, created_transaction.transaction_id)
                    raise CNOPDatabaseOperationException(f"Transaction failed: {str(e)}")

                updated_balance = self.balance_dao.get_balance(username)

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Withdrawal successful: user={username}, amount={amount}, lock_duration={lock_duration}s"
            )

                return TransactionResult(
                    status=TransactionStatus.COMPLETED,
                    transaction_type=TransactionType.WITHDRAW,
                    transaction_amount=amount,
                    balance=updated_balance,
                    transaction=created_transaction
                )

        except CNOPLockAcquisitionException as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Lock acquisition failed for withdrawal: user={username}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException("Service temporarily unavailable")
        except CNOPInsufficientBalanceException:
            # Re-raise CNOPInsufficientBalanceException directly
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Withdrawal failed: user={username}, amount={amount}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Withdrawal failed: {str(e)}")

    async def create_buy_order_with_balance_update(
        self,
        username: str,
        asset_id: str,
        quantity: Decimal,
        price: Decimal,
        order_type: OrderType,
        total_cost: Decimal
    ) -> TransactionResult:
        """
        Create a buy order with atomic balance update.

        Args:
            username: Username
            order_data: Order data (asset_id, quantity, order_price)
            total_cost: Total cost of the order

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(username, LockType.BUY_ORDER):
                balance = self.balance_dao.get_balance(username)
                if not balance:
                    logger.critical(f"CRITICAL SYSTEM ERROR: User balance missing for user {username}. "
                                  f"This should NEVER happen as balance is created during user registration.")
                    raise CNOPDatabaseOperationException(
                        f"Critical system error: User balance missing for user {username}. "
                        f"This indicates a serious system issue. Please contact support immediately."
                    )

                if balance.current_balance < total_cost:
                    shortfall = total_cost - balance.current_balance
                    raise CNOPInsufficientBalanceException(
                        f"Insufficient balance for buy order. "
                        f"Current balance: ${balance.current_balance:.2f}, "
                        f"Order cost: ${total_cost:.2f}, "
                        f"Asset: {asset_id}, "
                        f"Quantity: {quantity}, "
                        f"Shortfall: ${shortfall:.2f}. "
                        f"Please deposit additional funds or reduce order quantity."
                    )

                now = datetime.now(timezone.utc)
                order = Order(
                    Pk=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    Sk=OrderFields.SK_VALUE,
                    order_id=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    username=username,
                    order_type=order_type,
                    asset_id=asset_id,
                    quantity=quantity,
                    price=price,
                    total_amount=total_cost,
                    status=OrderStatus.COMPLETED,  # Market orders are completed immediately
                    created_at=now,
                    updated_at=now
                )

                created_order = self.order_dao.create_order(order)

                now_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
                transaction = BalanceTransaction(
                    Pk=f"{TransactionFields.PK_PREFIX}{username}",
                    username=username,
                    Sk=now_timestamp,
                    transaction_type=TransactionType.ORDER_PAYMENT,
                    amount=-total_cost,  # Negative for payment
                    description=f"Payment for buy order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=created_order.order_id,
                    created_at=now
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                self.balance_dao._update_balance_from_transaction(created_transaction)

                try:
                    asset_quantity = created_order.quantity
                    updated_asset_balance = self.asset_balance_dao.upsert_asset_balance(
                        username, created_order.asset_id, asset_quantity
                    )
                except Exception as e:
                    logger.error(
                action=LogAction.ERROR,
                message=f"Error in Phase 4: {str(e)}"
            )
                    raise

                asset_transaction = AssetTransaction(
                    username=username,
                    asset_id=created_order.asset_id,
                    transaction_type=AssetTransactionType.BUY,
                    quantity=asset_quantity,
                    price=created_order.price,
                    total_amount=asset_quantity * created_order.price,
                    order_id=created_order.order_id
                )
                created_asset_transaction = self.asset_transaction_dao.create_asset_transaction(asset_transaction)

                updated_balance = self.balance_dao.get_balance(username)

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Buy order executed successfully: user={username}, order_id={created_order.order_id}, "
                           f"asset={created_order.asset_id}, quantity={asset_quantity}, "
                           f"total_cost={total_cost}, lock_duration={lock_duration}s")

                return TransactionResult(
                    status=TransactionStatus.COMPLETED,
                    transaction_type=TransactionType.ORDER_PAYMENT,
                    transaction_amount=total_cost,
                    balance=updated_balance,
                    asset_id=created_order.asset_id,
                    asset_quantity=asset_quantity,
                    asset_balance=updated_asset_balance,
                    order=created_order
                )

        except CNOPLockAcquisitionException as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Lock acquisition failed for buy order: user={username}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException("Service temporarily unavailable")
        except CNOPInsufficientBalanceException:
            # Re-raise CNOPInsufficientBalanceException directly
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Buy order creation failed: user={username}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Order creation failed: {str(e)}")

    async def create_sell_order_with_balance_update(
        self,
        username: str,
        asset_id: str,
        quantity: Decimal,
        price: Decimal,
        order_type: OrderType,
        asset_amount: Decimal
    ) -> TransactionResult:
        """
        Create a sell order with atomic balance update.

        Args:
            username: Username
            order_data: Order data (asset_id, quantity, order_price)
            asset_amount: Total amount from the sell order

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(username, LockType.SELL_ORDER):
                now = datetime.now(timezone.utc)
                order = Order(
                    Pk=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    Sk=OrderFields.SK_VALUE,
                    order_id=f"order_{uuid.uuid4().hex[:8]}_{int(now.timestamp())}",
                    username=username,
                    order_type=order_type,
                    asset_id=asset_id,
                    quantity=quantity,
                    price=price,
                    total_amount=asset_amount,
                    status=OrderStatus.COMPLETED,  # Market orders are completed immediately
                    created_at=now,
                    updated_at=now
                )

                created_order = self.order_dao.create_order(order)

                now_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
                transaction = BalanceTransaction(
                    Pk=f"{TransactionFields.PK_PREFIX}{username}",
                    username=username,
                    Sk=now_timestamp,
                    transaction_type=TransactionType.ORDER_SALE,  # Cash from selling assets
                    amount=asset_amount,  # Positive for receipt
                    description=f"Sale proceeds from order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=created_order.order_id
                )

                created_transaction = self.balance_dao.create_transaction(transaction)

                self.balance_dao._update_balance_from_transaction(created_transaction)

                try:
                    asset_quantity = created_order.quantity
                    updated_asset_balance = self.asset_balance_dao.upsert_asset_balance(
                        username, created_order.asset_id, -asset_quantity
                    )
                except Exception as e:
                    logger.error(
                action=LogAction.ERROR,
                message=f"Error in Phase 4 (asset balance update): {str(e)}"
            )
                    raise

                asset_transaction = AssetTransaction(
                    username=username,
                    asset_id=created_order.asset_id,
                    transaction_type=AssetTransactionType.SELL,
                    quantity=asset_quantity,
                    price=created_order.price,
                    total_amount=asset_quantity * created_order.price,
                    order_id=created_order.order_id
                )
                created_asset_transaction = self.asset_transaction_dao.create_asset_transaction(asset_transaction)

                updated_balance = self.balance_dao.get_balance(username)  # Use username directly

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Sell order created successfully: user={username}, order_id={created_order.order_id}, "
                           f"asset_amount={asset_amount}, lock_duration={lock_duration}s")

                return TransactionResult(
                    status=TransactionStatus.COMPLETED,
                    transaction_type=TransactionType.ORDER_PAYMENT,
                    transaction_amount=asset_amount * price,
                    balance=updated_balance,
                    asset_id=created_order.asset_id,
                    asset_quantity=asset_amount,
                    asset_balance=updated_asset_balance,
                    order=created_order
                )

        except CNOPLockAcquisitionException as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Lock acquisition failed for sell order: user={username}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException("Service temporarily unavailable")
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Sell order creation failed: user={username}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Order creation failed: {str(e)}")