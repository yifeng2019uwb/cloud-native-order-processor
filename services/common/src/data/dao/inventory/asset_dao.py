from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from boto3.dynamodb.conditions import Attr
import sys
import os
import boto3

# Path setup for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..base_dao import BaseDAO
from ...entities.inventory import Asset, AssetItem
from ...entities.entity_constants import AssetFields, TimestampFields
from ...exceptions import CNOPDatabaseOperationException
from ....exceptions.shared_exceptions import CNOPAssetNotFoundException
from ....shared.logging import BaseLogger, Loggers, LogActions
from ...database.dynamodb_connection import get_dynamodb_manager

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class AssetDAO(BaseDAO):
    """Data Access Object for asset operations"""

    def __init__(self, db_connection):
        """Initialize AssetDAO with database connection"""
        super().__init__(db_connection)
        # Table reference
        self.table = self.db.inventory_table
        # Get DynamoDB client for batch operations
        self.client = get_dynamodb_manager().get_client()


    def create_asset(self, asset: Asset) -> Asset:
        try:
            # Convert Asset entity to AssetItem for database storage
            asset_item = AssetItem.from_entity(asset)
            asset_data = asset_item.model_dump()

            created_item = self._safe_put_item(self.table, asset_data)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Asset created successfully: id={asset.asset_id}, name={asset.name}, category={asset.category}"
            )

            # Convert back to Asset from database response
            return AssetItem(**created_item).to_entity()
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to create asset '{asset.asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating asset '{asset.asset_id}': {str(e)}")

    def get_asset_by_id(self, asset_id: str) -> Asset:
        try:
            key = {AssetFields.PRODUCT_ID: asset_id}
            item = self._safe_get_item(self.table, key)
            if not item:
                logger.warning(
                    action=LogActions.ERROR,
                    message=f"Asset '{asset_id}' not found"
                )
                raise CNOPAssetNotFoundException(f"Asset '{asset_id}' not found")
            return AssetItem(**item).to_entity()
        except CNOPAssetNotFoundException:
            # Re-raise asset not found exceptions directly
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving asset '{asset_id}': {str(e)}")

    def get_all_assets(self, active_only: bool = False) -> List[Asset]:
        """Get all assets, optionally filter by active status"""
        try:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Getting all assets, active_only: {active_only}"
            )

            # Scan the inventory table
            scan_kwargs = {}
            if active_only:
                scan_kwargs['FilterExpression'] = Attr('is_active').eq(True)

            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Found {len(items)} assets"
            )


            # Convert each item to Asset entity
            assets = []
            for item in items:
                assets.append(AssetItem(**item).to_entity())
            return assets

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get all assets: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving all assets: {str(e)}")

    def get_assets_by_ids(self, asset_ids: List[str]) -> Dict[str, Asset]:
        """
        Batch retrieve multiple assets by their IDs using DynamoDB batch_get_item

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
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Batch retrieving {len(asset_ids)} assets"
            )

            # Prepare keys for batch_get_item (DynamoDB low-level API format)
            keys = [{AssetFields.PRODUCT_ID: {'S': asset_id}} for asset_id in asset_ids]

            # Use DynamoDB client's batch_get_item method
            response = self.client.batch_get_item(
                RequestItems={
                    self.table.table_name: {
                        'Keys': keys
                    }
                }
            )

            # Extract items from response
            items = response.get('Responses', {}).get(self.table.table_name, [])

            # Handle unprocessed keys (retry once if needed)
            unprocessed_keys = response.get('UnprocessedKeys', {})
            if unprocessed_keys and self.table.table_name in unprocessed_keys:
                logger.warning(
                    action=LogActions.DB_OPERATION,
                    message=f"Retrying {len(unprocessed_keys[self.table.table_name]['Keys'])} unprocessed keys"
                )
                retry_response = self.client.batch_get_item(
                    RequestItems={
                        self.table.table_name: {
                            'Keys': unprocessed_keys[self.table.table_name]['Keys']
                        }
                    }
                )
                items.extend(retry_response.get('Responses', {}).get(self.table.table_name, []))

            # Convert to Asset entities and create mapping
            assets = {}
            for item in items:
                # Convert DynamoDB low-level format to high-level format
                converted_item = self._convert_dynamodb_item(item)
                asset = AssetItem(**converted_item).to_entity()
                assets[asset.asset_id] = asset

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Successfully retrieved {len(assets)} out of {len(asset_ids)} requested assets"
            )

            return assets

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to batch retrieve assets: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while batch retrieving assets: {str(e)}")

    def update_asset(self, asset: Asset) -> Asset:
        try:
            # Get existing asset to preserve created_at
            existing_asset = self.get_asset_by_id(asset.asset_id)

            # Convert Asset to AssetItem for database storage (handles float to Decimal conversion)
            asset_item = AssetItem.from_entity(asset)
            asset_data = asset_item.model_dump()

            # Add product_id for database key
            asset_data[AssetFields.PRODUCT_ID] = asset.asset_id

            # Preserve original created_at, update updated_at
            asset_data[TimestampFields.CREATED_AT] = existing_asset.created_at.isoformat()
            asset_data[TimestampFields.UPDATED_AT] = datetime.utcnow().isoformat()

            # Update the item in database
            key = {AssetFields.PRODUCT_ID: asset.asset_id}
            # Filter out product_id from update (it's the primary key)
            update_data = {k: v for k, v in asset_data.items() if k != AssetFields.PRODUCT_ID}

            # Handle reserved keyword "name" with expression attribute names
            expression_names = {"#name": "name"} if "name" in update_data else {}
            update_parts = []
            expression_values = {}

            for k, v in update_data.items():
                if k == "name":
                    update_parts.append("#name = :name")
                    expression_values[":name"] = v
                else:
                    update_parts.append(f"{k} = :{k}")
                    expression_values[f":{k}"] = v

            updated_item = self._safe_update_item(
                self.table,
                key,
                "SET " + ", ".join(update_parts),
                expression_values,
                expression_names
            )

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Asset updated successfully: id={asset.asset_id}, name={asset.name}"
            )

            return updated_item
        except CNOPAssetNotFoundException:
            # Re-raise asset not found exceptions directly
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to update asset '{asset.asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating asset '{asset.asset_id}': {str(e)}")

    def _convert_dynamodb_item(self, item: dict) -> dict:
        """
        Convert DynamoDB low-level format to high-level format for AssetItem

        Args:
            item: DynamoDB item in low-level format

        Returns:
            Converted item in high-level format
        """
        converted = {}
        for key, value in item.items():
            if isinstance(value, dict):
                if 'S' in value:
                    converted[key] = value['S']
                elif 'N' in value:
                    converted[key] = value['N']
                elif 'BOOL' in value:
                    converted[key] = value['BOOL']
                elif 'NULL' in value:
                    converted[key] = None
                else:
                    converted[key] = value
            else:
                converted[key] = value
        return converted
