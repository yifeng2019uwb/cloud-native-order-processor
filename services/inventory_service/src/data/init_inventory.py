"""
Initialize sample inventory data on service startup
Path: services/inventory-service/src/data/init_inventory.py
"""
import asyncio
from decimal import Decimal
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field, AfterValidator

from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.database.dynamodb_connection import get_dynamodb_manager
from common.data.entities.inventory import Asset
from common.exceptions import CNOPEntityNotFoundException, CNOPAssetNotFoundException
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import DEFAULT_ASSET_AMOUNT, DEFAULT_ASSET_CATEGORY
from services.fetch_coins import CoinData

logger = BaseLogger(Loggers.INVENTORY)


def get_category(coin: dict) -> str:
    """Get category for coin - simplified to use default"""
    return DEFAULT_ASSET_CATEGORY



def coin_to_asset(coin: CoinData) -> Asset:
    """Convert validated coin data to Asset entity"""
    return Asset(
        asset_id=coin.symbol,
        name=coin.name,
        description=f"Digital asset: {coin.name}",
        category=DEFAULT_ASSET_CATEGORY,
        amount=Decimal(str(DEFAULT_ASSET_AMOUNT)),
        price_usd=coin.price_usd,
        is_active=True,
        symbol=coin.symbol,
        image=coin.image,
        market_cap_rank=coin.market_cap_rank,
        current_price=coin.current_price,
        high_24h=coin.high_24h,
        low_24h=coin.low_24h,
        circulating_supply=coin.circulating_supply,
        total_supply=coin.total_supply,
        max_supply=coin.max_supply,
        price_change_24h=coin.price_change_24h,
        price_change_percentage_24h=coin.price_change_percentage_24h,
        price_change_percentage_7d=coin.price_change_percentage_7d,
        price_change_percentage_30d=coin.price_change_percentage_30d,
        market_cap=coin.market_cap,
        market_cap_change_24h=coin.market_cap_change_24h,
        market_cap_change_percentage_24h=coin.market_cap_change_percentage_24h,
        total_volume_24h=coin.total_volume_24h,
        volume_change_24h=coin.volume_change_24h,
        ath=coin.ath,
        ath_change_percentage=coin.ath_change_percentage,
        ath_date=coin.ath_date,
        atl=coin.atl,
        atl_change_percentage=coin.atl_change_percentage,
        atl_date=coin.atl_date,
        last_updated=coin.last_updated,
        sparkline_7d=coin.sparkline_7d
    )


async def upsert_coins_to_inventory(coins: List[CoinData]) -> int:
    """Upsert coins data to inventory - update existing, create new"""
    updated_count = 0
    db_connection = get_dynamodb_manager().get_connection()
    asset_dao = AssetDAO(db_connection)

    for coin in coins:
        try:
            asset = coin_to_asset(coin)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Processing coin: {asset.asset_id}, current_price: {coin.current_price}"
            )

            try:
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Checking if asset exists: {asset.asset_id}"
                )
                existing_asset = asset_dao.get_asset_by_id(asset.asset_id)
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Asset exists, updating: {asset.asset_id}"
                )
                asset_dao.update_asset(asset)
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Updated asset: {asset.asset_id}"
                )
            except (CNOPEntityNotFoundException, CNOPAssetNotFoundException):
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Asset doesn't exist, creating: {asset.asset_id}"
                )
                asset_dao.create_asset(asset)
                logger.info(
                    action=LogActions.DB_OPERATION,
                    message=f"Created asset: {asset.asset_id}"
                )
            except Exception as e:
                logger.error(
                    action=LogActions.ERROR,
                    message=f"Database operation failed for {asset.asset_id}: {e}"
                )
                continue

            updated_count += 1

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to upsert asset {coin.symbol}: {e}"
            )
            continue

    return updated_count


async def initialize_inventory_data(force_recreate: bool = False) -> None:
    """Initialize inventory data on service startup by fetching from data providers"""
    logger.info(
        action=LogActions.SERVICE_START,
        message="Starting inventory data initialization..."
    )
    try:
        from services.fetch_coins import fetch_coins

        coins = await fetch_coins()
        if not coins:
            logger.error(
                action=LogActions.ERROR,
                message="No coins received from fetch service"
            )
            return

        count = await upsert_coins_to_inventory(coins)
        logger.info(
            action=LogActions.SERVICE_START,
            message=f"Successfully upserted {count} assets from data providers"
        )

    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Failed to initialize inventory data: {e}"
        )


async def startup_inventory_initialization() -> None:
    """
    Non-blocking startup initialization
    This function is designed to not block service startup
    """
    await initialize_inventory_data()