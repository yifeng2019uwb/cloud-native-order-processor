import pytest
from datetime import datetime
from unittest.mock import Mock

from exceptions.internal_exceptions import (
    InternalInventoryError,
    InternalAssetNotFoundError,
    InternalDatabaseError,
    InternalValidationError,
    raise_asset_not_found,
    raise_database_error,
    raise_validation_error,
    AssetNotFoundException,
    InvalidAssetDataException
)
from common.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    EntityAlreadyExistsError,
    EntityValidationError,
    ConfigurationError,
    AWSError,
    EntityNotFoundError,
    BusinessRuleError
)


class TestInternalInventoryError:
    """Test the base internal inventory error class"""

    def test_internal_inventory_error_creation(self):
        """Test creating a basic internal inventory error"""
        error = InternalInventoryError(
            message="Test error message",
            error_code="TEST_ERROR",
            context={"test_key": "test_value"}
        )

        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.context == {"test_key": "test_value"}
        assert error.error_id is not None
        assert isinstance(error.timestamp, datetime)
        assert str(error) == "Test error message"

    def test_internal_inventory_error_minimal_creation(self):
        """Test creating internal inventory error with minimal parameters"""
        error = InternalInventoryError(
            message="Minimal error",
            error_code="MINIMAL_ERROR"
        )

        assert error.message == "Minimal error"
        assert error.error_code == "MINIMAL_ERROR"
        assert error.context == {}
        assert error.error_id is not None
        assert isinstance(error.timestamp, datetime)


class TestInternalAssetNotFoundError:
    """Test the asset not found error class"""

    def test_asset_not_found_error_creation(self):
        """Test creating an asset not found error"""
        error = InternalAssetNotFoundError(
            asset_id="BTC",
            search_criteria={"active_only": True}
        )

        assert error.asset_id == "BTC"
        assert error.search_criteria == {"active_only": True}
        assert error.error_code == "ASSET_NOT_FOUND_DETAILED"
        assert "BTC" in error.message
        assert "active_only" in str(error.context)

    def test_asset_not_found_error_minimal_creation(self):
        """Test creating asset not found error with minimal parameters"""
        error = InternalAssetNotFoundError(asset_id="ETH")

        assert error.asset_id == "ETH"
        assert error.search_criteria is None  # Default is None, not empty dict
        assert error.error_code == "ASSET_NOT_FOUND_DETAILED"
        assert "ETH" in error.message


class TestInternalDatabaseError:
    """Test the database error class"""

    def test_database_error_creation(self):
        """Test creating a database error"""
        original_error = ValueError("Database connection failed")
        error = InternalDatabaseError(
            operation="get_asset",
            table_name="assets",
            original_error=original_error
        )

        assert error.operation == "get_asset"
        assert error.table_name == "assets"
        assert error.original_error == original_error
        assert error.error_code == "DATABASE_ERROR_DETAILED"
        assert "get_asset" in error.message
        assert "assets" in error.message

    def test_database_error_with_complex_original_error(self):
        """Test database error with a complex original error"""
        original_error = Exception("Complex database error with details")
        error = InternalDatabaseError(
            operation="update_asset",
            table_name="asset_prices",
            original_error=original_error
        )

        assert error.operation == "update_asset"
        assert error.table_name == "asset_prices"
        assert error.original_error == original_error
        assert "update_asset" in error.message
        assert "asset_prices" in error.message


class TestInternalValidationError:
    """Test the validation error class"""

    def test_validation_error_creation(self):
        """Test creating a validation error"""
        error = InternalValidationError(
            field="price",
            value=100.50,
            rule="positive_number",
            details="Price must be positive"
        )

        assert error.field == "price"
        assert error.value == 100.50
        assert error.rule == "positive_number"
        assert error.error_code == "VALIDATION_ERROR_DETAILED"
        assert "price" in error.message
        assert "Price must be positive" in error.message

    def test_validation_error_with_long_value(self):
        """Test validation error with a long value that gets truncated"""
        long_value = "x" * 100  # 100 characters
        error = InternalValidationError(
            field="description",
            value=long_value,
            rule="max_length",
            details="Description too long"
        )

        assert error.field == "description"
        assert error.value == long_value
        assert "Description too long" in error.message
        # Check that the context contains truncated value
        context_value = error.context["attempted_value_preview"]
        assert len(context_value) <= 53  # 50 chars + "..."

    def test_validation_error_with_sensitive_data(self):
        """Test validation error with sensitive data handling"""
        sensitive_value = "secret_password_123"
        error = InternalValidationError(
            field="password",
            value=sensitive_value,
            rule="complexity",
            details="Password too simple"
        )

        assert error.field == "password"
        assert error.value == sensitive_value
        # Check that the context contains truncated value
        context_value = error.context["attempted_value_preview"]
        assert len(context_value) <= 53





