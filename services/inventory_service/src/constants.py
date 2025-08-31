"""
Inventory Service Constants
Path: services/inventory-service/src/constants.py

This file contains essential constant values used across the inventory service
"""

# CoinGecko API Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_DEFAULT_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 250,  # Fetch top 250 coins (maximum allowed by free API)
    "page": 1,
    "sparkline": True,  # Enable sparkline data for 7-day charts
}
COINGECKO_TIMEOUT = 30.0  # seconds

# Default Asset Values
DEFAULT_ASSET_AMOUNT = 1000.0
DEFAULT_ASSET_CATEGORY = "altcoin"
