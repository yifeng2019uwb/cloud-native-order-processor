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
                "PK": f"USER#{balance.user_id}",
                "SK": "BALANCE",
                "current_balance": str(balance.current_balance),
                "total_deposits": str(balance.total_deposits),
                "total_withdrawals": str(balance.total_withdrawals),
                "created_at": balance.created_at.isoformat(),
                "updated_at": balance.updated_at.isoformat(),
                "entity_type": "balance"
            }

            self.db.table.put_item(Item=item)
            return balance

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to create balance: {str(e)}")

    def get_balance(self, user_id: UUID) -> Optional[Balance]:
        """Get balance for a user."""
        try:
            response = self.db.table.get_item(
                Key={
                    "PK": f"USER#{user_id}",
                    "SK": "BALANCE"
                }
            )

            if "Item" not in response:
                return None

            item = response["Item"]
            return Balance(
                user_id=user_id,
                current_balance=Decimal(item["current_balance"]),
                total_deposits=Decimal(item["total_deposits"]),
                total_withdrawals=Decimal(item["total_withdrawals"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"])
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get balance: {str(e)}")

    def update_balance(self, user_id: UUID, current_balance: Decimal,
                      total_deposits: Decimal, total_withdrawals: Decimal) -> Balance:
        """Update balance for a user."""
        try:
            updated_at = datetime.utcnow()

            response = self.db.table.update_item(
                Key={
                    "PK": f"USER#{user_id}",
                    "SK": "BALANCE"
                },
                UpdateExpression="SET current_balance = :balance, total_deposits = :deposits, "
                               "total_withdrawals = :withdrawals, updated_at = :updated_at",
                ExpressionAttributeValues={
                    ":balance": str(current_balance),
                    ":deposits": str(total_deposits),
                    ":withdrawals": str(total_withdrawals),
                    ":updated_at": updated_at.isoformat()
                },
                ReturnValues="ALL_NEW"
            )

            item = response["Attributes"]
            return Balance(
                user_id=user_id,
                current_balance=Decimal(item["current_balance"]),
                total_deposits=Decimal(item["total_deposits"]),
                total_withdrawals=Decimal(item["total_withdrawals"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"])
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to update balance: {str(e)}")

    def create_transaction(self, transaction: BalanceTransaction) -> BalanceTransaction:
        """Create a new balance transaction and update balance."""
        try:
            # Create transaction record
            item = {
                "PK": f"USER#{transaction.user_id}#{transaction.transaction_id}",
                "SK": transaction.created_at.isoformat(),
                "transaction_id": str(transaction.transaction_id),
                "user_id": str(transaction.user_id),
                "transaction_type": transaction.transaction_type.value,
                "amount": str(transaction.amount),
                "description": transaction.description,
                "status": transaction.status.value,
                "reference_id": transaction.reference_id,
                "created_at": transaction.created_at.isoformat(),
                "updated_at": transaction.updated_at.isoformat(),
                "entity_type": "balance_transaction"
            }

            self.db.table.put_item(Item=item)

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
            current_balance = self.get_balance(transaction.user_id)
            if not current_balance:
                # Create initial balance if doesn't exist
                current_balance = Balance(
                    user_id=transaction.user_id,
                    current_balance=Decimal('0.00'),
                    total_deposits=Decimal('0.00'),
                    total_withdrawals=Decimal('0.00')
                )
                self.create_balance(current_balance)

            # Calculate new balance values
            new_current_balance = current_balance.current_balance + transaction.amount
            new_total_deposits = current_balance.total_deposits
            new_total_withdrawals = current_balance.total_withdrawals

            if transaction.amount > 0:
                new_total_deposits += transaction.amount
            else:
                new_total_withdrawals += abs(transaction.amount)

            # Update balance
            self.update_balance(
                transaction.user_id,
                new_current_balance,
                new_total_deposits,
                new_total_withdrawals
            )

        except Exception as e:
            raise DatabaseOperationException(f"Failed to update balance from transaction: {str(e)}")

    def get_transaction(self, user_id: UUID, transaction_id: UUID) -> Optional[BalanceTransaction]:
        """Get a specific transaction."""
        try:
            # We need to query since PK is composite
            response = self.db.table.query(
                KeyConditionExpression=Key("PK").eq(f"USER#{user_id}#{transaction_id}"),
                Limit=1
            )

            if not response.get("Items"):
                return None

            item = response["Items"][0]
            return BalanceTransaction(
                transaction_id=UUID(item["transaction_id"]),
                user_id=user_id,
                transaction_type=item["transaction_type"],
                amount=Decimal(item["amount"]),
                description=item["description"],
                status=item["status"],
                reference_id=item.get("reference_id"),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"])
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get transaction: {str(e)}")

    def get_user_transactions(self, user_id: UUID, limit: int = 50,
                            start_key: Optional[dict] = None) -> tuple[List[BalanceTransaction], Optional[dict]]:
        """Get transactions for a user with pagination."""
        try:
            # Query for all transactions for this user
            # Since PK is USER#{user_id}#{transaction_id}, we need to use begins_with
            query_params = {
                "KeyConditionExpression": Key("PK").begins_with(f"USER#{user_id}#"),
                "Limit": limit,
                "ScanIndexForward": False  # Most recent first
            }

            if start_key:
                query_params["ExclusiveStartKey"] = start_key

            response = self.db.table.query(**query_params)

            transactions = []
            for item in response.get("Items", []):
                transaction = BalanceTransaction(
                    transaction_id=UUID(item["transaction_id"]),
                    user_id=user_id,
                    transaction_type=item["transaction_type"],
                    amount=Decimal(item["amount"]),
                    description=item["description"],
                    status=item["status"],
                    reference_id=item.get("reference_id"),
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"])
                )
                transactions.append(transaction)

            last_evaluated_key = response.get("LastEvaluatedKey")
            return transactions, last_evaluated_key

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to get user transactions: {str(e)}")

    def update_transaction_status(self, user_id: UUID, transaction_id: UUID,
                                status: str) -> BalanceTransaction:
        """Update transaction status and adjust balance if needed."""
        try:
            updated_at = datetime.utcnow()

            # We need to query first to get the SK (timestamp)
            transaction = self.get_transaction(user_id, transaction_id)
            if not transaction:
                raise EntityNotFoundException(f"Transaction {transaction_id} not found")

            old_status = transaction.status.value
            transaction.status = status

            response = self.db.table.update_item(
                Key={
                    "PK": f"USER#{user_id}#{transaction_id}",
                    "SK": transaction.created_at.isoformat()
                },
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": status,
                    ":updated_at": updated_at.isoformat()
                },
                ReturnValues="ALL_NEW"
            )

            # Update balance if status changed to/from completed
            if old_status != status:
                if status == "completed" and old_status != "completed":
                    # Transaction just completed - add to balance
                    self._update_balance_from_transaction(transaction)
                elif old_status == "completed" and status != "completed":
                    # Transaction was completed but now not - reverse the balance change
                    reversed_transaction = BalanceTransaction(
                        transaction_id=transaction.transaction_id,
                        user_id=transaction.user_id,
                        transaction_type=transaction.transaction_type,
                        amount=-transaction.amount,  # Reverse the amount
                        description=transaction.description,
                        status=transaction.status,
                        reference_id=transaction.reference_id,
                        created_at=transaction.created_at,
                        updated_at=updated_at
                    )
                    self._update_balance_from_transaction(reversed_transaction)

            item = response["Attributes"]
            return BalanceTransaction(
                transaction_id=UUID(item["transaction_id"]),
                user_id=user_id,
                transaction_type=item["transaction_type"],
                amount=Decimal(item["amount"]),
                description=item["description"],
                status=item["status"],
                reference_id=item.get("reference_id"),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"])
            )

        except ClientError as e:
            raise DatabaseOperationException(f"Failed to update transaction status: {str(e)}")

    def balance_exists(self, user_id: UUID) -> bool:
        """Check if balance exists for a user."""
        try:
            response = self.db.table.get_item(
                Key={
                    "PK": f"USER#{user_id}",
                    "SK": "BALANCE"
                }
            )
            return "Item" in response
        except ClientError:
            return False

    def user_has_transactions(self, user_id: UUID) -> bool:
        """Check if user has any transactions."""
        try:
            response = self.db.table.query(
                KeyConditionExpression=Key("PK").begins_with(f"USER#{user_id}#"),
                Limit=1
            )
            return len(response.get("Items", [])) > 0
        except ClientError:
            return False