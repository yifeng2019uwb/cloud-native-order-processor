"""
Asset Balance DAO for managing user asset balances.
"""

from typing import List, Optional
from datetime import datetime
from boto3.dynamodb.conditions import Key
from decimal import Decimal

from ..base_dao import BaseDAO
from ...entities.asset import AssetBalance, AssetBalanceItem
from ...exceptions import CNOPDatabaseOperationException
from ....exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException
from ....shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class AssetBalanceDAO(BaseDAO):
    """Data Access Object for asset balance operations"""

    def __init__(self, db_connection):
        """Initialize AssetBalanceDAO with database connection"""
        super().__init__(db_connection)
        # Table reference
        self.table = self.db.users_table

    def upsert_asset_balance(self, username: str, asset_id: str, quantity: Decimal) -> AssetBalance:
        """Create or update asset balance atomically"""
        logger.info(
        action=LogActions.DB_OPERATION,
        message=f"Upserting asset balance: user={username}, asset={asset_id}, quantity={quantity}"
    )
        # logger.debug(f"Parameters received: username={username}, asset_id={asset_id}, quantity={quantity}")
        now = datetime.utcnow().isoformat()

        # Try to get existing balance first
        try:
            existing_balance = self.get_asset_balance(username, asset_id)
            # Asset balance exists - update it
            new_quantity = existing_balance.quantity + quantity
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Existing balance found: {existing_balance.quantity}, adding {quantity}, new total: {new_quantity}"
        )

            # Update existing balance
            key = {
                'Pk': username,
                'Sk': f"ASSET#{asset_id}"
            }
            update_expression = "SET #quantity = :quantity, updated_at = :updated_at"
            expression_values = {
                ':quantity': str(new_quantity),
                ':updated_at': now
            }
            expression_names = {
                '#quantity': 'quantity'
            }

            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Updating existing asset balance: key={key}, new_quantity={new_quantity}"
        )
            updated_item = self._safe_update_item(
                self.table,
                key,
                update_expression,
                expression_values,
                expression_names
            )
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Asset balance updated: user={username}, asset={asset_id}, quantity={existing_balance.quantity} -> {new_quantity}"
        )

            # Extract asset_id from Sk field (format: ASSET#{asset_id})
            asset_id_from_sk = updated_item['Sk'].split('#')[1] if '#' in updated_item['Sk'] else updated_item['Sk']
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Extracted asset_id from Sk for update: {asset_id_from_sk}"
        )

            return AssetBalance(
                Pk=updated_item['Pk'],
                Sk=updated_item['Sk'],
                username=updated_item.get('username', updated_item['Pk']),
                asset_id=asset_id_from_sk,
                quantity=Decimal(updated_item['quantity']),
                created_at=datetime.fromisoformat(updated_item.get('created_at', updated_item['updated_at'])),  # Use updated_at as fallback
                updated_at=datetime.fromisoformat(updated_item['updated_at'])
            )

        except CNOPAssetBalanceNotFoundException:
            # Asset balance doesn't exist - create new one
            new_quantity = quantity
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"No existing balance found, creating new balance with quantity: {new_quantity}"
        )

            balance_item = {
                'Pk': username,
                'Sk': f"ASSET#{asset_id}",
                'username': username,
                'asset_id': asset_id,
                'quantity': str(new_quantity),
                'created_at': now,
                'updated_at': now
            }

            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Creating new asset balance: item={balance_item}"
        )
            created_item = self._safe_put_item(self.table, balance_item)
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Asset balance created: user={username}, asset={asset_id}, quantity={new_quantity}"
        )

            return AssetBalance(
                Pk=created_item['Pk'],
                Sk=created_item['Sk'],
                username=created_item.get('username', created_item['Pk']),
                asset_id=created_item['asset_id'],
                quantity=Decimal(created_item['quantity']),
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

    def get_asset_balance(self, username: str, asset_id: str) -> AssetBalance:
        """Get specific asset balance for user"""
        logger.info(
        action=LogActions.DB_OPERATION,
        message=f"Getting asset balance: user={username}, asset={asset_id}"
    )
        key = {
            'Pk': username,
            'Sk': f"ASSET#{asset_id}"
        }

        item = self._safe_get_item(self.table, key)

        if not item:
            logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Asset balance not found for user '{username}' and asset '{asset_id}'"
        )
            raise CNOPAssetBalanceNotFoundException(f"Asset balance not found for user '{username}' and asset '{asset_id}'")

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Creating AssetBalance object from item: {item}"
        )

        return AssetBalance(
            Pk=item['Pk'],
            Sk=item['Sk'],
            username=item.get('username', item['Pk']),  # Use Pk as fallback if username missing
            asset_id=item['asset_id'],  # Read directly from item field
            quantity=Decimal(item['quantity']),
            created_at=datetime.fromisoformat(item.get('created_at', item['updated_at'])),  # Use updated_at as fallback
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def get_all_asset_balances(self, username: str) -> List[AssetBalance]:
        """Get all asset balances for a user"""
        key_condition = Key('Pk').eq(username) & Key('Sk').begins_with('ASSET#')

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Querying asset balances for user: {username}"
        )
        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Key condition: {key_condition}"
        )

        items = self._safe_query(self.table, key_condition)

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Query returned {len(items)} items"
        )
        if items:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"First item structure: {items[0]}"
            )

        balances = []
        for item in items:
            try:
                balance = AssetBalance(
                    Pk=item['Pk'],
                    Sk=item['Sk'],
                    username=item.get('username', item['Pk']),  # Use Pk as fallback if username missing
                    asset_id=item['asset_id'],  # Read directly from item field
                    quantity=Decimal(item['quantity']),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
                balances.append(balance)
            except KeyError as e:
                logger.error(
                action=LogActions.ERROR,
                message=f"Missing field in item: {e}, item: {item}"
            )
                raise
            except Exception as e:
                logger.error(
                    action=LogActions.ERROR,
                    message=f"Error processing item: {e}, item: {item}"
                )
                raise

        return balances

    def delete_asset_balance(self, username: str, asset_id: str) -> bool:
        """Delete asset balance"""
        key = {
            'Pk': username,
            'Sk': f"ASSET#{asset_id}"
        }

        success = self._safe_delete_item(self.table, key)

        if success:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Asset balance deleted successfully: user={username}, asset={asset_id}"
            )

        return success