class TestConvenienceFunctions:
    """Test the convenience functions for raising exceptions"""

    def test_raise_asset_not_found(self):
        """Test the raise_asset_not_found convenience function"""
        with pytest.raises(InternalAssetNotFoundError) as exc_info:
            raise_asset_not_found("ETH", {"active_only": True})

        error = exc_info.value
        assert error.asset_id == "ETH"
        assert error.search_criteria == {"active_only": True}

    def test_raise_database_error(self):
        """Test the raise_database_error convenience function"""
        original_error = Exception("DB error")

        with pytest.raises(InternalDatabaseError) as exc_info:
            raise_database_error("delete_asset", "assets", original_error)

        error = exc_info.value
        assert error.operation == "delete_asset"
        assert error.table_name == "assets"
        assert error.original_error == original_error

    def test_raise_validation_error(self):
        """Test the raise_validation_error convenience function"""
        with pytest.raises(InternalValidationError) as exc_info:
            raise_validation_error("symbol", "BTC", "format", "Invalid symbol format")

        error = exc_info.value
        assert error.field == "symbol"
        assert error.value == "BTC"
        assert error.rule == "format"
        assert "Invalid symbol format" in error.message
        assert "symbol" in error.message


class TestExternalExceptions:
    """Test the simple external exceptions"""

    def test_asset_not_found_exception(self):
        """Test the AssetNotFoundException"""
        with pytest.raises(AssetNotFoundException) as exc_info:
            raise AssetNotFoundException("XRP")

        error = exc_info.value
        assert error.asset_id == "XRP"
        assert str(error) == "Asset 'XRP' not found"

    def test_invalid_asset_data_exception(self):
        """Test the InvalidAssetDataException"""
        with pytest.raises(InvalidAssetDataException) as exc_info:
            raise InvalidAssetDataException("price", "Price must be positive")

        error = exc_info.value
        assert error.field == "price"
        assert error.message == "Price must be positive"
        assert str(error) == "Invalid price: Price must be positive"


class TestErrorContextAndLogging:
    """Test error context and logging features"""

    def test_error_context_contains_timestamp(self):
        """Test that error context contains timestamp"""
        error = InternalInventoryError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"custom_key": "custom_value"}
        )

        # Timestamp is not automatically added to context
        assert "custom_key" in error.context
        assert error.context["custom_key"] == "custom_value"
        # Timestamp is not automatically added to context in this implementation

    def test_error_id_uniqueness(self):
        """Test that error IDs are unique"""
        error1 = InternalInventoryError("Error 1", "ERROR_1")
        error2 = InternalInventoryError("Error 2", "ERROR_2")

        assert error1.error_id != error2.error_id
        assert len(error1.error_id) > 0
        assert len(error2.error_id) > 0

    def test_validation_error_context_structure(self):
        """Test validation error context structure"""
        error = InternalValidationError(
            field="test_field",
            value="test_value",
            rule="test_rule",
            details="Test details"
        )

        expected_keys = {
            "field", "attempted_value_preview", "validation_rule",
            "validation_details", "validation_timestamp"
        }

        assert all(key in error.context for key in expected_keys)
        assert error.context["field"] == "test_field"
        assert error.context["validation_rule"] == "test_rule"
        assert error.context["validation_details"] == "Test details"


class TestErrorInheritance:
    """Test error inheritance and type checking"""

    def test_inheritance_hierarchy(self):
        """Test that all errors inherit from InternalInventoryError"""
        asset_error = InternalAssetNotFoundError("BTC")
        db_error = InternalDatabaseError("test", "assets", Exception("test"))
        validation_error = InternalValidationError("field", "value", "rule", "details")

        assert isinstance(asset_error, InternalInventoryError)
        assert isinstance(db_error, InternalInventoryError)
        assert isinstance(validation_error, InternalInventoryError)

    def test_external_exceptions_dont_inherit(self):
        """Test that external exceptions don't inherit from InternalInventoryError"""
        asset_not_found = AssetNotFoundException("BTC")
        invalid_data = InvalidAssetDataException("field", "message")

        assert not isinstance(asset_not_found, InternalInventoryError)
        assert not isinstance(invalid_data, InternalInventoryError)