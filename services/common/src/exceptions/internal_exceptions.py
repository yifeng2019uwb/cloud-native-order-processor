"""
Internal exceptions for detailed logging and debugging (Common package functions)
Path: services/common/src/exceptions/internal_exceptions.py
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class InternalCommonError(Exception):
    """
    Base internal common package error - detailed for logging, never exposed to client

    Contains sensitive debugging information that should only be logged internally
    """
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class InternalDatabaseConnectionError(InternalCommonError):
    """Database connection failures (DynamoDB, Redis)"""
    pass


class InternalDatabaseOperationError(InternalCommonError):
    """Database operation failures (CRUD operations)"""
    pass


class InternalConfigurationError(InternalCommonError):
    """Configuration issues (missing env vars, invalid config)"""
    pass


class InternalEntityValidationError(InternalCommonError):
    """Entity validation failures (user, asset validation)"""
    pass


class InternalAWSError(InternalCommonError):
    """AWS service errors (STS, credentials, etc.)"""
    pass


class InternalEntityAlreadyExistsError(InternalCommonError):
    """Entity already exists (duplicate username, email, asset_id)"""
    pass


class InternalEntityNotFoundError(InternalCommonError):
    """Entity not found (user not found, asset not found)"""
    pass


class InternalBusinessRuleError(InternalCommonError):
    """Business rule violations (invalid price, invalid state)"""
    pass