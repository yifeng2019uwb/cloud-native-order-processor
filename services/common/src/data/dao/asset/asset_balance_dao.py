"""
Asset Balance DAO for managing user asset balances.
"""

from decimal import Decimal
from typing import List

from ....exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException
from ....shared.logging import BaseLogger, LogAction, LoggerName
from ...entities.asset.asset_balance import AssetBalance, AssetBalanceItem
from ...entities.entity_constants import AssetBalanceFields
from ...exceptions import CNOPDatabaseOperationException

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class AssetBalanceDAO:
    """Data Access Object for asset balance operations using PynamoDB"""

    def __init__(self, db_connection=None):
        """Initialize AssetBalanceDAO (PynamoDB doesn't need db_connection)"""
        # PynamoDB models handle their own connection

    def upsert_asset_balance(self, username: str, asset_id: str, quantity: Decimal) -> AssetBalance:
        """Create or update asset balance atomically"""
        try:
            # Try to get existing balance first
            try:
                balance_item = AssetBalanceItem.get(username, f"{AssetBalanceFields.SK_PREFIX}{asset_id}")
                existing_quantity = Decimal(balance_item.quantity)
                new_quantity = existing_quantity + quantity
                balance_item.quantity = str(new_quantity)
                balance_item.save()
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Asset balance updated: user={username}, asset={asset_id}, quantity={new_quantity}"
                )
                return balance_item.to_asset_balance()

            except AssetBalanceItem.DoesNotExist:
                new_quantity = quantity
                new_balance = AssetBalance(
                    username=username,
                    asset_id=asset_id,
                    quantity=new_quantity
                )
                balance_item = AssetBalanceItem.from_asset_balance(new_balance)
                balance_item.save()
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Asset balance created: user={username}, asset={asset_id}, quantity={new_quantity}"
                )
                return balance_item.to_asset_balance()

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to upsert asset balance for user '{username}' and asset '{asset_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while upserting asset balance for user '{username}' and asset '{asset_id}': {str(e)}") from e

    def get_asset_balance(self, username: str, asset_id: str) -> AssetBalance:
        """Get specific asset balance for user"""
        try:
            balance_item = AssetBalanceItem.get(username, f"{AssetBalanceFields.SK_PREFIX}{asset_id}")
            return balance_item.to_asset_balance()

        except AssetBalanceItem.DoesNotExist:
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"Asset balance not found for user '{username}' and asset '{asset_id}'"
            )
            raise CNOPAssetBalanceNotFoundException(f"Asset balance not found for user '{username}' and asset '{asset_id}'")
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get asset balance for user '{username}' and asset '{asset_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while getting asset balance for user '{username}' and asset '{asset_id}': {str(e)}") from e

    def get_all_asset_balances(self, username: str) -> List[AssetBalance]:
        """Get all asset balances for a user"""
        try:
            balances = []
            for balance_item in AssetBalanceItem.query(username, AssetBalanceItem.Sk.startswith(AssetBalanceFields.SK_PREFIX)):
                balances.append(balance_item.to_asset_balance())
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Asset balances for user {username}: {len(balances)} items"
            )
            return balances

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get asset balances for user '{username}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while getting asset balances for user '{username}': {str(e)}") from e

    def delete_asset_balance(self, username: str, asset_id: str) -> bool:
        """Delete asset balance"""
        try:
            balance_item = AssetBalanceItem.get(username, f"{AssetBalanceFields.SK_PREFIX}{asset_id}")
            balance_item.delete()
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Asset balance deleted: user={username}, asset={asset_id}"
            )
            return True

        except AssetBalanceItem.DoesNotExist:
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"Asset balance not found for deletion: user={username}, asset={asset_id}"
            )
            return False
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to delete asset balance for user '{username}' and asset '{asset_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while deleting asset balance for user '{username}' and asset '{asset_id}': {str(e)}") from e
