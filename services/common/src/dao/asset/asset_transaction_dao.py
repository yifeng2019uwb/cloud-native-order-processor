"""
Asset Transaction DAO for managing asset transactions.
"""

from typing import List, Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key
from decimal import Decimal

from ..base_dao import BaseDAO
from ...entities.asset import AssetTransaction, AssetTransactionCreate
from ...exceptions import DatabaseOperationException
from ...exceptions.shared_exceptions import TransactionNotFoundException

logger = logging.getLogger(__name__)


class AssetTransactionDAO(BaseDAO):
    """Data Access Object for asset transaction operations"""

    def __init__(self, db_connection):
        """Initialize AssetTransactionDAO with database connection"""
        super().__init__(db_connection)
        # Table reference - change here if we need to switch tables
        self.table = self.db.users_table

    def create_asset_transaction(self, transaction_create: AssetTransactionCreate) -> AssetTransaction:
        """Create a new asset transaction"""
        logger.info(f"Creating asset transaction: user={transaction_create.username}, "
                   f"asset={transaction_create.asset_id}, type={transaction_create.transaction_type.value}, "
                   f"quantity={transaction_create.quantity}, price={transaction_create.price}")

        now = datetime.utcnow().isoformat()
        timestamp_iso = now.replace('+00:00', 'Z')

        transaction_item = {
            'Pk': f"TRANS#{transaction_create.username}#{transaction_create.asset_id}",
            'Sk': timestamp_iso,
            'username': transaction_create.username,
            'asset_id': transaction_create.asset_id,
            'transaction_type': transaction_create.transaction_type.value,
            'quantity': str(transaction_create.quantity),
            'price': str(transaction_create.price),
            'total_amount': str(transaction_create.quantity * transaction_create.price),
            'order_id': transaction_create.order_id,
            'status': 'COMPLETED',  # Default status
            'created_at': now
        }

        self._safe_put_item(self.table, transaction_item)
        logger.info(f"Asset transaction created: user={transaction_create.username}, "
                   f"asset={transaction_create.asset_id}, type={transaction_create.transaction_type.value}, "
                   f"quantity={transaction_create.quantity}")

        return AssetTransaction(
            Pk=transaction_item['Pk'],
            Sk=transaction_item['Sk'],
            username=transaction_item['username'],
            asset_id=transaction_item['asset_id'],
            transaction_type=transaction_create.transaction_type,
            quantity=Decimal(transaction_item['quantity']),
            price=Decimal(transaction_item['price']),
            total_amount=Decimal(transaction_item['total_amount']),
            order_id=transaction_item.get('order_id'),
            status=transaction_item['status'],
            created_at=datetime.fromisoformat(transaction_item['created_at'])
        )

    def get_asset_transaction(self, username: str, asset_id: str, timestamp: str) -> AssetTransaction:
        """Get specific asset transaction"""
        key = {
            'Pk': f"TRANS#{username}#{asset_id}",
            'Sk': timestamp
        }

        item = self._safe_get_item(self.table, key)

        if not item:
            raise TransactionNotFoundException(f"Asset transaction not found for user '{username}', asset '{asset_id}', timestamp '{timestamp}'")

        return AssetTransaction(
            Pk=item['Pk'],
            Sk=item['Sk'],
            username=item['username'],
            asset_id=item['asset_id'],
            transaction_type=item['transaction_type'],
            quantity=Decimal(item['quantity']),
            price=Decimal(item['price']),
            total_amount=Decimal(item['total_amount']),
            order_id=item.get('order_id'),
            status=item['status'],
            created_at=datetime.fromisoformat(item['created_at'])
        )

    def get_user_asset_transactions(self, username: str, asset_id: str, limit: Optional[int] = None) -> List[AssetTransaction]:
        """Get all transactions for a user and specific asset"""
        key_condition = Key('Pk').eq(f"TRANS#{username}#{asset_id}")

        items = self._safe_query(self.table, key_condition, limit=limit)

        transactions = []
        for item in items:
            transaction = AssetTransaction(
                Pk=item['Pk'],
                Sk=item['Sk'],
                username=item['username'],
                asset_id=item['asset_id'],
                transaction_type=item['transaction_type'],
                quantity=Decimal(item['quantity']),
                price=Decimal(item['price']),
                total_amount=Decimal(item['total_amount']),
                order_id=item.get('order_id'),
                status=item['status'],
                created_at=datetime.fromisoformat(item['created_at'])
            )
            transactions.append(transaction)

        return transactions

    def get_user_transactions(self, username: str, limit: Optional[int] = None) -> List[AssetTransaction]:
        """Get all transactions for a user across all assets"""
        # Note: This method requires a GSI on username for efficient querying
        # For now, we'll return empty list and add GSI later when needed
        # TODO: Add GSI on username field for efficient user transaction queries
        logger.warning("get_user_transactions() requires GSI on username field for efficient querying")
        return []

    def delete_asset_transaction(self, username: str, asset_id: str, timestamp: str) -> bool:
        """Delete asset transaction"""
        key = {
            'Pk': f"TRANS#{username}#{asset_id}",
            'Sk': timestamp
        }

        return self._safe_delete_item(self.table, key)