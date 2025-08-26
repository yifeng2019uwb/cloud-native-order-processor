"""
Core Package - Business Logic Utilities

This package contains business logic utilities and validation that are shared
across all services in the CNOP system.
"""

from .utils.transaction_manager import (
    TransactionManager,
    TransactionResult
)

from .utils.lock_manager import (
    UserLock,
    acquire_lock,
    release_lock,
    LOCK_TIMEOUTS
)

__all__ = [
    # Transaction Manager
    "TransactionManager",
    "TransactionResult",

    # Lock Manager
    "UserLock",
    "acquire_lock",
    "release_lock",
    "LOCK_TIMEOUTS"
]
