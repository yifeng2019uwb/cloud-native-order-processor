"""
Balance DAO for user service database operations using PynamoDB.
"""

import os
import sys
# datetime import removed as it's not used directly
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

# Path setup for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ....exceptions.shared_exceptions import (CNOPBalanceNotFoundException,
                                              CNOPTransactionNotFoundException)
from ....shared.logging import BaseLogger, LogAction, LoggerName
from ...entities.user.balance import (Balance, BalanceItem, BalanceTransaction,
                                     BalanceTransactionItem)
from ...entities.entity_constants import BalanceFields, TransactionFields
from ..pagination import PaginationFields
from ...exceptions import CNOPDatabaseOperationException

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class BalanceDAO:
    """Data Access Object for balance operations using PynamoDB"""

    def __init__(self, db_connection=None):
        """Initialize BalanceDAO (PynamoDB doesn't need db_connection)"""
        # PynamoDB models handle their own connection


    def get_balance(self, username: str) -> Balance:
        """Get balance for a user."""
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Looking up balance for user: '{username}'"
            )

            # Use PynamoDB to get balance by primary key
            balance_item = BalanceItem.get(username, BalanceFields.SK_VALUE)

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance found for user: {username}"
            )

            # Convert to Balance domain model
            return balance_item.to_balance()

        except BalanceItem.DoesNotExist:
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"Balance not found for user: {username}"
            )
            raise CNOPBalanceNotFoundException(f"Balance for user '{username}' not found")
        except Exception as exc:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get balance for user {username}: {str(exc)}"
            )
            raise CNOPDatabaseOperationException(f"Failed to get balance for user '{username}'") from exc


    def create_balance(self, balance: Balance) -> Balance:
        """Create a new balance record for a user."""
        try:
            # Convert Balance to BalanceItem with PynamoDB
            balance_item = BalanceItem.from_balance(balance)

            # Save using PynamoDB (automatically handles timestamps)
            balance_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance created successfully: user={balance.username}, current_balance={balance.current_balance}"
            )

            # Convert back to Balance domain model
            return balance_item.to_balance()

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create balance for user '{balance.username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating balance for user '{balance.username}': {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction."""
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Creating balance transaction: user={transaction.username}, "
                       f"type={transaction.transaction_type.value}, amount={transaction.amount}, "
                       f"description={transaction.description}"
            )

            # Convert BalanceTransaction to BalanceTransactionItem with PynamoDB
            transaction_item = BalanceTransactionItem.from_balance_transaction(transaction)

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Transaction item prepared: {transaction_item.attribute_values}"
            )

            # Save using PynamoDB (automatically handles timestamps)
            transaction_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance transaction created successfully: user={transaction.username}, "
                       f"amount={transaction.amount}, reference_id={transaction.reference_id}"
            )

            # Convert back to BalanceTransaction domain model
            return transaction_item.to_balance_transaction()

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create transaction for user '{transaction.username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating transaction for user '{transaction.username}': {str(e)}")

    def update_balance(self, username: str, new_balance: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            # Get current balance first (same as archived version)
            current_balance = self.get_balance(username)

            # Create updated balance preserving created_at (same as archived version)
            updated_balance = Balance(
                username=username,
                current_balance=new_balance,
                created_at=current_balance.created_at,  # Preserve original created_at
                updated_at=current_balance.updated_at   # Will be updated by PynamoDB save()
            )

            # Convert to BalanceItem and save (same pattern as create_balance)
            balance_item = BalanceItem.from_balance(updated_balance)
            balance_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance updated successfully: user={username}, new_balance={new_balance}"
            )

            # Return the updated balance object (same as archived version)
            return updated_balance

        except CNOPBalanceNotFoundException:
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to update balance for user '{username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating balance for user '{username}': {str(e)}")

    def _update_balance_from_transaction(self, transaction: BalanceTransaction):
        """
        Update balance based on a completed transaction.

        Note: This method assumes balance records exist (created during user registration).
        All transactions in this simplified system are immediately completed.
        """
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Updating balance from transaction: user={transaction.username}, "
                       f"transaction_amount={transaction.amount}, type={transaction.transaction_type.value}"
            )

            current_balance = self.get_balance(transaction.username)
            new_balance = current_balance.current_balance + transaction.amount
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance calculation: current={current_balance.current_balance}, "
                        f"transaction={transaction.amount}, new={new_balance}"
            )

            self.update_balance(transaction.username, new_balance)
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Balance updated from transaction: user={transaction.username}, "
                       f"new_balance={new_balance}"
            )

        except Exception as e:
            raise CNOPDatabaseOperationException(f"Database operation failed while updating balance from transaction for user '{transaction.username}': {str(e)}")

    def get_transaction(self, username: str, transaction_id: UUID) -> BalanceTransaction:
        """Get a specific transaction for a user."""
        try:
            transactions, _ = self.get_user_transactions(username, limit=1000)

            for transaction in transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction

            logger.warning(
                action=LogAction.ERROR,
                message=f"Transaction '{transaction_id}' not found for user '{username}'"
            )
            raise CNOPTransactionNotFoundException(f"Transaction '{transaction_id}' not found for user '{username}'")

        except CNOPTransactionNotFoundException:
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get transaction '{transaction_id}' for user '{username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving transaction '{transaction_id}' for user '{username}': {str(e)}")

    def get_user_transactions(self, username: str, limit: int = 50,
                            start_key: Optional[dict] = None) -> tuple[List[BalanceTransaction], Optional[dict]]:
        """Get all transactions for a user with pagination."""
        try:
            # Use PynamoDB to query transactions
            query_result = BalanceTransactionItem.query(
                BalanceTransaction.build_pk(username),
                limit=limit,
                last_evaluated_key=start_key
            )

            transactions = []
            last_evaluated_key = None

            for item in query_result:
                transaction = item.to_balance_transaction()
                transactions.append(transaction)

            # Get the last evaluated key for pagination
            last_evaluated_key = getattr(query_result, PaginationFields.LAST_EVALUATED_KEY, None)

            return transactions, last_evaluated_key

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get transactions for user '{username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving transactions for user '{username}': {str(e)}")

    def cleanup_failed_transaction(self, username: str, transaction_id: UUID) -> None:
        """Clean up a failed transaction record to maintain data consistency."""
        try:
            # Find the transaction by querying and then delete it
            # Note: This matches the archived behavior of finding by transaction_id
            # Query to find the specific transaction
            for item in BalanceTransactionItem.query(BalanceTransaction.build_pk(username)):
                if item.transaction_id == str(transaction_id):
                    item.delete()
                    logger.info(
                        action=LogAction.DB_OPERATION,
                        message=f"Cleaned up failed transaction: user={username}, transaction_id={transaction_id}"
                    )
                    return

            logger.warning(
                action=LogAction.ERROR,
                message=f"Transaction not found for cleanup: user={username}, transaction_id={transaction_id}"
            )

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to cleanup transaction: user={username}, transaction_id={transaction_id}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while cleaning up transaction for user '{username}': {str(e)}")
