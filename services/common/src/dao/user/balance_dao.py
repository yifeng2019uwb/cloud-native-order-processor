"""
Balance DAO for user service database operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from ...database.dynamodb_connection import DynamoDBConnection
from ...entities.user import Balance, BalanceTransaction, BalanceCreate, BalanceTransactionCreate, BalanceResponse
from ...exceptions import DatabaseOperationException, EntityNotFoundException


class BalanceDAO:
    """Data Access Object for balance operations."""

    def __init__(self, db_connection: DynamoDBConnection):
        self.db = db_connection
        self.table_name = "users"  # Using the same user table for balance data

    def create_balance(self, balance: Balance) -> Balance:
        """Create a new balance record."""
        try:
            item = {
                "Pk": f"BALANCE#{balance.username}",
                "username": balance.username,
                "current_balance": str(balance.current_balance),
                "created_at": balance.created_at.isoformat(),
                "updated_at": balance.updated_at.isoformat(),
                "entity_type": "balance"
            }

            self.db.users_table.put_item(Item=item)
            return balance

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to create balance: {str(e)}")

    def create_balance_from_request(self, balance_create: BalanceCreate) -> Balance:
        """Create a new balance record from BalanceCreate request."""
        try:
            # Create Balance entity with proper PK generation
            balance = Balance(
                Pk=f"BALANCE#{balance_create.username}",
                username=balance_create.username,
                current_balance=balance_create.initial_balance
            )

            item = {
                "Pk": balance.Pk,
                "Sk": "BALANCE",  # Sort key for balance records
                "username": balance.username,
                "current_balance": str(balance.current_balance),
                "created_at": balance.created_at.isoformat(),
                "updated_at": balance.updated_at.isoformat(),
                "entity_type": "balance"
            }

            self.db.users_table.put_item(Item=item)
            return balance

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to create balance: {str(e)}")

    def get_balance(self, user_id: str) -> Optional[Balance]:
        """Get balance for a user."""
        try:
            response = self.db.users_table.get_item(
                Key={
                    "Pk": f"BALANCE#{user_id}",
                    "Sk": "BALANCE"
                }
            )

            if "Item" not in response:
                return None

            item = response["Item"]
            return Balance(
                Pk=item["Pk"],
                username=item["username"],
                current_balance=Decimal(item["current_balance"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
                entity_type=item.get("entity_type", "balance")
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get balance: {str(e)}")

    def update_balance(self, user_id: str, current_balance: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            updated_at = datetime.utcnow()

            response = self.db.users_table.update_item(
                Key={
                    "Pk": f"BALANCE#{user_id}",
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
                username=item["username"],
                current_balance=Decimal(item["current_balance"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
                entity_type=item.get("entity_type", "balance")
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to update balance: {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction and update balance."""
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

            # Update balance if transaction is completed
            if transaction.status.value == "completed":
                self._update_balance_from_transaction(transaction)

            return transaction

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to create transaction: {str(e)}")

    def _update_balance_from_transaction(self, transaction: BalanceTransaction):
        """Update balance based on a completed transaction."""
        try:
            # Get current balance
            current_balance = self.get_balance(transaction.username)
            if not current_balance:
                # Create initial balance if doesn't exist
                current_balance = Balance(
                    Pk=f"BALANCE#{transaction.username}",
                    username=transaction.username,
                    current_balance=Decimal('0.00')
                )
                self.create_balance(current_balance)

            # Calculate new balance value
            new_balance = current_balance.current_balance + transaction.amount

            # Update balance
            self.update_balance(transaction.username, new_balance)

        except Exception as e:
            raise DatabaseOperationException(f"Failed to update balance from transaction: {str(e)}")

    def get_transaction(self, user_id: str, transaction_id: UUID) -> Optional[BalanceTransaction]:
        """Get a specific transaction for a user."""
        try:
            # Note: This method needs GSI2 for efficient lookup by transaction_id
            # For now, we'll need to query by user and filter
            transactions, _ = self.get_user_transactions(user_id, limit=1000)

            for transaction in transactions:
                if transaction.transaction_id == transaction_id:
                    return transaction

            return None

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get transaction: {str(e)}")

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

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get user transactions: {str(e)}")

    def update_transaction_status(self, user_id: str, transaction_id: UUID,
                                status: str) -> BalanceTransaction:
        """Update transaction status and adjust balance if needed."""
        try:
            # Note: Transactions are immutable in the current design
            # This method would need to be redesigned if status updates are needed
            raise DatabaseOperationException("Transaction status updates not supported in current design")

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to update transaction status: {str(e)}")

    def balance_exists(self, user_id: str) -> bool:
        """Check if balance exists for a user."""
        try:
            balance = self.get_balance(user_id)
            return balance is not None
        except Exception:
            return False

    def user_has_transactions(self, user_id: str) -> bool:
        """Check if user has any transactions."""
        try:
            transactions, _ = self.get_user_transactions(user_id, limit=1)
            return len(transactions) > 0
        except Exception:
            return False