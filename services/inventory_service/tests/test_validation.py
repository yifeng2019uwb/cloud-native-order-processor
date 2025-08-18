"""
Tests for inventory service validation
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.validation.field_validators import validate_asset_id
from src.validation.business_validators import validate_asset_exists, validate_asset_is_active
from common.exceptions.shared_exceptions import AssetValidationException, AssetNotFoundException
from common.exceptions.shared_exceptions import EntityNotFoundException
from common.exceptions import DatabaseOperationException, ConfigurationException, AWSServiceException
from exceptions import AssetNotFoundException as InventoryAssetNotFoundException


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

    def test_sanitize_string_non_string_input(self):
        """Test sanitize_string with non-string input (line 17)"""
        from src.validation.field_validators import sanitize_string

        # Test with non-string inputs
        assert sanitize_string(123) == "123"
        assert sanitize_string(45.67) == "45.67"
        assert sanitize_string(True) == "True"
        assert sanitize_string(None) == "None"
        assert sanitize_string(["list"]) == "['list']"

    def test_sanitize_string_with_max_length(self):
        """Test sanitize_string with max_length parameter"""
        from src.validation.field_validators import sanitize_string

        # Test with max_length
        result = sanitize_string("This is a very long string that should be truncated", max_length=20)
        assert len(result) <= 20
        assert "This is a very long" in result

    def test_sanitize_string_remove_html_tags(self):
        """Test sanitize_string HTML tag removal"""
        from src.validation.field_validators import sanitize_string

        # Test HTML tag removal
        result = sanitize_string("<script>alert('xss')</script>Hello World")
        assert "Hello World" in result
        assert "<script>" not in result

    def test_is_suspicious_non_string_input(self):
        """Test is_suspicious with non-string input (line 27)"""
        from src.validation.field_validators import is_suspicious

        # Test with non-string inputs
        assert is_suspicious(123) is False
        assert is_suspicious(45.67) is False
        assert is_suspicious(True) is False
        assert is_suspicious(None) is False
        assert is_suspicious(["list"]) is False

    def test_is_suspicious_suspicious_patterns(self):
        """Test is_suspicious with suspicious content patterns (line 35)"""
        from src.validation.field_validators import is_suspicious

        # Test suspicious patterns
        suspicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "<iframe src='malicious.com'></iframe>",
            "<object data='malicious.swf'></object>",
            "<form action='malicious.com'></form>",
            "<input type='hidden' value='malicious'>",
            "<textarea>malicious content</textarea>",
            "<select><option>malicious</option></select>",
            "<button onclick='malicious()'>Click me</button>",
            "<link rel='stylesheet' href='malicious.css'>",
            "<meta http-equiv='refresh' content='0;url=malicious.com'>",
            "<style>body{background:url('malicious.jpg')}</style>",
            "<base href='malicious.com'>",
            "<bgsound src='malicious.wav'>",
            "<xmp>malicious content</xmp>",
            "<plaintext>malicious content</plaintext>",
            "<listing>malicious content</listing>",
            "<marquee>malicious content</marquee>",
            "<applet code='malicious.class'></applet>",
            "<isindex prompt='malicious'>",
            "<dir><li>malicious</li></dir>",
            "<menu><li>malicious</li></menu>",
            "<nobr>malicious content</nobr>",
            "<noembed>malicious content</noembed>",
            "<noframes>malicious content</noframes>",
            "<noscript>malicious content</noscript>",
            "<wbr>malicious content</wbr>"
        ]

        for suspicious_input in suspicious_inputs:
            assert is_suspicious(suspicious_input) is True, f"Failed to detect suspicious content: {suspicious_input}"

    def test_is_suspicious_clean_input(self):
        """Test is_suspicious with clean input (line 35)"""
        from src.validation.field_validators import is_suspicious

        # Test clean inputs
        clean_inputs = [
            "BTC",
            "Ethereum",
            "Bitcoin is a cryptocurrency",
            "123456",
            "normal-text",
            "UPPERCASE",
            "MixedCase",
            "with_numbers_123",
            "special.chars",
            "spaces are fine",
            "tabs\tare\tfine",
            "newlines\nare\nfine"
        ]

        for clean_input in clean_inputs:
            assert is_suspicious(clean_input) is False, f"False positive for clean input: {clean_input}"


class TestBusinessValidators:
    """Test business validation functions"""

    @pytest.fixture
    def mock_asset_dao(self):
        """Mock asset DAO for testing"""
        return Mock()

    @pytest.fixture
    def mock_asset(self):
        """Mock asset object for testing"""
        asset = Mock()
        asset.is_active = True
        return asset

    def test_validate_asset_exists_success(self, mock_asset_dao, mock_asset):
        """Test successful asset existence validation"""
        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        # Should not raise any exception
        validate_asset_exists("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_exists_entity_not_found(self, mock_asset_dao):
        """Test asset existence validation when asset is not found"""
        mock_asset_dao.get_asset_by_id.side_effect = EntityNotFoundException("Asset not found")

        with pytest.raises(InventoryAssetNotFoundException):
            validate_asset_exists("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_exists_database_error(self, mock_asset_dao):
        """Test asset existence validation when database error occurs (line 32)"""
        mock_asset_dao.get_asset_by_id.side_effect = DatabaseOperationException("Connection timeout")

        # Should re-raise the database exception
        with pytest.raises(DatabaseOperationException):
            validate_asset_exists("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_exists_generic_exception(self, mock_asset_dao):
        """Test asset existence validation when generic exception occurs (line 32)"""
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Unexpected error")

        # Should re-raise the generic exception
        with pytest.raises(Exception):
            validate_asset_exists("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_success(self, mock_asset_dao, mock_asset):
        """Test successful asset active validation"""
        mock_asset.is_active = True
        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        # Should not raise any exception
        validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_inactive_asset(self, mock_asset_dao, mock_asset):
        """Test asset active validation when asset is inactive"""
        mock_asset.is_active = False
        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        with pytest.raises(InventoryAssetNotFoundException):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_entity_not_found(self, mock_asset_dao):
        """Test asset active validation when asset is not found"""
        mock_asset_dao.get_asset_by_id.side_effect = EntityNotFoundException("Asset not found")

        with pytest.raises(InventoryAssetNotFoundException):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_database_error(self, mock_asset_dao):
        """Test asset active validation when database error occurs (lines 49-60)"""
        mock_asset_dao.get_asset_by_id.side_effect = DatabaseOperationException("Connection timeout")

        # Should re-raise the database exception
        with pytest.raises(DatabaseOperationException):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_generic_exception(self, mock_asset_dao):
        """Test asset active validation when generic exception occurs (lines 49-60)"""
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Unexpected error")

        # Should re-raise the generic exception
        with pytest.raises(Exception):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_configuration_error(self, mock_asset_dao):
        """Test asset active validation when configuration error occurs (lines 49-60)"""
        mock_asset_dao.get_asset_by_id.side_effect = ConfigurationException("Invalid configuration")

        # Should re-raise the configuration exception
        with pytest.raises(ConfigurationException):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_validate_asset_is_active_aws_service_error(self, mock_asset_dao):
        """Test asset active validation when AWS service error occurs (lines 49-60)"""
        mock_asset_dao.get_asset_by_id.side_effect = AWSServiceException("AWS service unavailable")

        # Should re-raise the AWS service exception
        with pytest.raises(AWSServiceException):
            validate_asset_is_active("BTC", mock_asset_dao)

        # Verify DAO was called correctly
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")