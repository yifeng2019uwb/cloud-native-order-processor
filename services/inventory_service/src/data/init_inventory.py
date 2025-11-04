"""
Initialize sample inventory data on service startup
Path: services/inventory-service/src/data/init_inventory.py

This module handles:
1. One-time inventory initialization on service startup
2. Continuous price updates every 5 minutes (FEATURE-001.1)
"""
import asyncio
from decimal import Decimal
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field, AfterValidator

from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.database.dynamodb_connection import get_dynamodb_manager
from common.data.database.redis_connection import get_redis_client
from common.data.entities.inventory import Asset
from common.exceptions import CNOPEntityNotFoundException, CNOPAssetNotFoundException
from common.shared.logging import BaseLogger, LoggerName, LogAction
from constants import (
    DEFAULT_ASSET_AMOUNT,
    DEFAULT_ASSET_CATEGORY,
    PRICE_UPDATE_INTERVAL_SECONDS,
    PRICE_REDIS_TTL_SECONDS
)
from services.fetch_coins import CoinData, fetch_coins

logger = BaseLogger(LoggerName.INVENTORY)


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
                action=LogAction.DB_OPERATION,
                message=f"Processing coin: {asset.asset_id}, current_price: {coin.current_price}"
            )

            try:
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Checking if asset exists: {asset.asset_id}"
                )
                existing_asset = asset_dao.get_asset_by_id(asset.asset_id)
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Asset exists, updating: {asset.asset_id}"
                )
                asset_dao.update_asset(asset)
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Updated asset: {asset.asset_id}"
                )
            except (CNOPEntityNotFoundException, CNOPAssetNotFoundException):
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Asset doesn't exist, creating: {asset.asset_id}"
                )
                asset_dao.create_asset(asset)
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"Created asset: {asset.asset_id}"
                )
            except Exception as e:
                logger.error(
                    action=LogAction.ERROR,
                    message=f"Database operation failed for {asset.asset_id}: {e}"
                )
                continue

            updated_count += 1

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to upsert asset {coin.symbol}: {e}"
            )
            continue

    return updated_count


async def startup_inventory_initialization() -> None:
    """
    Start continuous inventory data synchronization service

    This function runs continuously to keep inventory data synced with CoinGecko.
    Uses upsert pattern: updates existing coins, creates new ones.
    Simulates real-time inventory system with 5-minute sync interval.

    Design: Simple continuous loop - no separate "init" needed since upsert handles both
    """
    logger.info(
        action=LogAction.SERVICE_START,
        message=f"Starting continuous inventory data sync (interval: {PRICE_UPDATE_INTERVAL_SECONDS}s)"
    )

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.info(
                action=LogAction.SERVICE_START,
                message=f"Inventory sync cycle #{cycle_count} starting..."
            )

            # Run update cycle (fetches from CoinGecko, upserts to DynamoDB, updates Redis)
            success = await price_update_cycle()

            if success:
                logger.info(
                    action=LogAction.SERVICE_START,
                    message=f"Inventory sync cycle #{cycle_count} completed successfully"
                )
            else:
                logger.warning(
                    action=LogAction.ERROR,
                    message=f"Inventory sync cycle #{cycle_count} failed (will retry in {PRICE_UPDATE_INTERVAL_SECONDS}s)"
                )

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Unexpected error in inventory sync loop (cycle #{cycle_count}): {e}"
            )

        # Sleep for configured interval (default: 300 seconds = 5 minutes)
        logger.info(
            action=LogAction.SERVICE_START,
            message=f"Next sync in {PRICE_UPDATE_INTERVAL_SECONDS}s..."
        )
        await asyncio.sleep(PRICE_UPDATE_INTERVAL_SECONDS)


# =============================================================================
# FEATURE-001.1: Continuous Price Updates (Every 5 Minutes)
# =============================================================================

async def update_redis_prices(coins: List[CoinData]) -> int:
    """
    Update Redis with current prices for all coins

    Redis Key Format: price:{asset_id} = "45000.00"
    TTL: 10 minutes (ensures data freshness)

    Args:
        coins: List of CoinData objects with current prices

    Returns:
        Number of prices successfully updated in Redis
    """
    redis_client = get_redis_client()
    updated_count = 0

    for coin in coins:
        try:
            # Only update if price is available
            if coin.current_price is None:
                logger.warning(
                    action=LogAction.CACHE_OPERATION,
                    message=f"Skipping Redis update for {coin.symbol} - no price available"
                )
                continue

            # Redis key format: price:BTC, price:ETH, etc.
            redis_key = f"price:{coin.symbol}"
            price_str = str(coin.current_price)

            # Set with TTL (10 minutes = 600 seconds)
            redis_client.setex(
                name=redis_key,
                time=PRICE_REDIS_TTL_SECONDS,
                value=price_str
            )

            logger.info(
                action=LogAction.CACHE_OPERATION,
                message=f"Updated Redis: {redis_key} = {price_str} (TTL: {PRICE_REDIS_TTL_SECONDS}s)"
            )
            updated_count += 1

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to update Redis price for {coin.symbol}: {e}"
            )
            continue

    return updated_count


async def price_update_cycle():
    """
    Single price update cycle

    Fetches prices from CoinGecko, updates DynamoDB and Redis
    Returns True if successful, False if failed
    """
    try:
        logger.info(
            action=LogAction.SERVICE_START,
            message="Starting price update cycle..."
        )

        # 1. Fetch latest prices from CoinGecko
        coins = await fetch_coins()

        if not coins:
            logger.error(
                action=LogAction.ERROR,
                message="No coins received from CoinGecko - skipping update cycle"
            )
            return False

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Fetched {len(coins)} coins from CoinGecko"
        )

        # 2. Update DynamoDB inventory table
        db_update_count = await upsert_coins_to_inventory(coins)
        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Updated {db_update_count} assets in DynamoDB"
        )

        # 3. Update Redis price cache (NEW for limit orders)
        redis_update_count = await update_redis_prices(coins)
        logger.info(
            action=LogAction.CACHE_OPERATION,
            message=f"Updated {redis_update_count} prices in Redis"
        )

        logger.info(
            action=LogAction.SERVICE_START,
            message=f"Price update cycle complete: DynamoDB={db_update_count}, Redis={redis_update_count}"
        )
        return True

    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Price update cycle failed: {e}"
        )
        return False
