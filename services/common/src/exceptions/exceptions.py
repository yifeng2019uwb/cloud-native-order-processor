"""
Data Exceptions Package

This package contains all data-related exceptions for the CNOP system.
Data exceptions are for internal system/infrastructure issues only.
Business logic exceptions are handled in service layer or shared layer.
"""

from .base_exception import CNOPInternalException


class CNOPDatabaseConnectionException(CNOPInternalException):
    """Database connection exception"""
    pass


class CNOPDatabaseOperationException(CNOPInternalException):
    """Database operation exception"""
    pass


# ========================================
# CONFIGURATION EXCEPTIONS (500 scenarios)
# ========================================

class CNOPConfigurationException(CNOPInternalException):
    """Configuration exception"""
    pass


class CNOPAWSServiceException(CNOPInternalException):
    """AWS service exception"""
    pass


class CNOPExternalServiceException(CNOPInternalException):
    """External service exception"""
    pass


class CNOPLockAcquisitionException(CNOPInternalException):
    """Raised when lock acquisition fails"""
    pass


class CNOPLockTimeoutException(CNOPInternalException):
    """Raised when lock acquisition times out"""
    pass


class CNOPEntityValidationException(CNOPInternalException):
    """Entity validation exception - internal data validation only"""
    pass


class CNOPCommonServerException(CNOPInternalException):
    """Generic common server exception for catch-all scenarios in common package"""
    pass


__all__ = [
    # Database exceptions (internal infrastructure)
    "CNOPDatabaseConnectionException",
    "CNOPDatabaseOperationException",

    # System exceptions (internal infrastructure)
    "CNOPConfigurationException",
    "CNOPAWSServiceException",
    "CNOPExternalServiceException",
    "CNOPLockAcquisitionException",
    "CNOPLockTimeoutException",
    "CNOPCommonServerException",

    # Generic validation exception (internal data validation only)
    "CNOPEntityValidationException",
]