"""
Inventory Service Constants - Messages and configuration only
Path: services/inventory-service/src/constants.py

This file contains essential constant values used across the inventory service
"""

# =============================================================================
# RESPONSE FIELD NAMES (Keep as constants - used in JSON responses)
# =============================================================================
RESPONSE_FIELD_SERVICE = "service"
RESPONSE_FIELD_VERSION = "version"
RESPONSE_FIELD_STATUS = "status"
RESPONSE_FIELD_TIMESTAMP = "timestamp"
RESPONSE_FIELD_ENDPOINTS = "endpoints"
RESPONSE_FIELD_DOCS = "docs"
RESPONSE_FIELD_HEALTH = "health"
RESPONSE_FIELD_ASSETS = "assets"
RESPONSE_FIELD_ASSET_DETAIL = "asset_detail"
RESPONSE_FIELD_METRICS = "metrics"

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

# Price Update Configuration (for FEATURE-001.1)
PRICE_UPDATE_INTERVAL_SECONDS = 300  # 5 minutes - how often to fetch prices from CoinGecko
PRICE_REDIS_TTL_SECONDS = 600  # 10 minutes - Redis key expiration time (2x update interval for safety)
