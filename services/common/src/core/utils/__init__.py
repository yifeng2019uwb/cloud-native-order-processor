"""
Core Utils - Business Logic Utilities

This package contains business logic utilities for transaction management
and locking that are shared across all services.
"""

from .transaction_manager import (
    TransactionManager,
    TransactionResult
)

from .lock_manager import (
    UserLock,
    acquire_lock,
    release_lock,
    LOCK_TIMEOUTS
)

def get_transaction_manager() -> TransactionManager:
    """Factory function to get TransactionManager instance"""
    return TransactionManager()

__all__ = [
    # Transaction Manager
    "TransactionManager",
    "TransactionResult",
    "get_transaction_manager",

    # Lock Manager
    "UserLock",
    "acquire_lock",
    "release_lock",
    "LOCK_TIMEOUTS"
]
