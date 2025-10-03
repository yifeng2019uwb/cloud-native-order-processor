"""
Data Exceptions Package

This package contains all data-related exceptions for the CNOP system.
Data exceptions are for internal system/infrastructure issues only.
Business logic exceptions are handled in service layer or shared layer.
"""

from .database import (CNOPDatabaseConnectionException,
                       CNOPDatabaseOperationException)
from .system import (CNOPAWSServiceException, CNOPCommonServerException,
                     CNOPConfigurationException, CNOPExternalServiceException,
                     CNOPLockAcquisitionException, CNOPLockTimeoutException)
from .validation import CNOPEntityValidationException

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
