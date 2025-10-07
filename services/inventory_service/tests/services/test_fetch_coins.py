"""
Unit tests for fetch_coins service
Path: services/inventory-service/tests/services/test_fetch_coins.py
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from decimal import Decimal

from services.fetch_coins import (
    fetch_coins,
    _fetch_from_coingecko,
    _map_coingecko_to_our_format,
    _convert_to_decimal,
    validate_symbol,
    validate_positive_decimal,
    CoinData
)


class TestValidationFunctions:
    """Test validation functions - these are pure functions, no mocking needed"""

    def test_validate_symbol_uppercase_conversion(self):
        """Test that symbols are converted to uppercase"""
        assert validate_symbol("btc") == "BTC"
        assert validate_symbol("eth") == "ETH"
        assert validate_symbol("BTC") == "BTC"

    def test_validate_symbol_empty_string_raises_error(self):
        """Test that empty string raises ValueError"""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            validate_symbol("")

    def test_validate_symbol_none_raises_error(self):
        """Test that None raises ValueError"""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            validate_symbol(None)

    def test_validate_positive_decimal_none_returns_zero(self):
        """Test that None returns Decimal('0')"""
        result = validate_positive_decimal(None)
        assert result == Decimal("0")
        assert isinstance(result, Decimal)

    def test_validate_positive_decimal_negative_raises_error(self):
        """Test that negative values raise ValueError"""
        with pytest.raises(ValueError, match="Value must be positive"):
            validate_positive_decimal(-100.0)

        with pytest.raises(ValueError, match="Value must be positive"):
            validate_positive_decimal(Decimal("-50"))

    def test_validate_positive_decimal_zero_allowed(self):
        """Test that zero is allowed"""
        result = validate_positive_decimal(0)
        assert result == Decimal("0")

    def test_validate_positive_decimal_positive_value(self):
        """Test positive decimal conversion"""
        assert validate_positive_decimal(100.0) == Decimal("100.0")
        assert validate_positive_decimal(0.5) == Decimal("0.5")
        assert validate_positive_decimal("123.45") == Decimal("123.45")

    def test_convert_to_decimal_float(self):
        """Test _convert_to_decimal converts floats to Decimal"""
        result = _convert_to_decimal(45000.0)
        assert result == Decimal("45000.0")
        assert isinstance(result, Decimal)

    def test_convert_to_decimal_non_float(self):
        """Test _convert_to_decimal returns non-floats as-is"""
        assert _convert_to_decimal(None) is None
        assert _convert_to_decimal("test") == "test"
        assert _convert_to_decimal(100) == 100


class TestCoinDataModel:
    """Test CoinData Pydantic model"""

    def test_coin_data_basic_creation(self):
        """Test creating CoinData with basic fields"""
        coin = CoinData(
            symbol="btc",
            name="Bitcoin",
            current_price=45000.0
        )

        assert coin.symbol == "BTC"  # Should be uppercase via validator
        assert coin.name == "Bitcoin"
        assert coin.current_price == Decimal("45000.0")

    def test_coin_data_with_all_fields(self):
        """Test CoinData with all possible fields"""
        coin = CoinData(
            symbol="eth",
            name="Ethereum",
            image="https://example.com/eth.png",
            current_price=3000.0,
            market_cap_rank=2,
            high_24h=3100.0,
            low_24h=2900.0,
            circulating_supply=120000000.0,
            total_supply=120000000.0,
            max_supply=120000000.0,
            price_change_24h=100.0,
            price_change_percentage_24h=3.33,
            price_change_percentage_7d=5.0,
            price_change_percentage_30d=10.0,
            market_cap=360000000000.0,
            total_volume_24h=15000000000.0,
            ath=5000.0,
            ath_change_percentage=-40.0,
            ath_date="2021-11-10",
            atl=0.43,
            atl_change_percentage=692.0,
            atl_date="2015-10-20",
            last_updated="2024-01-15",
            price_usd=3000.0
        )

        assert coin.symbol == "ETH"
        assert coin.market_cap_rank == 2
        assert isinstance(coin.current_price, Decimal)
        assert isinstance(coin.market_cap, Decimal)

    def test_coin_data_extra_fields_ignored(self):
        """Test that extra fields are ignored (Config: extra='ignore')"""
        coin = CoinData(
            symbol="btc",
            name="Bitcoin",
            current_price=45000.0,
            unknown_field="should be ignored"
        )

        assert coin.symbol == "BTC"
        assert not hasattr(coin, 'unknown_field')


class TestFetchFromCoinGecko:
    """Test the CoinGecko API fetching function"""

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_success(self):
        """Test successful API call to CoinGecko"""
        mock_response_data = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 45000.0},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3000.0}
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()  # No exception

        # Mock httpx.AsyncClient
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await _fetch_from_coingecko()

            assert len(result) == 2
            assert result[0]["id"] == "bitcoin"
            assert result[1]["id"] == "ethereum"
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_timeout(self):
        """Test handling of timeout exception"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_http_status_error(self):
        """Test handling of HTTP status errors"""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limited",
                request=MagicMock(),
                response=mock_response
            )
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_general_exception(self):
        """Test handling of general exceptions"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await _fetch_from_coingecko()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_from_coingecko_empty_response(self):
        """Test handling of empty response"""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await _fetch_from_coingecko()

            assert result == []


class TestMapCoinGeckoToOurFormat:
    """Test the CoinGecko data mapping function - no mocking needed, pure function"""

    def test_map_coingecko_basic_fields(self):
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
        assert coin.symbol == "BTC"  # Uppercase via validator
        assert coin.name == "Bitcoin"
        assert coin.current_price == Decimal('45000.0')
        assert coin.price_usd == Decimal('45000.0')  # Copied from current_price
        assert coin.market_cap_rank == 1

    def test_map_coingecko_all_fields(self):
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

        # Verify all fields are properly mapped and converted to Decimal where needed
        assert coin.symbol == "ETH"
        assert coin.name == "Ethereum"
        assert coin.current_price == Decimal('3000.0')
        assert coin.price_usd == Decimal('3000.0')
        assert coin.image == "https://example.com/eth.png"
        assert coin.market_cap_rank == 2
        assert coin.high_24h == Decimal('3100.0')
        assert coin.low_24h == Decimal('2900.0')
        assert coin.circulating_supply == Decimal('120000000')
        assert coin.total_supply == Decimal('120000000')
        assert coin.max_supply == Decimal('120000000')
        assert coin.price_change_24h == Decimal('100.0')
        assert coin.price_change_percentage_24h == Decimal('3.33')
        assert coin.price_change_percentage_7d == Decimal('5.0')
        assert coin.price_change_percentage_30d == Decimal('10.0')
        assert coin.market_cap == Decimal('360000000000')
        assert coin.market_cap_change_24h == Decimal('12000000000')
        assert coin.market_cap_change_percentage_24h == Decimal('3.33')
        assert coin.total_volume_24h == Decimal('15000000000')  # Note: mapped from total_volume
        assert coin.volume_change_24h == Decimal('2000000000')
        assert coin.ath == Decimal('5000.0')
        assert coin.ath_change_percentage == Decimal('-40.0')
        assert coin.ath_date == "2021-11-10T14:24:11.849Z"
        assert coin.atl == Decimal('0.432979')
        assert coin.atl_change_percentage == Decimal('692.0')
        assert coin.atl_date == "2015-10-20T00:00:00.000Z"
        assert coin.last_updated == "2024-01-15T12:00:00.000Z"
        assert coin.sparkline_7d == {"price": [2800, 2850, 2900, 3000]}

    def test_map_coingecko_missing_fields(self):
        """Test handling of missing/optional fields"""
        coingecko_coin = {
            "symbol": "btc",
            "name": "Bitcoin"
            # Most fields missing
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]
        assert coin.symbol == "BTC"
        assert coin.name == "Bitcoin"
        assert coin.current_price is None
        assert coin.price_usd is None
        assert coin.image is None
        assert coin.market_cap_rank is None

    def test_map_coingecko_none_values(self):
        """Test handling of explicit None values"""
        coingecko_coin = {
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": None,
            "max_supply": None,  # Some coins don't have max supply
            "market_cap_rank": None
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        coin = result[0]
        assert coin.current_price is None
        assert coin.price_usd is None
        assert coin.max_supply is None

    def test_map_coingecko_empty_list(self):
        """Test handling of empty coin list"""
        result = _map_coingecko_to_our_format([])
        assert result == []

    def test_map_coingecko_validation_error_skips_coin(self):
        """Test that coins with validation errors are skipped"""
        coingecko_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0
            },
            {
                "symbol": "",  # Invalid - empty symbol
                "name": "Invalid Coin",
                "current_price": 100.0
            },
            {
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0
            }
        ]

        result = _map_coingecko_to_our_format(coingecko_coins)

        # Should only return valid coins, skipping the invalid one
        assert len(result) == 2
        assert result[0].symbol == "BTC"
        assert result[1].symbol == "ETH"

    def test_map_coingecko_negative_price_validation(self):
        """Test that negative prices are caught by validation"""
        coingecko_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": -45000.0  # Invalid negative price
            }
        ]

        result = _map_coingecko_to_our_format(coingecko_coins)

        # Should skip coin with negative price
        assert result == []

    def test_map_coingecko_special_characters_in_name(self):
        """Test handling of special characters in coin names"""
        coingecko_coin = {
            "symbol": "doge",
            "name": "Dogecoin 🐕",
            "current_price": 0.08
        }

        result = _map_coingecko_to_our_format([coingecko_coin])

        assert len(result) == 1
        assert result[0].symbol == "DOGE"
        assert result[0].name == "Dogecoin 🐕"
        assert result[0].current_price == Decimal('0.08')

    def test_map_coingecko_multiple_coins(self):
        """Test mapping multiple coins at once"""
        coingecko_coins = [
            {"symbol": "btc", "name": "Bitcoin", "current_price": 45000.0},
            {"symbol": "eth", "name": "Ethereum", "current_price": 3000.0},
            {"symbol": "ada", "name": "Cardano", "current_price": 0.5},
            {"symbol": "sol", "name": "Solana", "current_price": 100.0}
        ]

        result = _map_coingecko_to_our_format(coingecko_coins)

        assert len(result) == 4
        assert [coin.symbol for coin in result] == ["BTC", "ETH", "ADA", "SOL"]


class TestFetchCoins:
    """Test the main fetch_coins function"""

    @pytest.mark.asyncio
    async def test_fetch_coins_success(self):
        """Test successful coin fetching from CoinGecko"""
        mock_raw_coins = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap_rank": 1
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0,
                "market_cap_rank": 2
            }
        ]

        # Mock only the external dependency: _fetch_from_coingecko
        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_raw_coins) as mock_fetch:
            result = await fetch_coins()

            assert len(result) == 2
            assert result[0].symbol == "BTC"
            assert result[0].name == "Bitcoin"
            assert result[0].current_price == Decimal('45000.0')
            assert result[1].symbol == "ETH"
            assert result[1].name == "Ethereum"
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_coins_coingecko_failure(self):
        """Test fallback when CoinGecko fails"""
        with patch('services.fetch_coins._fetch_from_coingecko', side_effect=Exception("API Error")):
            result = await fetch_coins()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_coins_empty_response(self):
        """Test handling of empty response from CoinGecko"""
        with patch('services.fetch_coins._fetch_from_coingecko', return_value=[]):
            result = await fetch_coins()

            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_coins_returns_validated_coin_data_objects(self):
        """Test that fetch_coins returns CoinData objects, not raw dicts"""
        mock_raw_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_raw_coins):
            result = await fetch_coins()

            assert len(result) == 1
            assert isinstance(result[0], CoinData)
            assert result[0].symbol == "BTC"


class TestIntegrationScenarios:
    """Test integration scenarios with realistic data"""

    @pytest.mark.asyncio
    async def test_full_fetch_and_map_flow(self):
        """Test the complete flow from API call to validated CoinData objects"""
        mock_raw_coins = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap_rank": 1,
                "image": "https://example.com/btc.png",
                "high_24h": 46000.0,
                "low_24h": 44000.0
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3000.0,
                "market_cap_rank": 2,
                "image": "https://example.com/eth.png",
                "high_24h": 3100.0,
                "low_24h": 2900.0
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_raw_coins):
            result = await fetch_coins()

            assert len(result) == 2

            # Verify first coin
            btc = result[0]
            assert isinstance(btc, CoinData)
            assert btc.symbol == "BTC"
            assert btc.name == "Bitcoin"
            assert btc.current_price == Decimal('45000.0')
            assert btc.price_usd == Decimal('45000.0')
            assert btc.image == "https://example.com/btc.png"
            assert btc.high_24h == Decimal('46000.0')
            assert btc.low_24h == Decimal('44000.0')

            # Verify second coin
            eth = result[1]
            assert isinstance(eth, CoinData)
            assert eth.symbol == "ETH"
            assert eth.name == "Ethereum"
            assert eth.current_price == Decimal('3000.0')

    @pytest.mark.asyncio
    async def test_error_handling_with_network_issues(self):
        """Test error handling when network issues occur"""
        with patch('services.fetch_coins._fetch_from_coingecko', side_effect=httpx.TimeoutException("Timeout")):
            result = await fetch_coins()
            assert result == []

    @pytest.mark.asyncio
    async def test_partial_success_with_validation_errors(self):
        """Test scenario where some coins pass validation and others fail"""
        mock_raw_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0
            },
            {
                "symbol": "",  # Invalid
                "name": "Bad Coin",
                "current_price": 100.0
            },
            {
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": -3000.0  # Invalid negative price
            },
            {
                "symbol": "ada",
                "name": "Cardano",
                "current_price": 0.5
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_raw_coins):
            result = await fetch_coins()

            # Only valid coins should be returned
            assert len(result) == 2
            assert result[0].symbol == "BTC"
            assert result[1].symbol == "ADA"

    @pytest.mark.asyncio
    async def test_decimal_conversion_throughout_pipeline(self):
        """Test that Decimal conversion is properly maintained throughout"""
        mock_raw_coins = [
            {
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45123.456789,  # Float with many decimals
                "market_cap": 850000000000.12345
            }
        ]

        with patch('services.fetch_coins._fetch_from_coingecko', return_value=mock_raw_coins):
            result = await fetch_coins()

            assert len(result) == 1
            coin = result[0]

            # Verify Decimal types are preserved
            assert isinstance(coin.current_price, Decimal)
            assert isinstance(coin.market_cap, Decimal)
            assert coin.current_price == Decimal('45123.456789')
            assert coin.market_cap == Decimal('850000000000.1234')