"""
Internal exceptions for detailed logging and debugging (Order-focused)
Path: services/order_service/src/exceptions/internal_exceptions.py
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


class InternalOrderError(Exception):
    """
    Base internal order error - detailed for logging, never exposed to client

    Contains sensitive debugging information that should only be logged internally
    """
    def __init__(self, message: str, error_code: str, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class InternalOrderNotFoundError(InternalOrderError):
    """
    Internal: Order not found error with detailed context

    Contains sensitive information like order ID, user ID, search criteria, etc.
    Client will receive generic "order not found" message
    """
    def __init__(self, order_id: str, user_id: str = None, search_criteria: Dict[str, Any] = None):
        super().__init__(
            message=f"Order not found: {order_id}",
            error_code="ORDER_NOT_FOUND_DETAILED",
            context={
                "order_id": order_id,
                "user_id": user_id,
                "search_criteria": search_criteria,
                "search_timestamp": datetime.utcnow().isoformat(),
                "security_note": "Order access attempt"
            }
        )
        self.order_id = order_id
        self.user_id = user_id
        self.search_criteria = search_criteria


class InternalOrderExistsError(InternalOrderError):
    """
    Internal: Order already exists error with detailed context

    Contains sensitive information like existing order details, duplicate detection, etc.
    Client will receive generic "order creation failed" message
    """
    def __init__(self, order_id: str, order_type: str, asset_id: str, user_id: str = None):
        super().__init__(
            message=f"Order creation failed: Order already exists with ID {order_id}",
            error_code="ORDER_EXISTS_DETAILED",
            context={
                "order_id": order_id,
                "order_type": order_type,
                "asset_id": asset_id,
                "user_id": user_id,
                "creation_attempt_at": datetime.utcnow().isoformat(),
                "security_note": "Duplicate order creation attempt"
            }
        )
        self.order_id = order_id
        self.order_type = order_type
        self.asset_id = asset_id
        self.user_id = user_id


class InternalOrderValidationError(InternalOrderError):
    """
    Internal: Order validation error with detailed context

    Contains sensitive information about validation rules and attempted values
    Client will receive generic "invalid input" message
    """
    def __init__(self, field: str, value: Any, rule: str, details: str, order_type: str = None):
        # Truncate value for security (don't log full sensitive data)
        safe_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

        super().__init__(
            message=f"Order validation failed for field '{field}': {details}",
            error_code="ORDER_VALIDATION_ERROR_DETAILED",
            context={
                "field": field,
                "attempted_value_preview": safe_value,
                "validation_rule": rule,
                "validation_details": details,
                "order_type": order_type,
                "validation_source": "order_business_rules"
            }
        )
        self.field = field
        self.value = value
        self.rule = rule
        self.order_type = order_type


class InternalOrderStatusError(InternalOrderError):
    """
    Internal: Order status transition error with detailed context

    Contains sensitive information about status transitions, business rules, etc.
    Client will receive generic "order update failed" message
    """
    def __init__(self, order_id: str, current_status: str, attempted_status: str, reason: str):
        super().__init__(
            message=f"Order status transition failed: {current_status} -> {attempted_status}",
            error_code="ORDER_STATUS_ERROR_DETAILED",
            context={
                "order_id": order_id,
                "current_status": current_status,
                "attempted_status": attempted_status,
                "transition_reason": reason,
                "transition_attempt_at": datetime.utcnow().isoformat(),
                "business_rule": "status_transition_validation"
            }
        )
        self.order_id = order_id
        self.current_status = current_status
        self.attempted_status = attempted_status
        self.reason = reason


class InternalDatabaseError(InternalOrderError):
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


# ========================================
# HELPER FUNCTIONS
# ========================================

def raise_order_not_found(order_id: str, user_id: str = None, search_criteria: Dict[str, Any] = None):
    """
    Raise internal order not found error

    Args:
        order_id: Order ID that was not found
        user_id: User ID who was searching (if known)
        search_criteria: Search criteria used (if known)

    Raises:
        InternalOrderNotFoundError: Detailed internal exception
    """
    raise InternalOrderNotFoundError(order_id, user_id, search_criteria)


def raise_order_exists(order_id: str, order_type: str, asset_id: str, user_id: str = None):
    """
    Raise internal order exists error

    Args:
        order_id: Order ID that already exists
        order_type: Type of order being created
        asset_id: Asset ID for the order
        user_id: User ID creating the order (if known)

    Raises:
        InternalOrderExistsError: Detailed internal exception
    """
    raise InternalOrderExistsError(order_id, order_type, asset_id, user_id)


def raise_order_validation_error(field: str, value: Any, rule: str, details: str, order_type: str = None):
    """
    Raise internal order validation error

    Args:
        field: Field that failed validation
        value: Value that was being validated
        rule: Validation rule that was violated
        details: Detailed explanation of the failure
        order_type: Type of order being validated (if known)

    Raises:
        InternalOrderValidationError: Detailed internal exception
    """
    raise InternalOrderValidationError(field, value, rule, details, order_type)


def raise_order_status_error(order_id: str, current_status: str, attempted_status: str, reason: str):
    """
    Raise internal order status error

    Args:
        order_id: Order ID being updated
        current_status: Current order status
        attempted_status: Status being attempted
        reason: Reason for the status change

    Raises:
        InternalOrderStatusError: Detailed internal exception
    """
    raise InternalOrderStatusError(order_id, current_status, attempted_status, reason)


def raise_database_error(operation: str, table_name: str, original_error: Exception):
    """
    Raise internal database error

    Args:
        operation: Database operation that failed (e.g., "create_order", "get_order")
        table_name: Name of table involved
        original_error: Original exception from database layer

    Raises:
        InternalDatabaseError: Detailed internal exception
    """
    raise InternalDatabaseError(operation, table_name, original_error)
