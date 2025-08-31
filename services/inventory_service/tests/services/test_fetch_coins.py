"""
Unit tests for fetch_coins service
Path: services/inventory-service/tests/services/test_fetch_coins.py
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from services.fetch_coins import (
    fetch_coins,
    _fetch_from_coingecko,
    _map_coingecko_to_our_format
)
from decimal import Decimal


class TestFetchCoins:
    """Test the main fetch_coins function"""

    @pytest.mark.asyncio
    async def test_fetch_coins_success(self):
        """Test successful coin fetching from CoinGecko"""
        mock_coins = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap_rank": 1
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_coins) as mock_fetch:
            result = await fetch_coins()

            assert len(result) == 1
            assert result[0]["symbol"] == "BTC"  # Should be uppercase
            assert result[0]["name"] == "Bitcoin"
            assert result[0]["current_price"] == 45000.0
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_coins_coingecko_failure(self):
        """Test fallback when CoinGecko fails"""
        with patch('services.fetch_coins._fetch_from_coingecko', side_effect=Exception("API Error")):
            result = await fetch_coins()

            assert result == []
            # Should log error about all providers failing

    @pytest.mark.asyncio
    async def test_fetch_coins_empty_response(self):
        """Test handling of empty response from CoinGecko"""
        with patch('services.fetch_coins._fetch_from_coingecko', return_value=[]):
            result = await fetch_coins()

            assert result == []


class TestFetchFromCoinGecko:
    """Test the CoinGecko API fetching function"""

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_success(self):
        """Test successful API call to CoinGecko"""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
        ]
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await _fetch_from_coingecko()

            assert len(result) == 1
            assert result[0]["id"] == "bitcoin"
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_timeout(self):
        """Test handling of timeout exception"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.side_effect = httpx.TimeoutException("Request timed out")

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_http_error(self):
        """Test handling of HTTP status error"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_general_exception(self):
        """Test handling of general exceptions"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.side_effect = Exception("Network error")

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_client_context_manager(self):
        """Test that AsyncClient is used as context manager"""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            await _fetch_from_coingecko()

            mock_client_class.return_value.__aenter__.assert_called_once()
            mock_client_class.return_value.__aexit__.assert_called_once()


