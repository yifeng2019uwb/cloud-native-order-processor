"""
Asset Balance DAO for managing user asset balances.
"""

from typing import List, Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key
from decimal import Decimal

from ..base_dao import BaseDAO
from ...entities.asset import AssetBalance
from ...exceptions import DatabaseOperationException
from ...exceptions.shared_exceptions import AssetBalanceNotFoundException

logger = logging.getLogger(__name__)


class AssetBalanceDAO(BaseDAO):
    """Data Access Object for asset balance operations"""

    def __init__(self, db_connection):
        """Initialize AssetBalanceDAO with database connection"""
        super().__init__(db_connection)

    def upsert_asset_balance(self, username: str, asset_id: str, quantity: Decimal) -> AssetBalance:
        """Create or update asset balance atomically"""
        now = datetime.utcnow().isoformat()

        balance_item = {
            'Pk': username,
            'Sk': f"ASSET#{asset_id}",
            'username': username,
            'asset_id': asset_id,
            'quantity': str(quantity),
            'updated_at': now
        }

        # Use conditional expression to set created_at only if item doesn't exist
        update_expression = "SET quantity = :quantity, updated_at = :updated_at"
        expression_values = {
            ':quantity': str(quantity),
            ':updated_at': now
        }

        # Try to update first (item exists)
        try:
            key = {
                'Pk': username,
                'Sk': f"ASSET#{asset_id}"
            }
            updated_item = self._safe_update_item(
                self.db.asset_balances_table,
                key,
                update_expression,
                expression_values
            )

            return AssetBalance(
                Pk=updated_item['Pk'],
                Sk=updated_item['Sk'],
                username=updated_item['username'],
                asset_id=updated_item['asset_id'],
                quantity=Decimal(updated_item['quantity']),
                created_at=datetime.fromisoformat(updated_item['created_at']),
                updated_at=datetime.fromisoformat(updated_item['updated_at'])
            )

        except DatabaseOperationException:
            # Item doesn't exist, create new one
            balance_item['created_at'] = now
            created_item = self._safe_put_item(self.db.asset_balances_table, balance_item)

            return AssetBalance(
                Pk=created_item['Pk'],
                Sk=created_item['Sk'],
                username=created_item['username'],
                asset_id=created_item['asset_id'],
                quantity=Decimal(created_item['quantity']),
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

    def get_asset_balance(self, username: str, asset_id: str) -> AssetBalance:
        """Get specific asset balance for user"""
        key = {
            'Pk': username,
            'Sk': f"ASSET#{asset_id}"
        }

        item = self._safe_get_item(self.db.asset_balances_table, key)

        if not item:
            raise AssetBalanceNotFoundException(f"Asset balance not found for user '{username}' and asset '{asset_id}'")

        return AssetBalance(
            Pk=item['Pk'],
            Sk=item['Sk'],
            username=item['username'],
            asset_id=item['asset_id'],
            quantity=Decimal(item['quantity']),
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def get_all_asset_balances(self, username: str) -> List[AssetBalance]:
        """Get all asset balances for a user"""
        key_condition = Key('Pk').eq(username) & Key('Sk').begins_with('ASSET#')

        items = self._safe_query(self.db.asset_balances_table, key_condition)

        balances = []
        for item in items:
            balance = AssetBalance(
                Pk=item['Pk'],
                Sk=item['Sk'],
                username=item['username'],
                asset_id=item['asset_id'],
                quantity=Decimal(item['quantity']),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )
            balances.append(balance)

        return balances

    def delete_asset_balance(self, username: str, asset_id: str) -> bool:
        """Delete asset balance"""
        key = {
            'Pk': username,
            'Sk': f"ASSET#{asset_id}"
        }

        return self._safe_delete_item(self.db.asset_balances_table, key)
