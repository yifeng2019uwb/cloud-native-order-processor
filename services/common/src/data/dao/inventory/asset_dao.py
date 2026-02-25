from typing import Dict, List

from ....exceptions.shared_exceptions import CNOPAssetNotFoundException
from ....shared.logging import BaseLogger, LogAction, LoggerName
# AssetFields no longer needed with product_id schema
from ...entities.inventory.asset import Asset, AssetItem
from ...exceptions import CNOPDatabaseOperationException

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class AssetDAO:
    """Data Access Object for asset operations using PynamoDB"""

    def __init__(self, db_connection=None):
        """Initialize AssetDAO (PynamoDB doesn't need db_connection)"""
        # PynamoDB models handle their own connection


    def create_asset(self, asset: Asset) -> Asset:
        """Create a new asset (internal use e.g. price update job)"""
        try:
            # Convert Asset entity to AssetItem for database storage
            asset_item = AssetItem.from_asset(asset)
            asset_item.save()

            # Convert back to Asset domain model
            return asset_item.to_asset()
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create asset '{asset.asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating asset '{asset.asset_id}': {str(e)}") from e

    def get_asset_by_id(self, asset_id: str) -> Asset:
        """Get an asset by its ID"""
        try:
            # Use PynamoDB to get asset by primary key
            asset_item = AssetItem.get(asset_id)

            # Convert to Asset domain model
            return asset_item.to_asset()

        except AssetItem.DoesNotExist:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Asset '{asset_id}' not found"
            )
            raise CNOPAssetNotFoundException(f"Asset '{asset_id}' not found")
        except Exception as exc:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get asset '{asset_id}': {exc}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving asset '{asset_id}': {str(exc)}") from exc

    def get_all_assets(self, active_only: bool = False) -> List[Asset]:
        """Get all assets, optionally filter by active status"""
        try:
            if active_only:
                assets = [asset_item.to_asset() for asset_item in AssetItem.scan(AssetItem.is_active == True)]
            else:
                assets = [asset_item.to_asset() for asset_item in AssetItem.scan()]
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"All assets: {len(assets)} items, active_only={active_only}"
            )
            return assets

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get all assets: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving all assets: {str(e)}") from e

    def get_assets_by_ids(self, asset_ids: List[str]) -> Dict[str, Asset]:
        """
        Batch retrieve multiple assets by their IDs using PynamoDB

        Args:
            asset_ids: List of asset IDs to retrieve

        Returns:
            Dictionary mapping asset_id -> Asset object
            Missing assets are not included in the result

        Raises:
            CNOPDatabaseOperationException: If batch operation fails
        """
        if not asset_ids:
            return {}

        try:
            assets = {}
            for asset_id in asset_ids:
                try:
                    asset_item = AssetItem.get(asset_id)
                    assets[asset_id] = asset_item.to_asset()
                except AssetItem.DoesNotExist:
                    continue
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Batch assets: {len(assets)} retrieved, {len(asset_ids) - len(assets)} missing"
            )
            return assets

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to batch retrieve assets: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while batch retrieving assets: {str(e)}") from e

    def update_asset(self, asset: Asset) -> Asset:
        """Update an asset (internal use e.g. price update job)"""
        try:
            # Get existing asset to preserve created_at
            existing_asset_item = AssetItem.get(asset.asset_id)

            # Convert Asset to AssetItem for database storage
            asset_item = AssetItem.from_asset(asset)

            # Preserve original created_at
            asset_item.created_at = existing_asset_item.created_at

            # Business rule: if price is zero, asset should be inactive
            if asset_item.price_usd == 0 or asset_item.price_usd == 0.0:
                asset_item.is_active = False

            # Save the updated asset (updated_at will be set automatically in save method)
            asset_item.save()

            # Convert back to Asset domain model
            return asset_item.to_asset()
        except AssetItem.DoesNotExist:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Asset '{asset.asset_id}' not found for update"
            )
            raise CNOPAssetNotFoundException(f"Asset '{asset.asset_id}' not found")
        except Exception as exc:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to update asset '{asset.asset_id}': {exc}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating asset '{asset.asset_id}': {str(exc)}") from exc
