"""
Initialize sample inventory data on service startup
Path: services/inventory-service/src/data/init_inventory.py
"""
import logging
from typing import List
from decimal import Decimal
import httpx
import asyncio

from common.dao.inventory import AssetDAO
from common.entities.inventory import AssetCreate
from common.database.dynamodb_connection import dynamodb_manager

logger = logging.getLogger(__name__)

class Constants:
    COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"

    TOP_N_COINS = 100  # Change this value as needed
    PARAMS = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": TOP_N_COINS,
        "page": 1
    }
    CATEGORY_MAP = {
        # You can expand this mapping as needed
        "bitcoin": "major",
        "ethereum": "major",
        "binancecoin": "major",
        "tether": "stablecoin",
        "usd-coin": "stablecoin",
        "dai": "stablecoin",
        # fallback: altcoin
    }

def get_category(coin: dict) -> str:
    # Map CoinGecko id to category, fallback to altcoin
    return Constants.CATEGORY_MAP.get(coin.get("id"), "altcoin")

async def fetch_top_coins() -> List[dict]:
    """Fetch top coins from CoinGecko with timeout and error handling"""
    try:
        # This doesn't block other requests
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(Constants.COINGECKO_API, params=Constants.PARAMS)
            response.raise_for_status()
            coins = response.json()
            logger.info(f"Fetched {len(coins)} coins from CoinGecko.")
            return coins
    except Exception as e:
        logger.error(f"Failed to fetch coins from CoinGecko: {e}")
        return []

async def upsert_coins_to_inventory(coins: List[dict]) -> int:
    updated_count = 0
    async with dynamodb_manager.get_connection() as db_connection:
        asset_dao = AssetDAO(db_connection)
        for coin in coins:
            try:
                asset_id = coin["symbol"].upper()
                name = coin["name"]
                description = coin.get("description") or coin.get("id", "")
                category = get_category(coin)
                amount = Decimal("1000.0")  # Placeholder, can be dynamic
                price_usd = Decimal(str(coin["current_price"]))

                asset_create = AssetCreate(
                    asset_id=asset_id,
                    name=name,
                    description=description,
                    category=category,
                    amount=amount,
                    price_usd=price_usd
                )

                # Upsert: update if exists, else create
                existing_asset = await asset_dao.get_asset_by_id(asset_id)
                if existing_asset:
                    await asset_dao.update_asset(asset_id, asset_create)
                    logger.info(f"Updated asset: {asset_id} - {name}")
                else:
                    await asset_dao.create_asset(asset_create)
                    logger.info(f"Created asset: {asset_id} - {name}")
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to upsert asset {coin.get('symbol', '')}: {e}")
                continue
    return updated_count

async def initialize_inventory_data(force_recreate: bool = False) -> dict:
    """Initialize inventory data on service startup by fetching from CoinGecko"""
    logger.info("🚀 Starting inventory data initialization from CoinGecko...")
    try:
        coins = await fetch_top_coins()
        count = await upsert_coins_to_inventory(coins)
        logger.info(f"✅ Successfully upserted {count} assets from CoinGecko")
        return {
            "status": "success",
            "assets_upserted": count,
            "message": f"Successfully upserted {count} assets from CoinGecko"
        }
    except Exception as e:
        logger.error(f"❌ Failed to initialize inventory data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to initialize inventory data from CoinGecko"
        }

# Convenience function for startup
async def startup_inventory_initialization():
    """
    Non-blocking startup initialization
    This function is designed to not block service startup
    """
    return await initialize_inventory_data()