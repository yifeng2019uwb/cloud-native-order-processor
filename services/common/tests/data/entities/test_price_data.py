"""
Tests for PriceData entity
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.data.entities.price_data import PriceData

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"
TEST_PRICE_45000 = Decimal("45000.00")
TEST_PRICE_3000_50 = Decimal("3000.50")


class TestPriceData:
    """Test PriceData entity for Redis cache"""

    def test_price_data_creation(self):
        """Test creating PriceData with required fields"""
        price_data = PriceData(asset_id=TEST_ASSET_ID_BTC, price=TEST_PRICE_45000)
        assert price_data.asset_id == TEST_ASSET_ID_BTC
        assert price_data.price == TEST_PRICE_45000
        assert price_data.updated_at is not None
        assert isinstance(price_data.updated_at, datetime)

    def test_price_data_default_updated_at(self):
        """Test that updated_at is set automatically when not provided"""
        before = datetime.now(timezone.utc)
        price_data = PriceData(asset_id=TEST_ASSET_ID_ETH, price=TEST_PRICE_3000_50)
        after = datetime.now(timezone.utc)
        assert before <= price_data.updated_at <= after

    def test_price_data_redis_key(self):
        """Test redis_key property returns correct format"""
        price_data = PriceData(asset_id=TEST_ASSET_ID_BTC, price=TEST_PRICE_45000)
        assert price_data.redis_key == "price:BTC"

    def test_price_data_redis_key_different_asset(self):
        """Test redis_key for different asset_id"""
        price_data = PriceData(asset_id=TEST_ASSET_ID_ETH, price=TEST_PRICE_3000_50)
        assert price_data.redis_key == "price:ETH"

    def test_price_data_to_json(self):
        """Test to_json serializes to valid JSON string"""
        price_data = PriceData(asset_id=TEST_ASSET_ID_BTC, price=TEST_PRICE_45000)
        json_str = price_data.to_json()
        assert isinstance(json_str, str)
        assert TEST_ASSET_ID_BTC in json_str
        assert "45000" in json_str

    def test_price_data_from_json(self):
        """Test from_json deserializes JSON string to PriceData"""
        price_data = PriceData(asset_id=TEST_ASSET_ID_BTC, price=TEST_PRICE_45000)
        json_str = price_data.to_json()
        restored = PriceData.from_json(json_str)
        assert restored.asset_id == price_data.asset_id
        assert restored.price == price_data.price
        assert restored.updated_at == price_data.updated_at

    def test_price_data_json_round_trip(self):
        """Test full JSON round-trip preserves data"""
        original = PriceData(asset_id=TEST_ASSET_ID_ETH, price=TEST_PRICE_3000_50)
        json_str = original.to_json()
        restored = PriceData.from_json(json_str)
        assert restored.asset_id == original.asset_id
        assert restored.price == original.price
        assert restored.redis_key == original.redis_key

    def test_price_data_missing_asset_id(self):
        """Test PriceData raises ValidationError when asset_id is missing"""
        with pytest.raises(ValidationError) as exc_info:
            PriceData(price=TEST_PRICE_45000)
        assert "asset_id" in str(exc_info.value)

    def test_price_data_missing_price(self):
        """Test PriceData raises ValidationError when price is missing"""
        with pytest.raises(ValidationError) as exc_info:
            PriceData(asset_id=TEST_ASSET_ID_BTC)
        assert "price" in str(exc_info.value)
