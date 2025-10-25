from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.data.entities.inventory import Asset

# Test constants
TEST_ASSET_ID_BTC = "BTC"
TEST_NAME_BITCOIN = "Bitcoin"
TEST_DESCRIPTION_CURRENCY = "Digital currency"
TEST_CATEGORY_MAJOR = "major"
TEST_AMOUNT_10_12345678 = Decimal("10.12345678")
TEST_PRICE_45000_50 = Decimal("45000.50")


def test_asset_creation():
    """Test basic asset creation with required fields"""
    asset = Asset(
        asset_id=TEST_ASSET_ID_BTC,
        name=TEST_NAME_BITCOIN,
        description=TEST_DESCRIPTION_CURRENCY,
        category=TEST_CATEGORY_MAJOR,
        amount=TEST_AMOUNT_10_12345678,
        price_usd=TEST_PRICE_45000_50
    )
    assert asset.asset_id == TEST_ASSET_ID_BTC
    assert asset.name == TEST_NAME_BITCOIN
    assert asset.amount == TEST_AMOUNT_10_12345678
    assert asset.price_usd == TEST_PRICE_45000_50


def test_asset_required_fields():
    """Test that required fields are enforced"""
    with pytest.raises(ValidationError):
        Asset()  # Missing all required fields


def test_asset_whitespace_trimming():
    """Test that string fields are trimmed"""
    asset = Asset(
        asset_id=f"  {TEST_ASSET_ID_BTC}  ",
        name=f"  {TEST_NAME_BITCOIN}  ",
        description=f"  {TEST_DESCRIPTION_CURRENCY}  ",
        category=f"  {TEST_CATEGORY_MAJOR}  ",
        amount=TEST_AMOUNT_10_12345678,
        price_usd=TEST_PRICE_45000_50
    )
    assert asset.asset_id == TEST_ASSET_ID_BTC
    assert asset.name == TEST_NAME_BITCOIN
    assert asset.description == TEST_DESCRIPTION_CURRENCY
    assert asset.category == TEST_CATEGORY_MAJOR