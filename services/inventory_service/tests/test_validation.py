"""
Tests for inventory service validation
"""
import pytest
from src.validation.field_validators import validate_asset_id
from common.exceptions.shared_exceptions import AssetValidationException


class TestAssetIDValidation:
    """Test asset ID validation for GET /assets/{asset_id} endpoint"""

    def test_valid_asset_ids(self):
        """Test valid asset ID formats"""
        valid_ids = [
            "BTC",
            "ETH",
            "USDT",
            "ADA",
            "DOT",
            "LINK",
            "BCH",
            "LTC",
            "XRP",
            "BNB"
        ]

        for asset_id in valid_ids:
            result = validate_asset_id(asset_id)
            assert result == asset_id.upper()

    def test_empty_asset_id(self):
        """Test empty asset ID"""
        with pytest.raises(AssetValidationException, match="Asset ID cannot be empty"):
            validate_asset_id("")

    def test_whitespace_only_asset_id(self):
        """Test whitespace-only asset ID"""
        with pytest.raises(AssetValidationException, match="Asset ID cannot be empty"):
            validate_asset_id("   ")

    def test_invalid_characters(self):
        """Test asset IDs with invalid characters"""
        # These should fail because sanitize_string only removes HTML tags and trims whitespace
        # It doesn't remove special characters like hyphens, underscores, etc.
        invalid_ids = [
            "BTC-",      # Contains hyphen - should fail
            "ETH_",      # Contains underscore - should fail
            "USDT@",     # Contains special char - should fail
            "ADA#",      # Contains special char - should fail
            "LINK!",     # Contains special char - should fail
        ]

        for asset_id in invalid_ids:
            with pytest.raises(AssetValidationException, match="Asset ID must be 1-10 alphanumeric characters"):
                validate_asset_id(asset_id)

        # This should pass because sanitize_string trims whitespace
        result = validate_asset_id("DOT ")  # Space gets trimmed
        assert result == "DOT"

    def test_too_long_asset_id(self):
        """Test asset ID that's too long"""
        with pytest.raises(AssetValidationException, match="Asset ID must be 1-10 alphanumeric characters"):
            validate_asset_id("VERYLONGASSETID")

    def test_suspicious_content(self):
        """Test asset IDs with suspicious content"""
        suspicious_ids = [
            "<script>alert('xss')</script>BTC",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]

        for asset_id in suspicious_ids:
            with pytest.raises(AssetValidationException, match="Asset ID contains potentially malicious content"):
                validate_asset_id(asset_id)

    def test_case_conversion(self):
        """Test that asset IDs are converted to uppercase"""
        assert validate_asset_id("btc") == "BTC"
        assert validate_asset_id("Eth") == "ETH"
        assert validate_asset_id("usdt") == "USDT"