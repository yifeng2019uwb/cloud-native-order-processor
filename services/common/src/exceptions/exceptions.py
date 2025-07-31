"""
Exceptions for common package/component only
Path: services/common/src/exceptions/exceptions.py

These exceptions are for common package/component only and should be handled internally.
They should NOT be mapped to external error codes.
Services should catch these and convert them to their own InternalServerException.
"""

from .base_exception import BaseInternalException


class CommonException(BaseInternalException):
    """Base class for common package exceptions that should be handled internally"""
    pass


# ========================================
# DATABASE EXCEPTIONS (500 scenarios)
# ========================================

class DatabaseConnectionException(CommonException):
    """Database connection exception"""
    pass


class DatabaseOperationException(CommonException):
    """Database operation exception"""
    pass


# ========================================
# CONFIGURATION EXCEPTIONS (500 scenarios)
# ========================================

class ConfigurationException(CommonException):
    """Configuration exception"""
    pass


# ========================================
# EXTERNAL SERVICE EXCEPTIONS (503 scenarios)
# ========================================

class AWSServiceException(CommonException):
    """AWS service exception"""
    pass


class ExternalServiceException(CommonException):
    """External service exception"""
    pass


# ========================================
# GENERIC COMMON SERVER EXCEPTION (500 scenarios)
# ========================================

class CommonServerException(CommonException):
    """Generic common server exception for catch-all scenarios in common package"""
    pass