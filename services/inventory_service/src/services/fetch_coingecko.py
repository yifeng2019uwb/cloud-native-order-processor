import httpx
import asyncio
from common.shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.INVENTORY)

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": False,
}

async def fetch_top_coins():
    """Fetch top coins from CoinGecko with timeout and error handling"""
    try:
        # This doesn't block other requests
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(COINGECKO_API, params=PARAMS)
            response.raise_for_status()
            coins = response.json()
            logger.info(action=LogActions.REQUEST_START, message=f"Fetched {len(coins)} coins from CoinGecko")
            for coin in coins[:5]:  # Log first 5 for brevity
                logger.info(action=LogActions.REQUEST_START, message=f"{coin['market_cap_rank']}: {coin['name']} ({coin['symbol']}) - ${coin['current_price']}")
            return coins
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to fetch coins from CoinGecko: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(fetch_top_coins())