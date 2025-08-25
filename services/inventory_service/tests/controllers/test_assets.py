import pytest
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock

# Add the necessary paths to sys.path before importing the controller
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))  # for common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))  # for api_models

# Import the controller functions directly
from controllers.assets import list_assets, get_asset_by_id

# Import exception classes for testing
from exceptions import (
    AssetNotFoundException,
    AssetValidationException,
    InternalServerException
)
from common.exceptions import (
    DatabaseOperationException,
    ConfigurationException
)


def test_list_assets_success():
    """Test list_assets with mocked AssetDAO"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with proper attributes
        mock_asset1 = MagicMock()
        mock_asset1.asset_id = "BTC"
        mock_asset1.name = "Bitcoin"
        mock_asset1.description = "Bitcoin cryptocurrency"
        mock_asset1.category = "Cryptocurrency"
        mock_asset1.price_usd = 45000.0
        mock_asset1.is_active = True

        mock_asset2 = MagicMock()
        mock_asset2.asset_id = "ETH"
        mock_asset2.name = "Ethereum"
        mock_asset2.description = "Ethereum cryptocurrency"
        mock_asset2.category = "Cryptocurrency"
        mock_asset2.price_usd = 3000.0
        mock_asset2.is_active = True

        # Mock inactive asset for total count
        mock_asset3 = MagicMock()
        mock_asset3.asset_id = "INACTIVE"
        mock_asset3.name = "Inactive Asset"
        mock_asset3.description = "Inactive asset"
        mock_asset3.category = "Test"
        mock_asset3.price_usd = 100.0
        mock_asset3.is_active = False

        # Setup mock to return different results based on active_only parameter
        def mock_get_all_assets(active_only=True):
            if active_only:
                return [mock_asset1, mock_asset2]
            else:
                return [mock_asset1, mock_asset2, mock_asset3]

        mock_dao.get_all_assets.side_effect = mock_get_all_assets

        # test the function
        result = list_assets(active_only=True, limit=2, asset_dao=mock_dao)

        # Verify AssetDAO was called correctly (twice: once for active, once for total)
        assert mock_dao.get_all_assets.call_count == 2
        mock_dao.get_all_assets.assert_any_call(active_only=True)
        mock_dao.get_all_assets.assert_any_call(active_only=False)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2

        # Test result with active as false
        result = list_assets(active_only=False, limit=5, asset_dao=mock_dao)
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 3


def test_list_assets_with_limit():
    """Test list_assets with limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Create more mock assets with proper attributes
        mock_assets = []
        for i in range(5):
            mock_asset = MagicMock()
            mock_asset.asset_id = f"ASSET{i}"
            mock_asset.name = f"Asset {i}"
            mock_asset.description = f"Description for Asset {i}"
            mock_asset.category = "Test Category"
            mock_asset.price_usd = 100.0 + i
            mock_asset.is_active = True
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test with limit
        result = list_assets(active_only=True, limit=3, asset_dao=mock_dao)

        # Verify limit was applied
        assert len(result.assets) == 3
        assert result.assets[0].asset_id == "ASSET0"
        assert result.assets[1].asset_id == "ASSET1"
        assert result.assets[2].asset_id == "ASSET2"


def test_list_assets_without_limit():
    """Test list_assets without limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Create mock assets
        mock_assets = []
        for i in range(3):
            mock_asset = MagicMock()
            mock_asset.asset_id = f"ASSET{i}"
            mock_asset.name = f"Asset {i}"
            mock_asset.description = f"Description for Asset {i}"
            mock_asset.category = "Test Category"
            mock_asset.price_usd = 100.0 + i
            mock_asset.is_active = True
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test without limit
        result = list_assets(active_only=True, limit=None, asset_dao=mock_dao)

        # Verify all assets were returned
        assert len(result.assets) == 3


    def test_get_asset_by_id_success():
        """Test get_asset_by_id with valid asset ID"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Create mock asset
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.amount = 100.0  # Add amount for availability check

            mock_dao.get_asset_by_id.return_value = mock_asset

            # test the function
            result = get_asset_by_id("BTC", asset_dao=mock_dao)

        # Verify AssetDAO was called with uppercase asset_id
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None
        assert hasattr(result, 'asset_id')
        assert result.asset_id == "BTC"


