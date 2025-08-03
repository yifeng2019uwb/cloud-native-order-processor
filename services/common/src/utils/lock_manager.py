"""
Lock Manager for Transaction Atomicity
Provides user-level locking to prevent race conditions in balance and order operations.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from ..database.dynamodb_connection import dynamodb_manager
from ..exceptions import DatabaseOperationException, LockAcquisitionException, LockTimeoutException

logger = logging.getLogger(__name__)


class UserLock:
    """
    Context manager for user-level locking.
    Provides automatic lock acquisition and release.
    """

    def __init__(self, user_id: str, operation: str, timeout_seconds: int = 15):
        self.user_id = user_id
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.lock_id: Optional[str] = None
        self.acquired = False

    async def __aenter__(self):
        """Acquire lock when entering context"""
        try:
            self.lock_id = acquire_lock(
                self.user_id,
                self.operation,
                self.timeout_seconds
            )
            self.acquired = True
            logger.info(f"Lock acquired: user={self.user_id}, operation={self.operation}, lock_id={self.lock_id}")
            return self
        except LockAcquisitionException as e:
            raise e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock when exiting context"""
        if self.acquired and self.lock_id:
            release_lock(self.user_id, self.lock_id)
            logger.info(f"Lock released: user={self.user_id}, operation={self.operation}, lock_id={self.lock_id}")
            self.acquired = False


def acquire_lock(user_id: str, operation: str, timeout_seconds: int = 15) -> Optional[str]:
    """
    Acquire a lock for a user operation.

    Args:
        user_id: User ID to lock
        operation: Operation type (deposit, withdraw, buy_order, sell_order)
        timeout_seconds: Lock timeout in seconds

    Returns:
        Lock ID if acquired, None if failed

    Raises:
        DatabaseOperationException: If database operation fails
    """
    try:
        lock_id = f"lock_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

        # Use conditional write to acquire lock
        # Only succeeds if no lock exists or existing lock is expired
        dynamodb_manager.get_connection().users_table.put_item(
            Item={
                "Pk": f"USER#{user_id}",
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

        logger.debug(f"Lock acquired successfully: user={user_id}, operation={operation}, lock_id={lock_id}")
        return lock_id

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            logger.debug(f"Lock acquisition failed - lock exists: user={user_id}, operation={operation}")
            raise LockAcquisitionException(f"Lock acquisition failed for user {user_id}, operation {operation}")
        else:
            logger.error(f"Lock acquisition error: user={user_id}, operation={operation}, error={str(e)}")
            raise DatabaseOperationException(f"Failed to acquire lock: {str(e)}")


def release_lock(user_id: str, lock_id: str) -> bool:
    """
    Release a lock for a user.

    Args:
        user_id: User ID
        lock_id: Lock ID to release

    Returns:
        True if lock was released, False if lock was already released or changed

    Raises:
        DatabaseOperationException: If database operation fails
    """
    try:
        # Delete lock if it matches our lock_id
        dynamodb_manager.get_connection().users_table.delete_item(
            Key={
                "Pk": f"USER#{user_id}",
                "Sk": "LOCK"
            },
            ConditionExpression="lock_id = :lock_id",
            ExpressionAttributeValues={
                ":lock_id": lock_id
            }
        )

        logger.debug(f"Lock released successfully: user={user_id}, lock_id={lock_id}")
        return True

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            logger.debug(f"Lock release failed - lock was already released or changed: user={user_id}, lock_id={lock_id}")
            return False
        else:
            logger.error(f"Lock release error: user={user_id}, lock_id={lock_id}, error={str(e)}")
            raise DatabaseOperationException(f"Failed to release lock: {str(e)}")


def get_lock_info(user_id: str) -> Optional[dict]:
    """
    Get information about a user's current lock.

    Args:
        user_id: User ID

    Returns:
        Lock information if exists, None otherwise
    """
    try:
        response = dynamodb_manager.get_connection().users_table.get_item(
            Key={
                "Pk": f"USER#{user_id}",
                "Sk": "LOCK"
            }
        )

        if "Item" in response:
            item = response["Item"]
            # Check if lock is expired
            expires_at = datetime.fromisoformat(item["expires_at"].replace('Z', '+00:00'))
            if expires_at > datetime.now(timezone.utc):
                return {
                    "lock_id": item["lock_id"],
                    "operation": item["operation"],
                    "expires_at": item["expires_at"],
                    "created_at": item["created_at"]
                }
            else:
                logger.debug(f"Lock expired: user={user_id}, lock_id={item['lock_id']}")
                return None
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting lock info: user={user_id}, error={str(e)}")
        raise DatabaseOperationException(f"Failed to get lock info: {str(e)}")


def cleanup_expired_locks() -> int:
    """
    Clean up expired locks from the database.

    Returns:
        Number of locks cleaned up
    """
    try:
        # Scan for expired locks
        response = dynamodb_manager.get_connection().users_table.scan(
            FilterExpression="Sk = :sk AND expires_at < :now",
            ExpressionAttributeValues={
                ":sk": "LOCK",
                ":now": datetime.now(timezone.utc).isoformat()
            }
        )

        cleaned_count = 0
        for item in response.get("Items", []):
            try:
                dynamodb_manager.get_connection().users_table.delete_item(
                    Key={
                        "Pk": item["Pk"],
                        "Sk": item["Sk"]
                    }
                )
                cleaned_count += 1
                logger.debug(f"Cleaned up expired lock: user={item['Pk']}, lock_id={item['lock_id']}")
            except Exception as e:
                logger.error(f"Failed to clean up lock: user={item['Pk']}, error={str(e)}")

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired locks")

        return cleaned_count

    except Exception as e:
        logger.error(f"Error during lock cleanup: {str(e)}")
        raise DatabaseOperationException(f"Failed to cleanup expired locks: {str(e)}")


# Lock timeout configuration - Reduced for personal project with minimal traffic
LOCK_TIMEOUTS = {
    "deposit": 5,       # Simple operation - reduced from 10s
    "withdraw": 8,      # Includes validation - reduced from 15s
    "buy_order": 12,    # Complex operation - reduced from 25s
    "sell_order": 12,   # Complex operation - reduced from 25s
    "get_balance": 2,   # Optional lock for consistency - reduced from 5s
}