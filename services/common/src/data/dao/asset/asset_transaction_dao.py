"""
Asset Transaction DAO for managing asset transactions.
"""

from typing import List, Optional

from ....exceptions.shared_exceptions import CNOPTransactionNotFoundException
from ....shared.logging import BaseLogger, LogAction, LoggerName
from ...entities.asset import AssetTransaction, AssetTransactionItem
from ...entities.entity_constants import AssetTransactionFields
from ...exceptions import CNOPDatabaseOperationException

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class AssetTransactionDAO:
    """Data Access Object for asset transaction operations using PynamoDB"""

    def __init__(self, db_connection=None):
        """Initialize AssetTransactionDAO (PynamoDB doesn't need db_connection)"""
        # PynamoDB models handle their own connection


    def create_asset_transaction(self, transaction: AssetTransaction) -> AssetTransaction:
        """Create a new asset transaction"""
        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Creating asset transaction: user={transaction.username}, "
                   f"asset={transaction.asset_id}, type={transaction.transaction_type.value}, "
                   f"quantity={transaction.quantity}, price={transaction.price}"
        )

        try:
            # Create PynamoDB item from domain model
            transaction_item = AssetTransactionItem.from_asset_transaction(transaction)
            transaction_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Asset transaction created successfully: user={transaction.username}, "
                       f"asset={transaction.asset_id}, type={transaction.transaction_type.value}, "
                       f"quantity={transaction.quantity}"
            )

            return transaction_item.to_asset_transaction()

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create asset transaction: {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating asset transaction: {str(e)}") from e

    def get_asset_transaction(self, username: str, asset_id: str, timestamp: str) -> AssetTransaction:
        """Get specific asset transaction"""
        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Getting asset transaction: user={username}, asset={asset_id}, timestamp={timestamp}"
        )

        try:
            # Use PynamoDB get method
            transaction_item = AssetTransactionItem.get(
                AssetTransaction.build_pk(username, asset_id),
                timestamp
            )

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Asset transaction found: user={username}, asset={asset_id}, timestamp={timestamp}"
            )

            return transaction_item.to_asset_transaction()

        except AssetTransactionItem.DoesNotExist:
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"Asset transaction not found: user={username}, asset={asset_id}, timestamp={timestamp}"
            )
            raise CNOPTransactionNotFoundException(f"Asset transaction not found for user '{username}', asset '{asset_id}', timestamp '{timestamp}'")

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get asset transaction: {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while getting asset transaction: {str(e)}") from e

    def get_user_asset_transactions(self, username: str, asset_id: str, limit: Optional[int] = None) -> List[AssetTransaction]:
        """Get all transactions for a user and specific asset"""
        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Getting user asset transactions: user={username}, asset={asset_id}, limit={limit}"
        )

        try:
            # Use PynamoDB query method - query by hash key only
            query_result = AssetTransactionItem.query(
                AssetTransaction.build_pk(username, asset_id),
                limit=limit
            )

            transactions = []
            for item in query_result:
                transactions.append(item.to_asset_transaction())

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Found {len(transactions)} asset transactions for user={username}, asset={asset_id}"
            )

            return transactions

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get user asset transactions: {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while getting user asset transactions: {str(e)}") from e

    def get_user_transactions(self, username: str, limit: Optional[int] = None) -> List[AssetTransaction]:
        """Get all transactions for a user across all assets"""
        # Note: This method requires a GSI on username for efficient querying
        # For now, we'll return empty list and add GSI later when needed
        # Future enhancement: Add GSI on username field for efficient user transaction queries
        logger.warning(
            action=LogAction.ERROR,
            message="get_user_transactions() requires GSI on username field for efficient querying"
        )
        return []

    # TODO: Remove if not used after testing - delete_asset_transaction method
    # Financial transactions should never be deleted as they represent immutable historical records
    # def delete_asset_transaction(self, username: str, asset_id: str, timestamp: str) -> bool:
    #     """Delete asset transaction"""
    #     logger.info(
    #         action=LogAction.DB_OPERATION,
    #         message=f"Deleting asset transaction: user={username}, asset={asset_id}, timestamp={timestamp}"
    #     )

    #     try:
    #         # Use PynamoDB get and delete methods
    #         transaction_item = AssetTransactionItem.get(
    #             f"TRANS#{username}#{asset_id}",
    #             timestamp
    #         )
    #         transaction_item.delete()

    #         logger.info(
    #             action=LogAction.DB_OPERATION,
    #             message=f"Asset transaction deleted successfully: user={username}, asset={asset_id}, timestamp={timestamp}"
    #         )

    #         return True

    #     except AssetTransactionItem.DoesNotExist:
    #         logger.warning(
    #             action=LogAction.DB_OPERATION,
    #             message=f"Asset transaction not found for deletion: user={username}, asset={asset_id}, timestamp={timestamp}"
    #         )
    #         return False

    #     except Exception as e:
    #         logger.error(
    #             action=LogAction.ERROR,
    #             message=f"Failed to delete asset transaction: {str(e)}"
    #         )
    #         raise CNOPDatabaseOperationException(f"Database operation failed while deleting asset transaction: {str(e)}") from e