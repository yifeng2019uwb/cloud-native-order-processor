"""
Data Package - Pure data access domain

This package contains all data-related functionality:
- Database connections and management
- Data Access Objects (DAOs)
- Data entities and models
- Data-specific exceptions (internal only)
"""

__version__ = "1.0.0"

# Export data exceptions (internal infrastructure only)
from .exceptions import (
    CNOPDatabaseConnectionException,
    CNOPDatabaseOperationException,
    CNOPConfigurationException,
    CNOPAWSServiceException,
    CNOPExternalServiceException,
    CNOPLockAcquisitionException,
    CNOPLockTimeoutException,
    CNOPCommonServerException,
    CNOPEntityValidationException,
)

__all__ = [
    "CNOPDatabaseConnectionException",
    "CNOPDatabaseOperationException",
    "CNOPConfigurationException",
    "CNOPAWSServiceException",
    "CNOPExternalServiceException",
    "CNOPLockAcquisitionException",
    "CNOPLockTimeoutException",
    "CNOPCommonServerException",
    "CNOPEntityValidationException",
]