def test_get_asset_by_id_not_found():
    """Test get_asset_by_id with non-existent asset ID"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock DAO to return None (asset not found)
        mock_dao.get_asset_by_id.return_value = None

        # Test that the function raises the correct exception
        with pytest.raises(InternalServerException) as exc_info:
            get_asset_by_id("INVALID", asset_dao=mock_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset invalid" in str(error).lower()


    def test_get_asset_by_id_case_insensitive():
        """Test get_asset_by_id handles case insensitivity"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Create mock asset
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.amount = 100.0  # Add amount for availability check

            mock_dao.get_asset_by_id.return_value = mock_asset

            # Test with lowercase input
            result = get_asset_by_id("btc", asset_dao=mock_dao)

        # Verify AssetDAO was called with uppercase asset_id
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None
        assert result.asset_id == "BTC"


# ========================================
# COMPREHENSIVE EXCEPTION HANDLING TESTS
# ========================================

class TestAssetsControllerExceptionHandling:
    """Comprehensive tests for exception handling in assets controller"""

    def test_list_assets_database_error_handling(self):
        """Test that database errors are properly converted to internal exceptions"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = Exception("Database connection failed")

        with pytest.raises(InternalServerException) as exc_info:
            list_assets(active_only=True, limit=10, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to list assets" in str(error).lower()

    def test_get_asset_by_id_database_error_handling(self):
        """Test that database errors in get_asset_by_id are properly handled"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Database query failed")

        with pytest.raises(InternalServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset btc" in str(error).lower()

    def test_list_assets_with_common_package_exception(self):
        """Test handling of common package exceptions in list_assets"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = DatabaseOperationException(
            "Connection failed", service="dynamodb"
        )

        with pytest.raises(InternalServerException) as exc_info:
            list_assets(active_only=True, limit=10, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to list assets" in str(error).lower()

    def test_get_asset_by_id_with_common_package_exception(self):
        """Test handling of common package exceptions in get_asset_by_id"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = DatabaseOperationException(
            "Operation failed", operation="get_item"
        )

        with pytest.raises(InternalServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset btc" in str(error).lower()

    def test_assets_controller_error_context(self):
        """Test that assets controller provides proper error context"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Test database error")

        with pytest.raises(InternalServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error has proper context
        assert "failed to get asset btc" in str(error).lower()
        assert "Test database error" in str(error)

    def test_assets_controller_exception_flow(self):
        """Test the complete exception flow in assets controller"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = DatabaseOperationException(
            "Connection failed", service="dynamodb", region="us-east-1"
        )

        with pytest.raises(InternalServerException) as exc_info:
            list_assets(active_only=True, limit=5, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Verify the error is properly wrapped
        assert isinstance(error, InternalServerException)
        assert "failed to list assets" in str(error).lower()

    def test_assets_controller_with_complex_exception(self):
        """Test assets controller with complex nested exceptions"""
        # Create a complex nested exception
        class ComplexDatabaseError(Exception):
            def __init__(self, message, details):
                self.message = message
                self.details = details
                super().__init__(message)

        complex_error = ComplexDatabaseError("Complex error", {"level": "critical", "retry_count": 3})

        # Mock the asset DAO to raise the complex exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = complex_error

        with pytest.raises(InternalServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        assert "failed to get asset btc" in str(error).lower()
        assert "Complex error" in str(error)

    def test_assets_controller_with_multiple_exceptions(self):
        """Test assets controller handling multiple types of exceptions"""
        # Test with different exception types
        exceptions_to_test = [
            (Exception("Generic exception"), InternalServerException),
            (RuntimeError("Runtime error"), InternalServerException),
            (DatabaseOperationException("Connection error", service="dynamodb"), InternalServerException),
            (DatabaseOperationException("Operation error", operation="scan"), InternalServerException)
        ]

        for exc, expected_exception_type in exceptions_to_test:
            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = exc

            with pytest.raises(expected_exception_type) as exc_info:
                get_asset_by_id("BTC", asset_dao=mock_asset_dao)

            error = exc_info.value
            assert isinstance(error, expected_exception_type)
            if expected_exception_type == InternalServerException:
                assert "failed to get asset btc" in str(error).lower()

    def test_assets_controller_validation_error_handling(self):
        """Test assets controller handling validation errors"""
        # Test with validation errors that should be converted to AssetValidationException
        validation_errors = [
            AssetValidationException("Asset ID cannot be empty"),
            AssetValidationException("Asset ID contains potentially malicious content"),
            AssetValidationException("Asset ID must be 1-10 alphanumeric characters")
        ]

        for validation_error in validation_errors:
            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = validation_error

            with pytest.raises(AssetValidationException) as exc_info:
                get_asset_by_id("BTC", asset_dao=mock_asset_dao)

            error = exc_info.value
            assert isinstance(error, AssetValidationException)
            assert "Invalid asset ID" in str(error)


def test_list_assets_metrics_recording():
    """Test list_assets with metrics recording (lines 40-41)"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_retrieval') as mock_record_retrieval, \
         patch('controllers.assets.update_asset_counts') as mock_update_counts:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data
        mock_asset1 = MagicMock()
        mock_asset1.asset_id = "BTC"
        mock_asset1.name = "Bitcoin"
        mock_asset1.description = "Bitcoin cryptocurrency"
        mock_asset1.category = "Cryptocurrency"
        mock_asset1.price_usd = 45000.0
        mock_asset1.is_active = True

        mock_asset2 = MagicMock()
        mock_asset2.asset_id = "ETH"
        mock_asset2.name = "Ethereum"
        mock_asset2.description = "Ethereum cryptocurrency"
        mock_asset2.category = "Cryptocurrency"
        mock_asset2.price_usd = 3000.0
        mock_asset2.is_active = True

        # Setup mock to return different results based on active_only parameter
        def mock_get_all_assets(active_only=True):
            if active_only:
                return [mock_asset1, mock_asset2]
            else:
                return [mock_asset1, mock_asset2]

        mock_dao.get_all_assets.side_effect = mock_get_all_assets

        # Test the function
        result = list_assets(active_only=True, limit=2, asset_dao=mock_dao)

        # Verify metrics were recorded
        mock_record_retrieval.assert_called_once_with(category="all", active_only=True)
        mock_update_counts.assert_called_once_with(total=2, active=2)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2


def test_get_asset_by_id_validation_error_handling():
    """Test get_asset_by_id with AssetValidationException handling (lines 172-176)"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.validate_asset_exists') as mock_validate, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_detail_view') as mock_record_view:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with all required attributes
        mock_asset = MagicMock()
        mock_asset.asset_id = "BTC"
        mock_asset.name = "Bitcoin"
        mock_asset.description = "Bitcoin cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 45000.0
        mock_asset.is_active = True
        mock_asset.amount = 1000.0  # Add amount attribute
        mock_asset.market_cap = 850000000000
        mock_asset.volume_24h = 25000000000
        mock_asset.created_at = "2024-01-01T00:00:00Z"
        mock_asset.updated_at = "2024-01-01T00:00:00Z"

        # Setup mocks
        mock_dao.get_asset_by_id.return_value = mock_asset
        mock_validate.return_value = None  # No validation error

        # Test successful case first
        result = get_asset_by_id("BTC", asset_dao=mock_dao)

        # Verify validation was called
        mock_validate.assert_called_once_with("BTC", mock_dao)

        # Verify metrics were recorded
        mock_record_view.assert_called_once_with(asset_id="BTC")

        # Now test with AssetValidationException
        mock_validate.side_effect = AssetValidationException("Asset ID cannot be empty")

        with pytest.raises(AssetValidationException) as exc_info:
            get_asset_by_id("INVALID", asset_dao=mock_dao)

        # Verify the exception message is properly formatted
        # The actual format is: "Invalid asset ID: AssetValidationException: Asset ID cannot be empty"
        assert "Invalid asset ID:" in str(exc_info.value)
        assert "Asset ID cannot be empty" in str(exc_info.value)


def test_get_asset_by_id_metrics_recording():
    """Test get_asset_by_id with metrics recording when METRICS_AVAILABLE is True"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.validate_asset_exists') as mock_validate, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_detail_view') as mock_record_view:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with all required attributes
        mock_asset = MagicMock()
        mock_asset.asset_id = "ETH"
        mock_asset.name = "Ethereum"
        mock_asset.description = "Ethereum cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 3000.0
        mock_asset.is_active = True
        mock_asset.amount = 5000.0  # Add amount attribute
        mock_asset.market_cap = 350000000000
        mock_asset.volume_24h = 15000000000
        mock_asset.created_at = "2024-01-01T00:00:00Z"
        mock_asset.updated_at = "2024-01-01T00:00:00Z"

        # Setup mocks
        mock_dao.get_asset_by_id.return_value = mock_asset
        mock_validate.return_value = None  # No validation error

        # Test the function
        result = get_asset_by_id("ETH", asset_dao=mock_dao)

        # Verify metrics were recorded
        mock_record_view.assert_called_once_with(asset_id="ETH")

        # Verify result structure
        assert result is not None
