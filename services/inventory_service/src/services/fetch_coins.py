"""
Coin data fetching service for inventory service
Path: services/inventory-service/src/services/fetch_coins.py

Simple service to fetch coin data with fallback providers
"""
import asyncio
import httpx
from typing import List, Dict, Any, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field, AfterValidator
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import COINGECKO_API_URL, COINGECKO_DEFAULT_PARAMS, COINGECKO_TIMEOUT

logger = BaseLogger(Loggers.INVENTORY)


# Define reusable validated types
def validate_symbol(v: str) -> str:
    """Validate and normalize symbol"""
    if not v:
        raise ValueError("Symbol cannot be empty")
    return v.upper()


def validate_positive_decimal(v: Any) -> Decimal:
    """Validate positive decimal values"""
    if v is None:
        return Decimal("0")
    decimal_val = Decimal(str(v))
    if decimal_val < 0:
        raise ValueError("Value must be positive")
    return decimal_val


# Reusable type aliases
Symbol = Annotated[str, AfterValidator(validate_symbol)]
PositiveDecimal = Annotated[Decimal, AfterValidator(validate_positive_decimal)]


class CoinData(BaseModel):
    """Validated coin data from external API"""
    symbol: Symbol
    name: str = ""
    image: str | None = None
    current_price: PositiveDecimal | None = None
    market_cap_rank: int | None = None
    high_24h: PositiveDecimal | None = None
    low_24h: PositiveDecimal | None = None
    circulating_supply: PositiveDecimal | None = None
    total_supply: PositiveDecimal | None = None
    max_supply: PositiveDecimal | None = None
    price_change_24h: Decimal | None = None
    price_change_percentage_24h: Decimal | None = None
    price_change_percentage_7d: Decimal | None = None
    price_change_percentage_30d: Decimal | None = None
    market_cap: PositiveDecimal | None = None
    market_cap_change_24h: Decimal | None = None
    market_cap_change_percentage_24h: Decimal | None = None
    total_volume_24h: PositiveDecimal | None = None
    volume_change_24h: Decimal | None = None
    ath: PositiveDecimal | None = None
    ath_change_percentage: Decimal | None = None
    ath_date: str | None = None
    atl: PositiveDecimal | None = None
    atl_change_percentage: Decimal | None = None
    atl_date: str | None = None
    last_updated: str | None = None
    sparkline_7d: Dict[str, Any] | None = None
    price_usd: PositiveDecimal | None = None

    class Config:
        extra = "ignore"


def _convert_to_decimal(value: Any) -> Any:
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(value, float):
        return Decimal(str(value))
    return value


async def fetch_coins() -> List[CoinData]:
    """Fetch coins with fallback providers - returns validated coin data objects"""

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


def _map_coingecko_to_our_format(coins: List[Dict[str, Any]]) -> List[CoinData]:
    """Map CoinGecko fields to our coin format and return validated CoinData objects"""
    mapped_coins = []

    for coin in coins:
        try:
            # Create CoinData object directly - validation happens in the constructor
            coin_data = CoinData(
                # Our standard fields
                symbol=coin.get("symbol", ""),
                name=coin.get("name", ""),
                current_price=_convert_to_decimal(coin.get("current_price")),
                price_usd=_convert_to_decimal(coin.get("current_price")) if coin.get("current_price") is not None else None,

                # CoinGecko fields mapped to our names
                image=coin.get("image"),
                market_cap_rank=coin.get("market_cap_rank"),
                high_24h=_convert_to_decimal(coin.get("high_24h")),
                low_24h=_convert_to_decimal(coin.get("low_24h")),
                circulating_supply=_convert_to_decimal(coin.get("circulating_supply")),
                total_supply=_convert_to_decimal(coin.get("total_supply")),
                max_supply=_convert_to_decimal(coin.get("max_supply")),
                price_change_24h=_convert_to_decimal(coin.get("price_change_24h")),
                price_change_percentage_24h=_convert_to_decimal(coin.get("price_change_percentage_24h")),
                price_change_percentage_7d=_convert_to_decimal(coin.get("price_change_percentage_7d")),
                price_change_percentage_30d=_convert_to_decimal(coin.get("price_change_percentage_30d")),
                market_cap=_convert_to_decimal(coin.get("market_cap")),
                market_cap_change_24h=_convert_to_decimal(coin.get("market_cap_change_24h")),
                market_cap_change_percentage_24h=_convert_to_decimal(coin.get("market_cap_change_percentage_24h")),
                total_volume_24h=_convert_to_decimal(coin.get("total_volume")),
                volume_change_24h=_convert_to_decimal(coin.get("volume_change_24h")),
                ath=_convert_to_decimal(coin.get("ath")),
                ath_change_percentage=_convert_to_decimal(coin.get("ath_change_percentage")),
                ath_date=coin.get("ath_date"),
                atl=_convert_to_decimal(coin.get("atl")),
                atl_change_percentage=_convert_to_decimal(coin.get("atl_change_percentage")),
                atl_date=coin.get("atl_date"),
                last_updated=coin.get("last_updated"),
                sparkline_7d=coin.get("sparkline_7d")
            )
            mapped_coins.append(coin_data)
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to validate coin data for {coin.get('symbol', 'UNKNOWN')}: {e}"
            )
            continue

    return mapped_coins

if __name__ == "__main__":
    async def test():
        coins = await fetch_coins()
        logger.info(action=LogActions.REQUEST_END, message=f"Fetched {len(coins)} coins")
        if coins:
            logger.info(action=LogActions.REQUEST_END, message=f"First coin: {coins[0].symbol} - {coins[0].name}")

    asyncio.run(test())
