from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
import logging
from boto3.dynamodb.conditions import Attr
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .base_dao import BaseDAO
from src.entities.asset import Asset, AssetCreate, AssetUpdate

logger = logging.getLogger(__name__)


class AssetDAO(BaseDAO):
    """Data Access Object for asset operations"""

    async def create_asset(self, asset_create: AssetCreate) -> Asset:
        """Create a new asset"""
        try:
            # Check if asset already exists
            existing_asset = await self.get_asset_by_id(asset_create.asset_id)
            if existing_asset:
                raise ValueError(f"Asset with ID {asset_create.asset_id} already exists")

            # Create asset item
            now = datetime.now(UTC).isoformat()
            asset_item = {
                'product_id': asset_create.asset_id,  # Using existing table schema (product_id)
                'asset_id': asset_create.asset_id,    # Also store as asset_id for clarity
                'name': asset_create.name,
                'description': asset_create.description or "",
                'category': asset_create.category,
                'amount': asset_create.amount,
                'price_usd': asset_create.price_usd,
                'is_active': True,  # New assets are active by default
                'created_at': now,
                'updated_at': now
            }

            # Validate price/active relationship
            if asset_item['price_usd'] == 0:
                asset_item['is_active'] = False

            # Save to inventory table
            created_item = self._safe_put_item(self.db.inventory_table, asset_item)

            return Asset(
                asset_id=asset_create.asset_id,
                name=asset_create.name,
                description=asset_create.description,
                category=asset_create.category,
                amount=asset_create.amount,
                price_usd=asset_create.price_usd,
                is_active=created_item['is_active'],
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to create asset: {e}")
            raise

    async def get_asset_by_id(self, asset_id: str) -> Optional[Asset]:
        """Get asset by asset_id (Primary Key lookup)"""
        try:
            logger.info(f"🔍 DEBUG: Looking up asset by ID: '{asset_id}'")

            key = {
                'product_id': asset_id  # Using existing table schema
            }

            logger.info(f"🔍 DEBUG: Using key: {key}")

            item = self._safe_get_item(self.db.inventory_table, key)
            logger.info(f"🔍 DEBUG: Database returned item: {item}")

            if not item:
                logger.warning(f"❌ DEBUG: No asset found for ID: '{asset_id}'")
                return None

            return Asset(
                asset_id=item['asset_id'],
                name=item['name'],
                description=item.get('description', ''),
                category=item['category'],
                amount=float(item['amount']),
                price_usd=float(item['price_usd']),
                is_active=item.get('is_active', True),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to get asset by ID {asset_id}: {e}")
            raise

    async def get_all_assets(self, active_only: bool = False) -> List[Asset]:
        """Get all assets, optionally filter by active status"""
        try:
            logger.info(f"🔍 DEBUG: Getting all assets, active_only: {active_only}")

            # Scan the inventory table
            scan_kwargs = {}
            if active_only:
                scan_kwargs['FilterExpression'] = Attr('is_active').eq(True)

            response = self.db.inventory_table.scan(**scan_kwargs)
            items = response.get('Items', [])

            logger.info(f"🔍 DEBUG: Found {len(items)} assets")

            assets = []
            for item in items:
                # Only process items that have asset-related fields
                if 'asset_id' in item or 'name' in item:
                    asset = Asset(
                        asset_id=item.get('asset_id', item.get('product_id')),
                        name=item.get('name', ''),
                        description=item.get('description', ''),
                        category=item.get('category', 'unknown'),
                        amount=float(item.get('amount', 0)),
                        price_usd=float(item.get('price_usd', 0)),
                        is_active=item.get('is_active', True),
                        created_at=datetime.fromisoformat(item.get('created_at', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(item.get('updated_at', datetime.utcnow().isoformat()))
                    )
                    assets.append(asset)

            return assets

        except Exception as e:
            logger.error(f"Failed to get all assets: {e}")
            raise

    async def get_assets_by_category(self, category: str) -> List[Asset]:
        """Get assets by category"""
        try:
            logger.info(f"🔍 DEBUG: Getting assets by category: '{category}'")

            # Scan with filter expression
            response = self.db.inventory_table.scan(
                FilterExpression=Attr('category').eq(category.lower())
            )
            items = response.get('Items', [])

            logger.info(f"🔍 DEBUG: Found {len(items)} assets in category '{category}'")

            assets = []
            for item in items:
                if 'asset_id' in item or 'name' in item:
                    asset = Asset(
                        asset_id=item.get('asset_id', item.get('product_id')),
                        name=item.get('name', ''),
                        description=item.get('description', ''),
                        category=item.get('category', category),
                        amount=float(item.get('amount', 0)),
                        price_usd=float(item.get('price_usd', 0)),
                        is_active=item.get('is_active', True),
                        created_at=datetime.fromisoformat(item.get('created_at', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(item.get('updated_at', datetime.utcnow().isoformat()))
                    )
                    assets.append(asset)

            return assets

        except Exception as e:
            logger.error(f"Failed to get assets by category {category}: {e}")
            raise

    async def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> Optional[Asset]:
        """Update asset (asset_id and name cannot be changed)"""
        try:
            # Build update expression for provided fields only
            updates = {}
            if asset_update.description is not None:
                updates['description'] = asset_update.description
            if asset_update.category is not None:
                updates['category'] = asset_update.category
            if asset_update.amount is not None:
                updates['amount'] = asset_update.amount
            if asset_update.price_usd is not None:
                updates['price_usd'] = asset_update.price_usd
            if asset_update.is_active is not None:
                updates['is_active'] = asset_update.is_active

            if not updates:
                # No updates provided, just return current asset
                return await self.get_asset_by_id(asset_id)

            # Validate price/active relationship if both are being updated
            if 'price_usd' in updates and 'is_active' in updates:
                if updates['price_usd'] == 0 and updates['is_active']:
                    raise ValueError("Asset cannot be active with zero price")
            elif 'price_usd' in updates and updates['price_usd'] == 0:
                # If setting price to 0, force is_active to False
                updates['is_active'] = False

            # Build update expression
            set_clauses = []
            expression_values = {}

            for field, value in updates.items():
                set_clauses.append(f"{field} = :{field}")
                expression_values[f":{field}"] = value

            # Always update timestamp
            set_clauses.append("updated_at = :updated_at")
            expression_values[":updated_at"] = datetime.utcnow().isoformat()

            update_expression = "SET " + ", ".join(set_clauses)

            key = {
                'product_id': asset_id  # Using existing table schema
            }

            item = self._safe_update_item(
                self.db.inventory_table,
                key,
                update_expression,
                expression_values
            )

            if not item:
                return None

            return Asset(
                asset_id=item.get('asset_id', asset_id),
                name=item['name'],
                description=item.get('description', ''),
                category=item['category'],
                amount=float(item['amount']),
                price_usd=float(item['price_usd']),
                is_active=item.get('is_active', True),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to update asset {asset_id}: {e}")
            raise

    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset by asset_id"""
        try:
            key = {
                'product_id': asset_id  # Using existing table schema
            }

            success = self._safe_delete_item(self.db.inventory_table, key)

            if success:
                logger.info(f"Asset deleted successfully: {asset_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete asset {asset_id}: {e}")
            raise

    async def update_asset_price(self, asset_id: str, new_price: float) -> Optional[Asset]:
        """Update only the price of an asset (convenience method)"""
        try:
            asset_update = AssetUpdate(price_usd=new_price)

            # If price is 0, automatically set is_active to False
            if new_price == 0:
                asset_update.is_active = False

            return await self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(f"Failed to update price for asset {asset_id}: {e}")
            raise

    async def update_asset_amount(self, asset_id: str, new_amount: float) -> Optional[Asset]:
        """Update only the amount of an asset (convenience method for inventory management)"""
        try:
            asset_update = AssetUpdate(amount=new_amount)
            return await self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(f"Failed to update amount for asset {asset_id}: {e}")
            raise

    async def deactivate_asset(self, asset_id: str) -> Optional[Asset]:
        """Deactivate an asset (convenience method)"""
        try:
            asset_update = AssetUpdate(is_active=False)
            return await self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(f"Failed to deactivate asset {asset_id}: {e}")
            raise

    async def activate_asset(self, asset_id: str) -> Optional[Asset]:
        """Activate an asset (only if price > 0)"""
        try:
            # First check if asset has valid price
            asset = await self.get_asset_by_id(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")

            if asset.price_usd <= 0:
                raise ValueError(f"Cannot activate asset {asset_id} with zero or negative price")

            asset_update = AssetUpdate(is_active=True)
            return await self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(f"Failed to activate asset {asset_id}: {e}")
            raise

    async def get_asset_stats(self) -> Dict[str, Any]:
        """Get summary statistics about assets"""
        try:
            all_assets = await self.get_all_assets()
            active_assets = [asset for asset in all_assets if asset.is_active]

            total_value = sum(asset.amount * asset.price_usd for asset in active_assets)

            category_counts = {}
            for asset in all_assets:
                category_counts[asset.category] = category_counts.get(asset.category, 0) + 1

            return {
                'total_assets': len(all_assets),
                'active_assets': len(active_assets),
                'inactive_assets': len(all_assets) - len(active_assets),
                'total_inventory_value_usd': round(total_value, 2),
                'assets_by_category': category_counts,
                'last_updated': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get asset stats: {e}")
            raise