class TestMapCoinGeckoToOurFormat:
    """Test the CoinGecko data mapping function"""

    def test_map_coingecko_to_our_format_basic_fields(self):
        """Test basic field mapping"""
        coingecko_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap_rank": 1
            }
        ]

        result = _map_coingecko_to_our_format(coingecko_coins)

        assert len(result) == 1
        coin = result[0]
        assert coin["symbol"] == "BTC"  # Should be uppercase
        assert coin["name"] == "Bitcoin"
        assert coin["current_price"] == Decimal('45000.0')
        assert coin["price_usd"] == Decimal('45000.0')  # Should copy current_price
        assert coin["market_cap_rank"] == 1

    def test_map_coingecko_to_our_format_all_fields(self):
        """Test mapping of all available fields"""
        coingecko_coin = {
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3000.0,
            "image": "https://example.com/eth.png",
            "market_cap_rank": 2,
            "high_24h": 3100.0,
            "low_24h": 2900.0,
            "circulating_supply": 120000000,
            "total_supply": 120000000,
            "max_supply": 120000000,
            "price_change_24h": 100.0,
            "price_change_percentage_24h": 3.33,
            "price_change_percentage_7d": 5.0,
            "price_change_percentage_30d": 10.0,
            "market_cap": 360000000000,
            "market_cap_change_24h": 12000000000,
            "market_cap_change_percentage_24h": 3.33,
            "total_volume": 15000000000,
            "volume_change_24h": 2000000000,
            "ath": 5000.0,
            "ath_change_percentage": -40.0,
            "ath_date": "2021-11-10T14:24:11.849Z",
            "atl": 0.432979,
            "atl_change_percentage": 692.0,
            "atl_date": "2015-10-20T00:00:00.000Z",
            "last_updated": "2024-01-15T12:00:00.000Z",
            "sparkline_7d": {"price": [2800, 2850, 2900, 3000]}
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]

        # Check all mapped fields
        assert coin["symbol"] == "ETH"
        assert coin["name"] == "Ethereum"
        assert coin["current_price"] == Decimal('3000.0')
        assert coin["price_usd"] == Decimal('3000.0')
        assert coin["image"] == "https://example.com/eth.png"
        assert coin["market_cap_rank"] == 2
        assert coin["high_24h"] == Decimal('3100.0')
        assert coin["low_24h"] == Decimal('2900.0')
        assert coin["circulating_supply"] == Decimal('120000000')
        assert coin["total_supply"] == Decimal('120000000')
        assert coin["max_supply"] == Decimal('120000000')
        assert coin["price_change_24h"] == Decimal('100.0')
        assert coin["price_change_percentage_24h"] == Decimal('3.33')
        assert coin["price_change_percentage_7d"] == Decimal('5.0')
        assert coin["price_change_percentage_30d"] == Decimal('10.0')
        assert coin["market_cap"] == Decimal('360000000000')
        assert coin["market_cap_change_24h"] == Decimal('12000000000')
        assert coin["market_cap_change_percentage_24h"] == Decimal('3.33')
        assert coin["total_volume_24h"] == Decimal('15000000000')
        assert coin["volume_change_24h"] == Decimal('2000000000')
        assert coin["ath"] == Decimal('5000.0')
        assert coin["ath_change_percentage"] == Decimal('-40.0')
        assert coin["ath_date"] == "2021-11-10T14:24:11.849Z"
        assert coin["atl"] == Decimal('0.432979')
        assert coin["atl_change_percentage"] == Decimal('692.0')
        assert coin["atl_date"] == "2015-10-20T00:00:00.000Z"
        assert coin["last_updated"] == "2024-01-15T12:00:00.000Z"
        assert coin["sparkline_7d"] == {"price": [2800, 2850, 2900, 3000]}

    def test_map_coingecko_to_our_format_missing_fields(self):
        """Test handling of missing fields"""
        coingecko_coin = {
            "symbol": "btc",
            "name": "Bitcoin"
            # Missing most fields
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]

        # Should have default values for missing fields
        assert coin["symbol"] == "BTC"
        assert coin["name"] == "Bitcoin"
        assert coin["current_price"] is None
        assert coin["price_usd"] is None
        assert coin["image"] is None
        assert coin["market_cap_rank"] is None

    def test_map_coingecko_to_our_format_empty_list(self):
        """Test handling of empty coin list"""
        result = _map_coingecko_to_our_format([])
        assert result == []

    def test_map_coingecko_to_our_format_none_values(self):
        """Test handling of None values in fields"""
        coingecko_coin = {
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": None,
            "market_cap_rank": None
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]
        assert coin["current_price"] is None
        assert coin["price_usd"] is None
        assert coin["market_cap_rank"] is None

    def test_map_coingecko_to_our_format_special_characters(self):
        """Test handling of special characters in names"""
        coingecko_coin = {
            "symbol": "doge",
            "name": "Dogecoin 🐕",
            "current_price": 0.08
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]
        assert coin["symbol"] == "DOGE"
        assert coin["name"] == "Dogecoin 🐕"
        assert coin["current_price"] == Decimal('0.08')


class TestIntegrationScenarios:
    """Test integration scenarios"""

    @pytest.mark.asyncio
    async def test_full_fetch_and_map_flow(self):
        """Test the complete flow from API call to mapped result"""
        mock_coins = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap_rank": 1,
                "image": "https://example.com/btc.png"
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0,
                "market_cap_rank": 2,
                "image": "https://example.com/eth.png"
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_coins):
            result = await fetch_coins()

            assert len(result) == 2

            # Check first coin
            btc = result[0]
            assert btc["symbol"] == "BTC"
            assert btc["name"] == "Bitcoin"
            assert btc["current_price"] == Decimal('45000.0')
            assert btc["image"] == "https://example.com/btc.png"

            # Check second coin
            eth = result[1]
            assert eth["symbol"] == "ETH"
            assert eth["name"] == "Ethereum"
            assert eth["current_price"] == Decimal('3000.0')
            assert eth["image"] == "https://example.com/eth.png"

    @pytest.mark.asyncio
    async def test_error_handling_flow(self):
        """Test error handling in the complete flow"""
        with patch('services.fetch_coins._fetch_from_coingecko', side_effect=httpx.TimeoutException("Timeout")):
            result = await fetch_coins()
            assert result == []

    @pytest.mark.asyncio
    async def test_mixed_success_and_failure(self):
        """Test scenario where some operations succeed and others fail"""
        # First call succeeds, second fails
        mock_coins = [{"symbol": "btc", "name": "Bitcoin", "current_price": 45000.0}]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_coins):
            result = await fetch_coins()
            assert len(result) == 1
            assert result[0]["symbol"] == "BTC"
