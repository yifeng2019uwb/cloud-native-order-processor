"""
Common package exceptions for detailed logging and debugging
Path: services/common/src/exceptions/internal_exceptions.py
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class CommonError(Exception):
    """
    Base common package error - detailed for logging, never exposed to client

    Contains sensitive debugging information that should only be logged internally
    """
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)


class DatabaseConnectionError(CommonError):
    """Database connection failures (DynamoDB, Redis)"""
    pass


class DatabaseOperationError(CommonError):
    """Database operation failures (CRUD operations)"""
    pass


class ConfigurationError(CommonError):
    """Configuration issues (missing env vars, invalid config)"""
    pass


class EntityValidationError(CommonError):
    """Entity validation failures (user, asset validation)"""
    pass


class AWSError(CommonError):
    """AWS service errors (STS, credentials, etc.)"""
    pass


class EntityAlreadyExistsError(CommonError):
    """Entity already exists (duplicate username, email, asset_id)"""
    pass


class EntityNotFoundError(CommonError):
    """Entity not found (user not found, asset not found)"""
    pass


class BusinessRuleError(CommonError):
    """Business rule violations (invalid price, invalid state)"""
    pass