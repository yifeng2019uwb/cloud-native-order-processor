"""
Balance DAO for user service database operations.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from ...database.dynamodb_connection import DynamoDBConnection
from ...entities.user import Balance, BalanceTransaction, BalanceCreate, BalanceTransactionCreate, BalanceResponse
from ...exceptions import DatabaseOperationException
from ...exceptions.shared_exceptions import BalanceNotFoundException, TransactionNotFoundException
from ..base_dao import BaseDAO

logger = logging.getLogger(__name__)


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
            raise BalanceNotFoundException(f"Balance for user '{username}' not found")

        return Balance(
            Pk=item["Pk"],
            Sk=item["Sk"],
            username=item["username"],
            current_balance=Decimal(item["current_balance"]),
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
            entity_type=item.get("entity_type", "balance")
        )

    def update_balance(self, username: str, current_balance: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            logger.info(f"Updating balance: user={username}, new_balance={current_balance}")
            updated_at = datetime.utcnow()

            response = self.table.update_item(
                Key={
                    "Pk": username,
                    "Sk": "BALANCE"
                },
                UpdateExpression="SET current_balance = :balance, updated_at = :updated_at",
                ExpressionAttributeValues={
                    ":balance": str(current_balance),
                    ":updated_at": updated_at.isoformat()
                },
                ReturnValues="ALL_NEW"
            )
            logger.info(f"Balance updated successfully: user={username}, new_balance={current_balance}")

            item = response["Attributes"]
            return Balance(
                Pk=item["Pk"],
                Sk=item["Sk"],
                username=item["username"],
                current_balance=Decimal(item["current_balance"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
                entity_type=item.get("entity_type", "balance")
            )

        except Exception as e:
            logger.error(f"Failed to update balance for user '{username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while updating balance for user '{username}': {str(e)}")

    def create_balance(self, balance_create: BalanceCreate) -> Balance:
        """Create a new balance record for a user."""
        try:
            now = datetime.utcnow()
            balance_item = {
                "Pk": balance_create.username,
                "Sk": "BALANCE",
                "username": balance_create.username,
                "current_balance": str(balance_create.initial_balance),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "entity_type": "balance"
            }

            self.table.put_item(Item=balance_item)

            return Balance(
                Pk=balance_item["Pk"],
                Sk=balance_item["Sk"],
                username=balance_item["username"],
                current_balance=balance_create.initial_balance,
                created_at=now,
                updated_at=now,
                entity_type="balance"
            )

        except Exception as e:
            logger.error(f"Failed to create balance for user '{balance_create.username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while creating balance for user '{balance_create.username}': {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction."""
        try:
            logger.info(f"Creating balance transaction: user={transaction.username}, "
                       f"type={transaction.transaction_type.value}, amount={transaction.amount}, "
                       f"description={transaction.description}")

            # Create transaction record
            item = {
                "Pk": f"TRANS#{transaction.username}",
                "username": transaction.username,
                "Sk": transaction.created_at.isoformat(),
                "transaction_id": str(transaction.transaction_id),
                "transaction_type": transaction.transaction_type.value,
                "amount": str(transaction.amount),
                "description": transaction.description,
                "status": transaction.status.value,
                "reference_id": transaction.reference_id,
                "created_at": transaction.created_at.isoformat(),
                "entity_type": "balance_transaction"
            }

            logger.debug(f"Transaction item prepared: {item}")
            self.table.put_item(Item=item)
            logger.info(f"Balance transaction created successfully: user={transaction.username}, "
                       f"amount={transaction.amount}, reference_id={transaction.reference_id}")

            return transaction

        except Exception as e:
            logger.error(f"Failed to create transaction for user '{transaction.username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while creating transaction for user '{transaction.username}': {str(e)}")

    def _update_balance_from_transaction(self, transaction: BalanceTransaction):
        """
        Update balance based on a completed transaction.

        Note: This method assumes balance records exist (created during user registration).
        All transactions in this simplified system are immediately completed.
        """
        try:
            logger.info(f"Updating balance from transaction: user={transaction.username}, "
                       f"transaction_amount={transaction.amount}, type={transaction.transaction_type.value}")

            # Get current balance and update it
            current_balance = self.get_balance(transaction.username)
            # Calculate new balance value
            new_balance = current_balance.current_balance + transaction.amount
            logger.debug(f"Balance calculation: current={current_balance.current_balance}, "
                        f"transaction={transaction.amount}, new={new_balance}")

            # Update existing balance
            self.update_balance(transaction.username, new_balance)
            logger.info(f"Balance updated from transaction: user={transaction.username}, "
                       f"new_balance={new_balance}")

        except Exception as e:
            raise DatabaseOperationException(f"Database operation failed while updating balance from transaction for user '{transaction.username}': {str(e)}")

    def get_transaction(self, username: str, transaction_id: UUID) -> BalanceTransaction:
        """Get a specific transaction for a user."""
        try:
            # Note: This method needs GSI2 for efficient lookup by transaction_id
            # For now, we'll need to query by user and filter
            transactions, _ = self.get_user_transactions(username, limit=1000)

            for transaction in transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction

            logger.warning(f"Transaction '{transaction_id}' not found for user '{username}'")
            raise TransactionNotFoundException(f"Transaction '{transaction_id}' not found for user '{username}'")

        except Exception as e:
            logger.error(f"Failed to get transaction '{transaction_id}' for user '{username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving transaction '{transaction_id}' for user '{username}': {str(e)}")

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
                transaction = BalanceTransaction(
                    Pk=item["Pk"],
                    username=item["username"],
                    Sk=item["Sk"],
                    transaction_id=UUID(item["transaction_id"]),
                    transaction_type=item["transaction_type"],
                    amount=Decimal(item["amount"]),
                    description=item["description"],
                    status=item["status"],
                    reference_id=item.get("reference_id"),
                    created_at=datetime.fromisoformat(item["created_at"]),
                    entity_type=item.get("entity_type", "balance_transaction")
                )
                transactions.append(transaction)

            last_evaluated_key = response.get("LastEvaluatedKey")
            return transactions, last_evaluated_key

        except Exception as e:
            logger.error(f"Failed to get transactions for user '{username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving transactions for user '{username}': {str(e)}")
