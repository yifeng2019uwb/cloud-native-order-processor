"""
Balance DAO for user service database operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from boto3.dynamodb.conditions import Key

from ...database.dynamodb_connection import DynamoDBConnection
from ...entities.user import Balance, BalanceTransaction, BalanceItem, BalanceTransactionItem
from ...exceptions import CNOPDatabaseOperationException
from ....exceptions.shared_exceptions import CNOPBalanceNotFoundException, CNOPTransactionNotFoundException
from ..base_dao import BaseDAO
from ....shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class BalanceDAO(BaseDAO):
    """Data Access Object for balance operations."""

    def __init__(self, db_connection: DynamoDBConnection):
        super().__init__(db_connection)
        self.table_name = "users"  # Using the same user table for balance data
        # Table reference - change here if we need to switch tables
        self.table = self.db.users_table


    def get_balance(self, username: str) -> Balance:
        """Get balance for a user."""
        key = {
            "Pk": username,
            "Sk": "BALANCE"
        }

        item = self._safe_get_item(self.table, key)

        if not item:
            raise CNOPBalanceNotFoundException(f"Balance for user '{username}' not found")

        # Convert database item to BalanceItem and then to Balance entity
        balance_item = BalanceItem(**item)
        return balance_item.to_entity()


    def create_balance(self, balance: Balance) -> Balance:
        """Create a new balance record for a user."""
        try:
            # Convert Balance entity to BalanceItem for database storage
            balance_item = BalanceItem.from_entity(balance)
            balance_data = balance_item.model_dump()

            self.table.put_item(Item=balance_data)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Balance created successfully: user={balance.username}, current_balance={balance.current_balance}"
            )

            # Convert back to Balance entity from database response
            return BalanceItem(**balance_data).to_entity()

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to create balance for user '{balance.username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating balance for user '{balance.username}': {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction."""
        try:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Creating balance transaction: user={transaction.username}, "
                       f"type={transaction.transaction_type.value}, amount={transaction.amount}, "
                       f"description={transaction.description}"
            )

            # Convert BalanceTransaction entity to BalanceTransactionItem for database storage
            transaction_item = BalanceTransactionItem.from_entity(transaction)
            transaction_data = transaction_item.model_dump()

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Transaction item prepared: {transaction_data}"
            )
            self.table.put_item(Item=transaction_data)
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Balance transaction created successfully: user={transaction.username}, "
                       f"amount={transaction.amount}, reference_id={transaction.reference_id}"
            )

            # Convert back to BalanceTransaction entity from database response
            return BalanceTransactionItem(**transaction_data).to_entity()

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to create transaction for user '{transaction.username}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating transaction for user '{transaction.username}': {str(e)}")

    def update_balance(self, username: str, new_balance: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            # Get current balance to preserve created_at
            current_balance = self.get_balance(username)

            # Create updated balance entity
            updated_balance = Balance(
                username=username,
                current_balance=new_balance,
                created_at=current_balance.created_at,
                updated_at=datetime.utcnow()
            )

            # Convert to BalanceItem and save
            balance_item = BalanceItem.from_entity(updated_balance)
            balance_data = balance_item.model_dump()

            self.table.put_item(Item=balance_data)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Balance updated successfully: user={username}, new_balance={new_balance}"
            )

            return updated_balance

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
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
                action=LogActions.DB_OPERATION,
                message=f"Updating balance from transaction: user={transaction.username}, "
                       f"transaction_amount={transaction.amount}, type={transaction.transaction_type.value}"
            )

            # Get current balance and update it
            current_balance = self.get_balance(transaction.username)
            # Calculate new balance value
            new_balance = current_balance.current_balance + transaction.amount
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Balance calculation: current={current_balance.current_balance}, "
                        f"transaction={transaction.amount}, new={new_balance}"
            )

            # Update existing balance
            self.update_balance(transaction.username, new_balance)
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Balance updated from transaction: user={transaction.username}, "
                       f"new_balance={new_balance}"
            )

        except Exception as e:
            raise CNOPDatabaseOperationException(f"Database operation failed while updating balance from transaction for user '{transaction.username}': {str(e)}")

    def get_transaction(self, username: str, transaction_id: UUID) -> BalanceTransaction:
        """Get a specific transaction for a user."""
        try:
            # Note: This method needs GSI2 for efficient lookup by transaction_id
            # For now, we'll need to query by user and filter
            transactions, _ = self.get_user_transactions(username, limit=1000)

            for transaction in transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction

            logger.warning(
            action=LogActions.ERROR,
            message=f"Transaction '{transaction_id}' not found for user '{username}'"
        )
            raise CNOPTransactionNotFoundException(f"Transaction '{transaction_id}' not found for user '{username}'")

        except Exception as e:
            logger.error(
            action=LogActions.ERROR,
            message=f"Failed to get transaction '{transaction_id}' for user '{username}': {e}"
        )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving transaction '{transaction_id}' for user '{username}': {str(e)}")

    def get_user_transactions(self, username: str, limit: int = 50,
                            start_key: Optional[dict] = None) -> tuple[List[BalanceTransaction], Optional[dict]]:
        """Get all transactions for a user with pagination."""
        try:
            query_params = {
                "KeyConditionExpression": Key("Pk").eq(f"TRANS#{username}"),
                "Limit": limit
            }

            if start_key:
                query_params["ExclusiveStartKey"] = start_key

            response = self.table.query(**query_params)

            transactions = []
            for item in response.get("Items", []):
                # Convert database item to BalanceTransactionItem and then to BalanceTransaction entity
                transaction_item = BalanceTransactionItem(**item)
                transaction = transaction_item.to_entity()
                transactions.append(transaction)

            last_evaluated_key = response.get("LastEvaluatedKey")
            return transactions, last_evaluated_key

        except Exception as e:
            logger.error(
            action=LogActions.ERROR,
            message=f"Failed to get transactions for user '{username}': {e}"
        )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving transactions for user '{username}': {str(e)}")
