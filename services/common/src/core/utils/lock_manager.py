"""
Lock Manager for Transaction Atomicity
Provides user-level locking to prevent race conditions in balance and order operations.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from ...data.database.dynamodb_connection import dynamodb_manager
from ...data.exceptions import CNOPDatabaseOperationException, CNOPLockAcquisitionException, CNOPLockTimeoutException
from ...shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class UserLock:
    """
    Context manager for user-level locking.
    Provides automatic lock acquisition and release.
    """

    def __init__(self, username: str, operation: str, timeout_seconds: int = 15):
        self.username = username
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.lock_id: Optional[str] = None
        self.acquired = False

    async def __aenter__(self):
        """Acquire lock when entering context"""
        try:
            self.lock_id = acquire_lock(
                self.username,
                self.operation,
                self.timeout_seconds
            )
            self.acquired = True
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Lock acquired: user={self.username}, operation={self.operation}, lock_id={self.lock_id}"
            )
            return self
        except CNOPLockAcquisitionException as e:
            raise e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock when exiting context"""
        if self.acquired and self.lock_id:
            release_lock(self.username, self.lock_id)
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Lock released: user={self.username}, operation={self.operation}, lock_id={self.lock_id}"
            )
            self.acquired = False


def acquire_lock(username: str, operation: str, timeout_seconds: int = 15) -> Optional[str]:
    """
    Acquire a lock for a user operation.

    Args:
        username: Username to lock
        operation: Operation type (deposit, withdraw, buy_order, sell_order)
        timeout_seconds: Lock timeout in seconds

    Returns:
        Lock ID if acquired, None if failed

    Raises:
        CNOPDatabaseOperationException: If database operation fails
    """
    try:
        lock_id = f"lock_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

        # Use conditional write to acquire lock
        # Only succeeds if no lock exists or existing lock is expired
        dynamodb_manager.get_connection().users_table.put_item(
            Item={
                "Pk": f"USER#{username}",
                "Sk": "LOCK",
                "lock_id": lock_id,
                "expires_at": expires_at.isoformat(),
                "operation": operation,
                "request_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "entity_type": "user_lock"
            },
            ConditionExpression="attribute_not_exists(Pk) OR expires_at < :now",
            ExpressionAttributeValues={
                ":now": datetime.now(timezone.utc).isoformat()
            }
        )

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Lock acquired successfully: user={username}, operation={operation}, lock_id={lock_id}"
        )
        return lock_id

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            logger.info(
                action=LogActions.ERROR,
                message=f"Lock acquisition failed - lock exists: user={username}, operation={operation}"
            )
            raise CNOPLockAcquisitionException(f"Lock acquisition failed for user {username}, operation {operation}")
        else:
            logger.error(
                action=LogActions.ERROR,
                message=f"Lock acquisition error: user={username}, operation={operation}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Failed to acquire lock: {str(e)}")


def release_lock(username: str, lock_id: str) -> bool:
    """
    Release a lock for a user.

    Args:
        username: Username
        lock_id: Lock ID to release

    Returns:
        True if lock was released, False if lock was already released or changed

    Raises:
        CNOPDatabaseOperationException: If database operation fails
    """
    try:
        # Delete lock if it matches our lock_id
        dynamodb_manager.get_connection().users_table.delete_item(
            Key={
                "Pk": f"USER#{username}",
                "Sk": "LOCK"
            },
            ConditionExpression="lock_id = :lock_id",
            ExpressionAttributeValues={
                ":lock_id": lock_id
            }
        )

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Lock released successfully: user={username}, lock_id={lock_id}"
        )
        return True

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            logger.info(
                action=LogActions.ERROR,
                message=f"Lock release failed - lock was already released or changed: user={username}, lock_id={lock_id}"
            )
            return False
        else:
            logger.error(
                action=LogActions.ERROR,
                message=f"Lock release error: user={username}, lock_id={lock_id}, error={str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Failed to release lock: {str(e)}")





# Lock timeout configuration - Reduced for personal project with minimal traffic
LOCK_TIMEOUTS = {
    "deposit": 5,       # Simple operation - 5s
    "withdraw": 5,      # Includes validation - 5s
    "buy_order": 5,     # Complex operation - 5s
    "sell_order": 5,    # Complex operation - 5s
    "get_balance": 1,   # Optional lock for consistency - 1s
}