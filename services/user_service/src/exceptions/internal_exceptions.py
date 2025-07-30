"""
Internal exceptions for detailed logging and debugging (Registration-focused)
Path: /Users/yifengzhang/workspace/cloud-native-order-processor/services/user-service/src/exceptions/internal_exceptions.py
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


class InternalAuthError(Exception):
    """
    Base internal authentication error - detailed for logging, never exposed to client

    Contains sensitive debugging information that should only be logged internally
    """
    def __init__(self, message: str, error_code: str, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class InternalUserExistsError(InternalAuthError):
    """
    Internal: User already exists error with detailed context

    Contains sensitive information like existing user ID, registration timestamp, etc.
    Client will receive generic "registration failed" message
    """
    def __init__(self, email: str, existing_user_id: str = None):
        super().__init__(
            message=f"Registration failed: User already exists with email {email}",
            error_code="USER_EXISTS_DETAILED",
            context={
                "attempted_email": email,
                "existing_user_id": existing_user_id,
                "attempted_registration_at": datetime.utcnow().isoformat(),
                "security_note": "Potential email enumeration attempt"
            }
        )
        self.email = email
        self.existing_user_id = existing_user_id


class InternalDatabaseError(InternalAuthError):
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


class InternalValidationError(InternalAuthError):
    """
    Internal: Business validation error with detailed context

    Contains sensitive information about validation rules and attempted values
    Client will receive generic "invalid input" message
    """
    def __init__(self, field: str, value: Any, rule: str, details: str):
        # Truncate value for security (don't log full passwords, etc.)
        safe_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

        super().__init__(
            message=f"Validation failed for field '{field}': {details}",
            error_code="VALIDATION_ERROR_DETAILED",
            context={
                "field": field,
                "attempted_value_preview": safe_value,
                "validation_rule": rule,
                "validation_details": details,
                "validation_source": "business_rules"
            }
        )
        self.field = field
        self.value = value
        self.rule = rule


# ========================================
# COMMON PACKAGE EXCEPTION WRAPPERS - REMOVED
# ========================================
# Wrapper functions removed - direct raise of user service internal exceptions
# ========================================
# SIMPLE EXTERNAL EXCEPTIONS
# ========================================

class UserNotFoundException(Exception):
    """
    User not found exception - safe to expose to client
    """
    def __init__(self, user_id: str):
        self.message = f"User '{user_id}' not found"
        super().__init__(self.message)


class InvalidCredentialsException(Exception):
    """
    Invalid credentials exception - safe to expose to client
    """
    def __init__(self, username: str):
        self.message = f"Invalid credentials for user '{username}'"
        super().__init__(self.message)


class TokenExpiredException(Exception):
    """
    Token expired exception - safe to expose to client
    """
    def __init__(self):
        self.message = "Authentication token has expired"
        super().__init__(self.message)


# ========================================
# HELPER FUNCTIONS
# ========================================

def raise_user_exists(email: str, existing_user_id: str = None):
    """
    Raise internal user exists error

    Args:
        email: Email that already exists
        existing_user_id: ID of existing user (if known)

    Raises:
        InternalUserExistsError: Detailed internal exception
    """
    raise InternalUserExistsError(email, existing_user_id)


def raise_database_error(operation: str, table_name: str, original_error: Exception):
    """
    Raise internal database error

    Args:
        operation: Database operation that failed (e.g., "create_user", "get_user")
        table_name: Name of table involved
        original_error: Original exception from database layer

    Raises:
        InternalDatabaseError: Detailed internal exception
    """
    raise InternalDatabaseError(operation, table_name, original_error)


def raise_validation_error(field: str, value: Any, rule: str, details: str):
    """
    Raise internal validation error

    Args:
        field: Field that failed validation
        value: Value that was being validated
        rule: Validation rule that was violated
        details: Detailed explanation of the failure

    Raises:
        InternalValidationError: Detailed internal exception
    """
    raise InternalValidationError(field, value, rule, details)