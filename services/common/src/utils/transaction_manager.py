"""
Transaction Manager for Atomic Operations
Orchestrates complex transactions with proper locking for order and balance operations.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

from .lock_manager import UserLock, LOCK_TIMEOUTS, LockAcquisitionError
from ..dao.user import UserDAO, BalanceDAO
from ..dao.order import OrderDAO
from ..dao.inventory import AssetDAO
from ..entities.user import BalanceTransaction, TransactionType, TransactionStatus
from ..entities.order import Order, OrderStatus
from ..exceptions import DatabaseOperationException, EntityNotFoundException

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
            user_id: User ID
            amount: Amount to deposit

        Returns:
            TransactionResult with deposit information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "deposit", LOCK_TIMEOUTS["deposit"]):
                # Create deposit transaction
                transaction = BalanceTransaction(
                    user_id=UUID(user_id),
                    transaction_type=TransactionType.DEPOSIT,
                    amount=amount,
                    description="Deposit",
                    status=TransactionStatus.COMPLETED
                )

                # This will automatically update the balance
                created_transaction = await self.balance_dao.create_transaction(transaction)

                # Get updated balance
                balance = await self.balance_dao.get_balance(UUID(user_id))

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

        except LockAcquisitionError as e:
            logger.warning(f"Lock acquisition failed for deposit: user={user_id}, error={str(e)}")
            return TransactionResult(
                success=False,
                error="Operation is busy, please try again in a moment"
            )
        except Exception as e:
            logger.error(f"Deposit failed: user={user_id}, amount={amount}, error={str(e)}")
            return TransactionResult(
                success=False,
                error=f"Deposit failed: {str(e)}"
            )

    async def withdraw_funds(self, user_id: str, amount: Decimal) -> TransactionResult:
        """
        Withdraw funds from user account with proper locking.

        Args:
            user_id: User ID
            amount: Amount to withdraw

        Returns:
            TransactionResult with withdrawal information
        """
        start_time = datetime.now(timezone.utc)

        try:
            async with UserLock(user_id, "withdraw", LOCK_TIMEOUTS["withdraw"]):
                # Check balance first
                balance = await self.balance_dao.get_balance(UUID(user_id))
                if not balance:
                    return TransactionResult(
                        success=False,
                        error="User balance not found"
                    )

                if balance.current_balance < amount:
                    return TransactionResult(
                        success=False,
                        error=f"Insufficient balance. Current: ${balance.current_balance}, Required: ${amount}"
                    )

                # Create withdrawal transaction
                transaction = BalanceTransaction(
                    user_id=UUID(user_id),
                    transaction_type=TransactionType.WITHDRAWAL,
                    amount=-amount,  # Negative for withdrawal
                    description="Withdrawal",
                    status=TransactionStatus.COMPLETED
                )

                # This will automatically update the balance
                created_transaction = await self.balance_dao.create_transaction(transaction)

                # Get updated balance
                updated_balance = await self.balance_dao.get_balance(UUID(user_id))

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

        except LockAcquisitionError as e:
            logger.warning(f"Lock acquisition failed for withdrawal: user={user_id}, error={str(e)}")
            return TransactionResult(
                success=False,
                error="Operation is busy, please try again in a moment"
            )
        except Exception as e:
            logger.error(f"Withdrawal failed: user={user_id}, amount={amount}, error={str(e)}")
            return TransactionResult(
                success=False,
                error=f"Withdrawal failed: {str(e)}"
            )

    async def create_buy_order_with_balance_update(
        self,
        user_id: str,
        order_data: Dict[str, Any],
        total_cost: Decimal
    ) -> TransactionResult:
        """
        Create a buy order and update balance atomically.

        Args:
            user_id: User ID
            order_data: Order creation data
            total_cost: Total cost of the order

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)
        created_order = None
        balance_transaction = None

        try:
            async with UserLock(user_id, "buy_order", LOCK_TIMEOUTS["buy_order"]):
                # Phase 1: Validate prerequisites
                balance = await self.balance_dao.get_balance(UUID(user_id))
                if not balance:
                    return TransactionResult(
                        success=False,
                        error="User balance not found"
                    )

                if balance.current_balance < total_cost:
                    return TransactionResult(
                        success=False,
                        error=f"Insufficient balance. Current: ${balance.current_balance}, Required: ${total_cost}"
                    )

                # Phase 2: Execute operations
                # 2.1 Create order with PENDING status
                order_create_data = order_data.copy()
                order_create_data["status"] = OrderStatus.PENDING
                order_create_data["user_id"] = user_id
                order_create_data["total_amount"] = total_cost

                created_order = await self.order_dao.create_order(order_create_data)
                logger.info(f"Order created: {created_order.order_id}")

                # 2.2 Create balance transaction
                balance_transaction = BalanceTransaction(
                    user_id=UUID(user_id),
                    transaction_type=TransactionType.ORDER_PAYMENT,
                    amount=-total_cost,  # Negative for spending
                    description=f"Buy order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=str(created_order.order_id)
                )

                created_transaction = await self.balance_dao.create_transaction(balance_transaction)
                logger.info(f"Balance transaction created: {created_transaction.transaction_id}")

                # 2.3 Update order status to CONFIRMED
                await self.order_dao.update_order_status(
                    created_order.order_id,
                    OrderStatus.CONFIRMED
                )
                logger.info(f"Order confirmed: {created_order.order_id}")

                # Get updated balance
                updated_balance = await self.balance_dao.get_balance(UUID(user_id))

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Buy order transaction successful: user={user_id}, order_id={created_order.order_id}, lock_duration={lock_duration}s")

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

        except LockAcquisitionError as e:
            logger.warning(f"Lock acquisition failed for buy order: user={user_id}, error={str(e)}")
            return TransactionResult(
                success=False,
                error="Operation is busy, please try again in a moment"
            )
        except Exception as e:
            # Phase 3: Rollback on Error
            logger.error(f"Buy order transaction failed: user={user_id}, error={str(e)}")

            # Rollback balance transaction if created
            if balance_transaction:
                try:
                    await self.balance_dao.update_transaction_status(
                        UUID(user_id),
                        balance_transaction.transaction_id,
                        TransactionStatus.CANCELLED
                    )
                    logger.info("Balance transaction rolled back")
                except Exception as rollback_error:
                    logger.error(f"Balance rollback failed: {rollback_error}")

            # Mark order as FAILED if created
            if created_order:
                try:
                    await self.order_dao.update_order_status(
                        created_order.order_id,
                        OrderStatus.FAILED
                    )
                    logger.info("Order marked as FAILED")
                except Exception as rollback_error:
                    logger.error(f"Order rollback failed: {rollback_error}")

            return TransactionResult(
                success=False,
                error=f"Buy order failed: {str(e)}"
            )

    async def create_sell_order_with_balance_update(
        self,
        user_id: str,
        order_data: Dict[str, Any],
        asset_amount: Decimal
    ) -> TransactionResult:
        """
        Create a sell order and update asset balance atomically.

        Args:
            user_id: User ID
            order_data: Order creation data
            asset_amount: Amount of asset being sold

        Returns:
            TransactionResult with order and transaction information
        """
        start_time = datetime.now(timezone.utc)
        created_order = None
        balance_transaction = None

        try:
            async with UserLock(user_id, "sell_order", LOCK_TIMEOUTS["sell_order"]):
                # Phase 1: Validate prerequisites
                # TODO: Check asset balance when asset management is implemented
                # For now, we'll assume user has the asset

                # Phase 2: Execute operations
                # 2.1 Create order with PENDING status
                order_create_data = order_data.copy()
                order_create_data["status"] = OrderStatus.PENDING
                order_create_data["user_id"] = user_id
                order_create_data["asset_amount"] = asset_amount

                created_order = await self.order_dao.create_order(order_create_data)
                logger.info(f"Sell order created: {created_order.order_id}")

                # 2.2 Create balance transaction for asset sale
                # TODO: This will be updated when asset management is implemented
                balance_transaction = BalanceTransaction(
                    user_id=UUID(user_id),
                    transaction_type=TransactionType.ASSET_SALE,
                    amount=asset_amount,  # Positive for asset sale
                    description=f"Sell order {created_order.order_id}",
                    status=TransactionStatus.COMPLETED,
                    reference_id=str(created_order.order_id)
                )

                created_transaction = await self.balance_dao.create_transaction(balance_transaction)
                logger.info(f"Asset transaction created: {created_transaction.transaction_id}")

                # 2.3 Update order status to CONFIRMED
                await self.order_dao.update_order_status(
                    created_order.order_id,
                    OrderStatus.CONFIRMED
                )
                logger.info(f"Sell order confirmed: {created_order.order_id}")

                lock_duration = (datetime.now(timezone.utc) - start_time).total_seconds()

                logger.info(f"Sell order transaction successful: user={user_id}, order_id={created_order.order_id}, lock_duration={lock_duration}s")

                return TransactionResult(
                    success=True,
                    data={
                        "order": created_order,
                        "transaction": created_transaction,
                        "asset_amount": asset_amount
                    },
                    lock_duration=lock_duration
                )

        except LockAcquisitionError as e:
            logger.warning(f"Lock acquisition failed for sell order: user={user_id}, error={str(e)}")
            return TransactionResult(
                success=False,
                error="Operation is busy, please try again in a moment"
            )
        except Exception as e:
            # Phase 3: Rollback on Error
            logger.error(f"Sell order transaction failed: user={user_id}, error={str(e)}")

            # Rollback balance transaction if created
            if balance_transaction:
                try:
                    await self.balance_dao.update_transaction_status(
                        UUID(user_id),
                        balance_transaction.transaction_id,
                        TransactionStatus.CANCELLED
                    )
                    logger.info("Asset transaction rolled back")
                except Exception as rollback_error:
                    logger.error(f"Asset rollback failed: {rollback_error}")

            # Mark order as FAILED if created
            if created_order:
                try:
                    await self.order_dao.update_order_status(
                        created_order.order_id,
                        OrderStatus.FAILED
                    )
                    logger.info("Sell order marked as FAILED")
                except Exception as rollback_error:
                    logger.error(f"Sell order rollback failed: {rollback_error}")

            return TransactionResult(
                success=False,
                error=f"Sell order failed: {str(e)}"
            )