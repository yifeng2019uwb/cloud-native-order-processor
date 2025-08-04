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
from ...exceptions import DatabaseOperationException, EntityNotFoundException
from ..base_dao import BaseDAO

logger = logging.getLogger(__name__)


class BalanceDAO(BaseDAO):
    """Data Access Object for balance operations."""

    def __init__(self, db_connection: DynamoDBConnection):
        super().__init__(db_connection)
        self.table_name = "users"  # Using the same user table for balance data



    def get_balance(self, user_id: str) -> Balance:
        """Get balance for a user."""
        try:
            response = self.db.users_table.get_item(
                Key={
                    "Pk": user_id,
                    "Sk": "BALANCE"
                }
            )

            if "Item" not in response:
                logger.warning(f"Balance for user '{user_id}' not found")
                raise EntityNotFoundException(f"Balance for user '{user_id}' not found")

            item = response["Item"]
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
            logger.error(f"Failed to get balance for user '{user_id}': {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving balance for user '{user_id}': {str(e)}")

    def update_balance(self, user_id: str, current_balance: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            updated_at = datetime.utcnow()

            response = self.db.users_table.update_item(
                Key={
                    "Pk": user_id,
                    "Sk": "BALANCE"
                },
                UpdateExpression="SET current_balance = :balance, updated_at = :updated_at",
                ExpressionAttributeValues={
                    ":balance": str(current_balance),
                    ":updated_at": updated_at.isoformat()
                },
                ReturnValues="ALL_NEW"
            )

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
            logger.error(f"Failed to update balance for user '{user_id}': {e}")
            raise DatabaseOperationException(f"Database operation failed while updating balance for user '{user_id}': {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction."""
        try:
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

            self.db.users_table.put_item(Item=item)

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
            # Get current balance and update it
            current_balance = self.get_balance(transaction.username)
            # Calculate new balance value
            new_balance = current_balance.current_balance + transaction.amount
            # Update existing balance
            self.update_balance(transaction.username, new_balance)

        except Exception as e:
            raise DatabaseOperationException(f"Database operation failed while updating balance from transaction for user '{transaction.username}': {str(e)}")

    def get_transaction(self, user_id: str, transaction_id: UUID) -> BalanceTransaction:
        """Get a specific transaction for a user."""
        try:
            # Note: This method needs GSI2 for efficient lookup by transaction_id
            # For now, we'll need to query by user and filter
            transactions, _ = self.get_user_transactions(user_id, limit=1000)

            for transaction in transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction

            logger.warning(f"Transaction '{transaction_id}' not found for user '{user_id}'")
            raise EntityNotFoundException(f"Transaction '{transaction_id}' not found for user '{user_id}'")

        except Exception as e:
            logger.error(f"Failed to get transaction '{transaction_id}' for user '{user_id}': {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving transaction '{transaction_id}' for user '{user_id}': {str(e)}")

    def get_user_transactions(self, user_id: str, limit: int = 50,
                            start_key: Optional[dict] = None) -> tuple[List[BalanceTransaction], Optional[dict]]:
        """Get all transactions for a user with pagination."""
        try:
            query_params = {
                "KeyConditionExpression": Key("Pk").eq(f"TRANS#{user_id}"),
                "Limit": limit
            }

            if start_key:
                query_params["ExclusiveStartKey"] = start_key

            response = self.db.users_table.query(**query_params)

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
            logger.error(f"Failed to get transactions for user '{user_id}': {e}")
            raise DatabaseOperationException(f"Database operation failed while retrieving transactions for user '{user_id}': {str(e)}")
