"""
Internal exceptions for detailed logging and debugging (Inventory-focused)
Path: /Users/yifengzhang/workspace/cloud-native-order-processor/services/inventory-service/src/exceptions/internal_exceptions.py
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

# Import common package exceptions
from common.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    ConfigurationError,
    EntityValidationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    BusinessRuleError,
    AWSError
)


class InternalInventoryError(Exception):
    """
    Base internal inventory error - detailed for logging, never exposed to client

    Contains sensitive debugging information that should only be logged internally
    """
    def __init__(self, message: str, error_code: str, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class InternalAssetNotFoundError(InternalInventoryError):
    """
    Internal: Asset not found error with detailed context

    Contains sensitive information like attempted asset_id, search criteria, etc.
    Client will receive generic "asset not found" message
    """
    def __init__(self, asset_id: str, search_criteria: Dict[str, Any] = None):
        super().__init__(
            message=f"Asset not found: {asset_id}",
            error_code="ASSET_NOT_FOUND_DETAILED",
            context={
                "attempted_asset_id": asset_id,
                "search_criteria": search_criteria or {},
                "search_timestamp": datetime.utcnow().isoformat(),
                "security_note": "Potential asset enumeration attempt"
            }
        )
        self.asset_id = asset_id
        self.search_criteria = search_criteria


class InternalDatabaseError(InternalInventoryError):
    """
    Internal: Database operation error with full context

    Contains sensitive information about database structure, table names, etc.
    Client will receive generic "service unavailable" message
    """
    def __init__(self, operation: str, table_name: str, original_error: Exception):
        super().__init__(
            message=f"Database operation '{operation}' failed on table '{table_name}': {str(original_error)}",
            error_code="DATABASE_ERROR_DETAILED",
            context={
                "operation": operation,
                "table_name": table_name,
                "original_error_type": type(original_error).__name__,
                "original_error_message": str(original_error),
                "database_driver": "dynamodb",
                "retry_recommended": True
            }
        )
        self.operation = operation
        self.table_name = table_name
        self.original_error = original_error


class InternalValidationError(InternalInventoryError):
    """
    Internal: Business validation error with detailed context

    Contains sensitive information about validation rules and attempted values
    Client will receive generic "invalid input" message
    """
    def __init__(self, field: str, value: Any, rule: str, details: str):
        # Truncate value for security (don't log full sensitive data)
        safe_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

        super().__init__(
            message=f"Validation failed for field '{field}': {details}",
            error_code="VALIDATION_ERROR_DETAILED",
            context={
                "field": field,
                "attempted_value_preview": safe_value,
                "validation_rule": rule,
                "validation_details": details,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        )
        self.field = field
        self.value = value
        self.rule = rule





# ========================================
# SIMPLE EXTERNAL EXCEPTIONS
# ========================================

class AssetNotFoundException(Exception):
    """Simple external exception for asset not found"""
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        super().__init__(f"Asset '{asset_id}' not found")


class InvalidAssetDataException(Exception):
    """Simple external exception for invalid asset data"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Invalid {field}: {message}")


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def raise_asset_not_found(asset_id: str, search_criteria: Dict[str, Any] = None):
    """
    Convenience function to raise internal asset not found error

    Args:
        asset_id: The asset ID that was not found
        search_criteria: Optional search criteria used
    """
    raise InternalAssetNotFoundError(asset_id=asset_id, search_criteria=search_criteria)


def raise_database_error(operation: str, table_name: str, original_error: Exception):
    """
    Convenience function to raise internal database error

    Args:
        operation: The database operation that failed
        table_name: The table name involved
        original_error: The original exception that occurred
    """
    raise InternalDatabaseError(
        operation=operation,
        table_name=table_name,
        original_error=original_error
    )


def raise_validation_error(field: str, value: Any, rule: str, details: str):
    """
    Convenience function to raise internal validation error

    Args:
        field: The field that failed validation
        value: The value that failed validation
        rule: The validation rule that was violated
        details: Additional details about the validation failure
    """
    raise InternalValidationError(
        field=field,
        value=value,
        rule=rule,
        details=details
    )