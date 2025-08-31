"""
Initialize sample inventory data on service startup
Path: services/inventory-service/src/data/init_inventory.py
"""
import asyncio
from decimal import Decimal
from typing import List
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.database.dynamodb_connection import dynamodb_manager
from common.data.entities.inventory import AssetCreate, AssetUpdate
from common.exceptions import CNOPEntityNotFoundException
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import DEFAULT_ASSET_AMOUNT, DEFAULT_ASSET_CATEGORY

# Initialize our standardized logger
logger = BaseLogger(Loggers.INVENTORY)

def get_category(coin: dict) -> str:
    """Get category for coin - simplified to use default"""
    return DEFAULT_ASSET_CATEGORY

async def upsert_coins_to_inventory(coins: List[dict]) -> int:
    """Upsert coins data to inventory - update existing, create new"""
    updated_count = 0
    db_connection = dynamodb_manager.get_connection()
    asset_dao = AssetDAO(db_connection)

    for coin in coins:
        try:
            asset_id = coin["symbol"].upper()

            # Only use the mapped fields from fetch_coins, not all original CoinGecko fields
            # This ensures all numeric values are properly converted to Decimal
            asset_update = AssetUpdate(
                asset_id=asset_id,  # Add the asset_id field
                symbol=coin.get("symbol"),
                name=coin.get("name"),
                current_price=coin.get("current_price"),
                price_usd=coin.get("price_usd"),
                image=coin.get("image"),
                market_cap_rank=coin.get("market_cap_rank"),
                high_24h=coin.get("high_24h"),
                low_24h=coin.get("low_24h"),
                circulating_supply=coin.get("circulating_supply"),
                total_supply=coin.get("total_supply"),
                max_supply=coin.get("max_supply"),
                price_change_24h=coin.get("price_change_24h"),
                price_change_percentage_24h=coin.get("price_change_percentage_24h"),
                price_change_percentage_7d=coin.get("price_change_percentage_7d"),
                price_change_percentage_30d=coin.get("price_change_percentage_30d"),
                market_cap=coin.get("market_cap"),
                market_cap_change_24h=coin.get("market_cap_change_24h"),
                market_cap_change_percentage_24h=coin.get("market_cap_change_percentage_24h"),
                total_volume_24h=coin.get("total_volume_24h"),
                volume_change_24h=coin.get("volume_change_24h"),
                ath=coin.get("ath"),
                ath_change_percentage=coin.get("ath_change_percentage"),
                ath_date=coin.get("ath_date"),
                atl=coin.get("atl"),
                atl_change_percentage=coin.get("atl_change_percentage"),
                atl_date=coin.get("atl_date"),
                last_updated=coin.get("last_updated"),
                sparkline_7d=coin.get("sparkline_7d"),
                is_active=True  # Ensure all coins from CoinGecko are marked as active
            )

            asset_dao.update_asset(asset_id, asset_update)
            logger.info(action=LogActions.DB_OPERATION, message=f"Upserted asset: {asset_id}")
            updated_count += 1

        except Exception as e:
            logger.error(action=LogActions.ERROR, message=f"Failed to upsert asset {coin.get('symbol', '')}: {e}")
            continue

    return updated_count

async def initialize_inventory_data(force_recreate: bool = False) -> dict:
    """Initialize inventory data on service startup by fetching from data providers"""
    logger.info(action=LogActions.SERVICE_START, message="Starting inventory data initialization...")
    try:
        # Import here to avoid circular imports
        from services.fetch_coins import fetch_coins

        coins = await fetch_coins()
        if not coins:
            logger.error(action=LogActions.ERROR, message="No coins received from fetch service")
            return {
                "status": "error",
                "error": "No coins received",
                "message": "Failed to fetch coins from data providers"
            }

        count = await upsert_coins_to_inventory(coins)
        logger.info(action=LogActions.SERVICE_START, message=f"Successfully upserted {count} assets from data providers")
        return {
            "status": "success",
            "assets_upserted": count,
            "message": f"Successfully upserted {count} assets from data providers"
        }
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to initialize inventory data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to initialize inventory data from data providers"
        }

# Convenience function for startup
async def startup_inventory_initialization():
    """
    Non-blocking startup initialization
    This function is designed to not block service startup
    """
    return await initialize_inventory_data()