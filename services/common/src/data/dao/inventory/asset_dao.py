from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from boto3.dynamodb.conditions import Attr
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..base_dao import BaseDAO
from ...entities.inventory import Asset, AssetCreate, AssetUpdate
from ...exceptions import CNOPDatabaseOperationException
from ....exceptions.shared_exceptions import CNOPAssetNotFoundException
from ....shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class AssetDAO(BaseDAO):
    """Data Access Object for asset operations"""

    def __init__(self, db_connection):
        """Initialize AssetDAO with database connection"""
        super().__init__(db_connection)
        # Table reference - change here if we need to switch tables
        self.table = self.db.inventory_table

    def create_asset(self, asset_create: AssetCreate) -> Asset:
        try:
            now = datetime.now(UTC).isoformat()
            asset_item = {
                'product_id': asset_create.asset_id,
                'asset_id': asset_create.asset_id,
                'name': asset_create.name,
                'description': asset_create.description or "",
                'category': asset_create.category,
                'amount': asset_create.amount,
                'price_usd': asset_create.price_usd,

                # CoinGecko API fields - Comprehensive market data
                'symbol': asset_create.symbol,
                'image': asset_create.image,
                'market_cap_rank': asset_create.market_cap_rank,

                # Price data
                'current_price': asset_create.current_price,
                'high_24h': asset_create.high_24h,
                'low_24h': asset_create.low_24h,

                # Supply information
                'circulating_supply': asset_create.circulating_supply,
                'total_supply': asset_create.total_supply,
                'max_supply': asset_create.max_supply,

                # Price changes
                'price_change_24h': asset_create.price_change_24h,
                'price_change_percentage_24h': asset_create.price_change_percentage_24h,
                'price_change_percentage_7d': asset_create.price_change_percentage_7d,
                'price_change_percentage_30d': asset_create.price_change_percentage_30d,

                # Market metrics
                'market_cap': asset_create.market_cap,
                'market_cap_change_24h': asset_create.market_cap_change_24h,
                'market_cap_change_percentage_24h': asset_create.market_cap_change_percentage_24h,

                # Volume and trading
                'total_volume_24h': asset_create.total_volume_24h,
                'volume_change_24h': asset_create.volume_change_24h,

                # Historical context
                'ath': asset_create.ath,
                'ath_change_percentage': asset_create.ath_change_percentage,
                'ath_date': asset_create.ath_date,
                'atl': asset_create.atl,
                'atl_change_percentage': asset_create.atl_change_percentage,
                'atl_date': asset_create.atl_date,

                # Additional metadata
                'last_updated': asset_create.last_updated,
                'sparkline_7d': asset_create.sparkline_7d,

                'is_active': True,
                'created_at': now,
                'updated_at': now
            }
            created_item = self._safe_put_item(self.table, asset_item)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Asset created successfully: id={asset_create.asset_id}, name={asset_create.name}, category={asset_create.category}"
            )

            return Asset(
                asset_id=asset_create.asset_id,
                name=asset_create.name,
                description=asset_create.description,
                category=asset_create.category,
                amount=asset_create.amount,
                price_usd=asset_create.price_usd,

                # CoinGecko API fields - Comprehensive market data
                symbol=asset_create.symbol,
                image=asset_create.image,
                market_cap_rank=asset_create.market_cap_rank,

                # Price data
                current_price=asset_create.current_price,
                high_24h=asset_create.high_24h,
                low_24h=asset_create.low_24h,

                # Supply information
                circulating_supply=asset_create.circulating_supply,
                total_supply=asset_create.total_supply,
                max_supply=asset_create.max_supply,

                # Price changes
                price_change_24h=asset_create.price_change_24h,
                price_change_percentage_24h=asset_create.price_change_percentage_24h,
                price_change_percentage_7d=asset_create.price_change_percentage_7d,
                price_change_percentage_30d=asset_create.price_change_percentage_30d,

                # Market metrics
                market_cap=asset_create.market_cap,
                market_cap_change_24h=asset_create.market_cap_change_24h,
                market_cap_change_percentage_24h=asset_create.market_cap_change_percentage_24h,

                # Volume and trading
                total_volume_24h=asset_create.total_volume_24h,
                volume_change_24h=asset_create.volume_change_24h,

                # Historical context
                ath=asset_create.ath,
                ath_change_percentage=asset_create.ath_change_percentage,
                ath_date=asset_create.ath_date,
                atl=asset_create.atl,
                atl_change_percentage=asset_create.atl_change_percentage,
                atl_date=asset_create.atl_date,

                # Additional metadata
                last_updated=asset_create.last_updated,
                sparkline_7d=asset_create.sparkline_7d,

                is_active=created_item['is_active'],
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to create asset '{asset_create.asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating asset '{asset_create.asset_id}': {str(e)}")

    def get_asset_by_id(self, asset_id: str) -> Asset:
        try:
            key = {'product_id': asset_id}
            item = self._safe_get_item(self.table, key)
            if not item:
                logger.warning(
                    action=LogActions.ERROR,
                    message=f"Asset '{asset_id}' not found"
                )
                raise CNOPAssetNotFoundException(f"Asset '{asset_id}' not found")
            return Asset(
                asset_id=item['asset_id'],
                name=item['name'],
                description=item.get('description', ''),
                category=item['category'],
                amount=float(item['amount']),
                price_usd=float(item['price_usd']),

                # CoinGecko API fields - Comprehensive market data
                symbol=item.get('symbol'),
                image=item.get('image'),
                market_cap_rank=item.get('market_cap_rank'),

                # Price data
                current_price=item.get('current_price'),
                high_24h=item.get('high_24h'),
                low_24h=item.get('low_24h'),

                # Supply information
                circulating_supply=item.get('circulating_supply'),
                total_supply=item.get('total_supply'),
                max_supply=item.get('max_supply'),

                # Price changes
                price_change_24h=item.get('price_change_24h'),
                price_change_percentage_24h=item.get('price_change_percentage_24h'),
                price_change_percentage_7d=item.get('price_change_percentage_7d'),
                price_change_percentage_30d=item.get('price_change_percentage_30d'),

                # Market metrics
                market_cap=item.get('market_cap'),
                market_cap_change_24h=item.get('market_cap_change_24h'),
                market_cap_change_percentage_24h=item.get('market_cap_change_percentage_24h'),

                # Volume and trading
                total_volume_24h=item.get('total_volume_24h'),
                volume_change_24h=item.get('volume_change_24h'),

                # Historical context
                ath=item.get('ath'),
                ath_change_percentage=item.get('ath_change_percentage'),
                ath_date=item.get('ath_date'),
                atl=item.get('atl'),
                atl_change_percentage=item.get('atl_change_percentage'),
                atl_date=item.get('atl_date'),

                # Additional metadata
                last_updated=item.get('last_updated'),
                sparkline_7d=item.get('sparkline_7d'),

                is_active=item.get('is_active', True),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )
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

                        # CoinGecko API fields - Comprehensive market data
                        symbol=item.get('symbol'),
                        image=item.get('image'),
                        market_cap_rank=item.get('market_cap_rank'),

                        # Price data
                        current_price=item.get('current_price'),
                        high_24h=item.get('high_24h'),
                        low_24h=item.get('low_24h'),

                        # Supply information
                        circulating_supply=item.get('circulating_supply'),
                        total_supply=item.get('total_supply'),
                        max_supply=item.get('max_supply'),

                        # Price changes
                        price_change_24h=item.get('price_change_24h'),
                        price_change_percentage_24h=item.get('price_change_percentage_24h'),
                        price_change_percentage_7d=item.get('price_change_percentage_7d'),
                        price_change_percentage_30d=item.get('price_change_percentage_30d'),

                        # Market metrics
                        market_cap=item.get('market_cap'),
                        market_cap_change_24h=item.get('market_cap_change_24h'),
                        market_cap_change_percentage_24h=item.get('market_cap_change_percentage_24h'),

                        # Volume and trading
                        total_volume_24h=item.get('total_volume_24h'),
                        volume_change_24h=item.get('volume_change_24h'),

                        # Historical context
                        ath=item.get('ath'),
                        ath_change_percentage=item.get('ath_change_percentage'),
                        ath_date=item.get('ath_date'),
                        atl=item.get('atl'),
                        atl_change_percentage=item.get('atl_change_percentage'),
                        atl_date=item.get('atl_date'),

                        # Additional metadata
                        last_updated=item.get('last_updated'),
                        sparkline_7d=item.get('sparkline_7d'),

                        is_active=item.get('is_active', True),
                        created_at=datetime.fromisoformat(item.get('created_at', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(item.get('updated_at', datetime.utcnow().isoformat()))
                    )
                    assets.append(asset)

            return assets

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get all assets: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving all assets: {str(e)}")

    def get_assets_by_category(self, category: str) -> List[Asset]:
        """Get assets by category"""
        try:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Getting assets by category: '{category}'"
            )

            # Scan with filter expression
            response = self.table.scan(
                FilterExpression=Attr('category').eq(category.lower())
            )
            items = response.get('Items', [])

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Found {len(items)} assets in category '{category}'"
            )

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

                        # CoinGecko API fields - Comprehensive market data
                        symbol=item.get('symbol'),
                        image=item.get('image'),
                        market_cap_rank=item.get('market_cap_rank'),

                        # Price data
                        current_price=item.get('current_price'),
                        high_24h=item.get('high_24h'),
                        low_24h=item.get('low_24h'),

                        # Supply information
                        circulating_supply=item.get('circulating_supply'),
                        total_supply=item.get('total_supply'),
                        max_supply=item.get('max_supply'),

                        # Price changes
                        price_change_24h=item.get('price_change_24h'),
                        price_change_percentage_24h=item.get('price_change_percentage_24h'),
                        price_change_percentage_7d=item.get('price_change_percentage_7d'),
                        price_change_percentage_30d=item.get('price_change_percentage_30d'),

                        # Market metrics
                        market_cap=item.get('market_cap'),
                        market_cap_change_24h=item.get('market_cap_change_24h'),
                        market_cap_change_percentage_24h=item.get('market_cap_change_percentage_24h'),

                        # Volume and trading
                        total_volume_24h=item.get('total_volume_24h'),
                        volume_change_24h=item.get('volume_change_24h'),

                        # Historical context
                        ath=item.get('ath'),
                        ath_change_percentage=item.get('ath_change_percentage'),
                        ath_date=item.get('ath_date'),
                        atl=item.get('atl'),
                        atl_change_percentage=item.get('atl_change_percentage'),
                        atl_date=item.get('atl_date'),

                        # Additional metadata
                        last_updated=item.get('last_updated'),
                        sparkline_7d=item.get('sparkline_7d'),

                        is_active=item.get('is_active', True),
                        created_at=datetime.fromisoformat(item.get('created_at', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(item.get('updated_at', datetime.utcnow().isoformat()))
                    )
                    assets.append(asset)

            return assets

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get assets by category '{category}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving assets by category '{category}': {str(e)}")

    def get_all_assets_sorted_by_rank(self, active_only: bool = False) -> List[Asset]:
        """Get all assets sorted by market cap rank for frontend display"""
        try:
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Getting all assets sorted by market cap rank, active_only: {active_only}"
            )

            # Get all assets first
            assets = self.get_all_assets(active_only=active_only)

            # Sort by market cap rank (None values go to the end)
            def sort_key(asset):
                rank = asset.market_cap_rank
                return rank if rank is not None else float('inf')

            sorted_assets = sorted(assets, key=sort_key)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Returning {len(sorted_assets)} assets sorted by market cap rank"
            )

            return sorted_assets

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get assets sorted by rank: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving assets sorted by rank: {str(e)}")

    def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> Asset:
        try:
            updates = {}
            for field in [
                'name', 'asset_id',  # Add missing core fields
                'description', 'category', 'amount', 'price_usd', 'is_active',

                # CoinGecko API fields - Comprehensive market data
                'symbol', 'image', 'market_cap_rank',

                # Price data
                'current_price', 'high_24h', 'low_24h',

                # Supply information
                'circulating_supply', 'total_supply', 'max_supply',

                # Price changes
                'price_change_24h', 'price_change_percentage_24h',
                'price_change_percentage_7d', 'price_change_percentage_30d',

                # Market metrics
                'market_cap', 'market_cap_change_24h', 'market_cap_change_percentage_24h',

                # Volume and trading
                'total_volume_24h', 'volume_change_24h',

                # Historical context
                'ath', 'ath_change_percentage', 'ath_date',
                'atl', 'atl_change_percentage', 'atl_date',

                # Additional metadata
                'last_updated', 'sparkline_7d'
            ]:
                value = getattr(asset_update, field, None)
                if value is not None:
                    updates[field] = value
            if not updates:
                return self.get_asset_by_id(asset_id)
            set_clauses = []
            expression_values = {}
            for field, value in updates.items():
                set_clauses.append(f"{field} = :{field}")
                expression_values[f":{field}"] = value
            set_clauses.append("updated_at = :updated_at")
            expression_values[":updated_at"] = datetime.utcnow().isoformat()
            update_expression = "SET " + ", ".join(set_clauses)
            key = {'product_id': asset_id}
            item = self._safe_update_item(
                self.table,
                key,
                update_expression,
                expression_values
            )

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Asset updated successfully: id={asset_id}, fields_updated={list(updates.keys())}"
            )

            return Asset(
                asset_id=item.get('asset_id', asset_id),
                name=item.get('name', ''),  # Use safe get with default
                description=item.get('description', ''),
                category=item.get('category', 'unknown'),  # Use safe get with default
                amount=float(item.get('amount', 0)),
                price_usd=float(item.get('price_usd', 0)),

                # CoinGecko API fields - Comprehensive market data
                symbol=item.get('symbol'),
                image=item.get('image'),
                market_cap_rank=item.get('market_cap_rank'),

                # Price data
                current_price=item.get('current_price'),
                high_24h=item.get('high_24h'),
                low_24h=item.get('low_24h'),

                # Supply information
                circulating_supply=item.get('circulating_supply'),
                total_supply=item.get('total_supply'),
                max_supply=item.get('max_supply'),

                # Price changes
                price_change_24h=item.get('price_change_24h'),
                price_change_percentage_24h=item.get('price_change_percentage_24h'),
                price_change_percentage_7d=item.get('price_change_percentage_7d'),
                price_change_percentage_30d=item.get('price_change_percentage_30d'),

                # Market metrics
                market_cap=item.get('market_cap'),
                market_cap_change_24h=item.get('market_cap_change_24h'),
                market_cap_change_percentage_24h=item.get('market_cap_change_percentage_24h'),

                # Volume and trading
                total_volume_24h=item.get('total_volume_24h'),
                volume_change_24h=item.get('volume_change_24h'),

                # Historical context
                ath=item.get('ath'),
                ath_change_percentage=item.get('ath_change_percentage'),
                ath_date=item.get('ath_date'),
                atl=item.get('atl'),
                atl_change_percentage=item.get('atl_change_percentage'),
                atl_date=item.get('atl_date'),

                # Additional metadata
                last_updated=item.get('last_updated'),
                sparkline_7d=item.get('sparkline_7d'),

                is_active=item.get('is_active', True),
                created_at=datetime.fromisoformat(item.get('created_at', datetime.utcnow().isoformat())),  # Use safe get with default
                updated_at=datetime.fromisoformat(item.get('updated_at', datetime.utcnow().isoformat()))  # Use safe get with default
            )
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to update asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating asset '{asset_id}': {str(e)}")

    def delete_asset(self, asset_id: str) -> bool:
        """Delete asset by asset_id"""
        try:
            key = {
                'product_id': asset_id  # Using existing table schema
            }

            success = self._safe_delete_item(self.table, key)

            if success:
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Asset deleted successfully: {asset_id}"
                )

            return success

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to delete asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while deleting asset '{asset_id}': {str(e)}")

    def update_asset_price(self, asset_id: str, new_price: float) -> Asset:
        """Update only the price of an asset (convenience method)"""
        try:
            asset_update = AssetUpdate(price_usd=new_price)

            # If price is 0, automatically set is_active to False
            if new_price == 0:
                asset_update.is_active = False

            return self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to update price for asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating price for asset '{asset_id}': {str(e)}")

    def update_asset_amount(self, asset_id: str, new_amount: float) -> Asset:
        """Update only the amount of an asset (convenience method for inventory management)"""
        try:
            asset_update = AssetUpdate(amount=new_amount)
            return self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to update amount for asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating amount for asset '{asset_id}': {str(e)}")

    def deactivate_asset(self, asset_id: str) -> Asset:
        """Deactivate an asset (convenience method)"""
        try:
            asset_update = AssetUpdate(is_active=False)
            return self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to deactivate asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while deactivating asset '{asset_id}': {str(e)}")

    def activate_asset(self, asset_id: str) -> Asset:
        """Activate an asset (convenience method)"""
        try:
            asset_update = AssetUpdate(is_active=True)
            return self.update_asset(asset_id, asset_update)

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to activate asset '{asset_id}': {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while activating asset '{asset_id}': {str(e)}")

    def get_asset_stats(self) -> Dict[str, Any]:
        """Get summary statistics about assets"""
        try:
            all_assets = self.get_all_assets()
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
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to get asset stats: {e}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving asset statistics: {str(e)}")