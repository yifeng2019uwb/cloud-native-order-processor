"""
Coin data fetching service for inventory service
Path: services/inventory-service/src/services/fetch_coins.py

Simple service to fetch coin data with fallback providers
"""
import asyncio
import httpx
from typing import List, Dict, Any
from decimal import Decimal
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import COINGECKO_API_URL, COINGECKO_DEFAULT_PARAMS, COINGECKO_TIMEOUT

logger = BaseLogger(Loggers.INVENTORY)


def _convert_to_decimal(value: Any) -> Any:
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(value, float):
        return Decimal(str(value))
    return value


async def fetch_coins() -> List[Dict[str, Any]]:
    """Fetch coins with fallback providers - returns mapped coin data"""

    # Try CoinGecko first
    try:
        coins = await _fetch_from_coingecko()
        if coins:
            logger.info(action=LogActions.REQUEST_START, message=f"Fetched {len(coins)} coins from CoinGecko")
            return _map_coingecko_to_our_format(coins)
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"CoinGecko failed: {e}")

    logger.error(action=LogActions.ERROR, message="All coin providers failed")
    return []


async def _fetch_from_coingecko() -> List[Dict[str, Any]]:
    """Fetch from CoinGecko API"""
    try:
        logger.info(action=LogActions.REQUEST_START, message="Starting CoinGecko API call...")

        async with httpx.AsyncClient(timeout=COINGECKO_TIMEOUT) as client:
            response = await client.get(COINGECKO_API_URL, params=COINGECKO_DEFAULT_PARAMS)
            response.raise_for_status()
            coins = response.json()

            logger.info(action=LogActions.REQUEST_END, message=f"CoinGecko API call successful, received {len(coins)} coins")
            return coins

    except httpx.TimeoutException:
        logger.error(action=LogActions.ERROR, message="CoinGecko API call timed out")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(action=LogActions.ERROR, message=f"CoinGecko API HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"CoinGecko API call failed: {e}")
        return []


def _map_coingecko_to_our_format(coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map CoinGecko fields to our coin format"""
    mapped_coins = []

    for coin in coins:
        mapped_coin = {
            # Our standard fields
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name", ""),
            "current_price": _convert_to_decimal(coin.get("current_price")),
            "price_usd": _convert_to_decimal(coin.get("current_price")),

            # CoinGecko fields mapped to our names
            "image": coin.get("image"),
            "market_cap_rank": coin.get("market_cap_rank"),  # Integer, no conversion needed
            "high_24h": _convert_to_decimal(coin.get("high_24h")),
            "low_24h": _convert_to_decimal(coin.get("low_24h")),
            "circulating_supply": _convert_to_decimal(coin.get("circulating_supply")),
            "total_supply": _convert_to_decimal(coin.get("total_supply")),
            "max_supply": _convert_to_decimal(coin.get("max_supply")),
            "price_change_24h": _convert_to_decimal(coin.get("price_change_24h")),
            "price_change_percentage_24h": _convert_to_decimal(coin.get("price_change_percentage_24h")),
            "price_change_percentage_7d": _convert_to_decimal(coin.get("price_change_percentage_7d")),
            "price_change_percentage_30d": _convert_to_decimal(coin.get("price_change_percentage_30d")),
            "market_cap": _convert_to_decimal(coin.get("market_cap")),
            "market_cap_change_24h": _convert_to_decimal(coin.get("market_cap_change_24h")),
            "market_cap_change_percentage_24h": _convert_to_decimal(coin.get("market_cap_change_percentage_24h")),
            "total_volume_24h": _convert_to_decimal(coin.get("total_volume")),
            "volume_change_24h": _convert_to_decimal(coin.get("volume_change_24h")),
            "ath": _convert_to_decimal(coin.get("ath")),
            "ath_change_percentage": _convert_to_decimal(coin.get("ath_change_percentage")),
            "ath_date": coin.get("ath_date"),  # String, no conversion needed
            "atl": _convert_to_decimal(coin.get("atl")),
            "atl_change_percentage": _convert_to_decimal(coin.get("atl_change_percentage")),
            "atl_date": coin.get("atl_date"),  # String, no conversion needed
            "last_updated": coin.get("last_updated"),  # String, no conversion needed
            "sparkline_7d": coin.get("sparkline_7d")  # Dict, no conversion needed
        }
        mapped_coins.append(mapped_coin)

    return mapped_coins

if __name__ == "__main__":
    async def test():
        coins = await fetch_coins()
        print(f"Fetched {len(coins)} coins")
        if coins:
            print(f"First coin: {coins[0]}")

    asyncio.run(test())
