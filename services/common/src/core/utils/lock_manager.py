"""
Lock Manager for Transaction Atomicity
Provides user-level locking to prevent race conditions in balance and order operations.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from enum import Enum


from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.exceptions import DeleteError

from ...data.entities.entity_constants import UserConstants, LockFields
from ...data.database.database_constants import AWSConfig, TableNames
from ...data.exceptions import (CNOPDatabaseOperationException,
                                        CNOPLockAcquisitionException)
from ...shared.logging import BaseLogger, LogAction, LoggerName

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class LockType(str, Enum):
    """Types of locks"""
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    BUY_ORDER = "buy_order"
    SELL_ORDER = "sell_order"
    GET_BALANCE = "get_balance"


class LockTimeout(int, Enum):
    """Lock timeout values in seconds"""
    DEPOSIT = 2
    WITHDRAW = 2
    BUY_ORDER = 5
    SELL_ORDER = 5
    GET_BALANCE = 1

class UserLockItem(Model):
    """PynamoDB model for user locks - uses same table as users but different key pattern"""

    class Meta:
        """Meta class for UserLockItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary key (different from UserItem)
    Pk = UnicodeAttribute(hash_key=True)  # LockFields.PK_PREFIX + username
    Sk = UnicodeAttribute(range_key=True, default=LockFields.SK_VALUE)

    # Lock fields
    lock_id = UnicodeAttribute()
    expires_at = UTCDateTimeAttribute()
    operation = UnicodeAttribute()
    request_id = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    entity_type = UnicodeAttribute(default=LockFields.ENTITY_TYPE)

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return super().save(condition=condition, **kwargs)


class UserLock:
    """
    Context manager for user-level locking.
    Provides automatic lock acquisition and release.
    """

    def __init__(self, username: str, operation: LockType):
        self.username = username
        self.operation = operation
        self.timeout_seconds = LockTimeout[operation.name].value
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
                action=LogAction.DB_OPERATION,
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
                action=LogAction.DB_OPERATION,
                message=f"Lock released: user={self.username}, operation={self.operation}, lock_id={self.lock_id}"
            )
            self.acquired = False


def acquire_lock(username: str, operation: LockType, timeout_seconds: int = None) -> Optional[str]:
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
        timeout = timeout_seconds if timeout_seconds is not None else LockTimeout[operation.name].value
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=timeout)
        now = datetime.now(timezone.utc)

        # Check if lock already exists
        try:
            existing_lock = UserLockItem.get(f"{LockFields.PK_PREFIX}{username}", LockFields.SK_VALUE)
            # If lock exists and is not expired, acquisition fails
            if existing_lock.expires_at > now.replace(tzinfo=None):
                logger.warning(
                    action=LogAction.DB_OPERATION,
                    message=f"Lock acquisition failed - lock already exists and not expired: user={username}, operation={operation}"
                )
                raise CNOPLockAcquisitionException(f"Could not acquire lock for user '{username}' - lock already exists and not expired")
        except UserLockItem.DoesNotExist:
            # No existing lock, proceed to create new one
            pass

        # Create UserLockItem for the lock
        lock_item = UserLockItem()
        lock_item.Pk = f"{LockFields.PK_PREFIX}{username}"
        lock_item.Sk = LockFields.SK_VALUE
        lock_item.lock_id = lock_id
        lock_item.expires_at = expires_at.replace(tzinfo=None)  # Convert to naive UTC
        lock_item.operation = operation
        lock_item.request_id = str(uuid.uuid4())
        lock_item.created_at = now.replace(tzinfo=None)
        lock_item.updated_at = now.replace(tzinfo=None)
        lock_item.entity_type = LockFields.ENTITY_TYPE

        # Save the lock item
        lock_item.save()

        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Lock acquired successfully: user={username}, operation={operation}, lock_id={lock_id}"
        )
        return lock_id

    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Failed to acquire lock: {str(e)}"
        )
        raise CNOPDatabaseOperationException(f"Database operation failed while acquiring lock: {str(e)}") from e


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

    # Get the lock item first to check if it exists and matches
        try:
            lock_item = UserLockItem.get(f"{LockFields.PK_PREFIX}{username}", LockFields.SK_VALUE)
            if lock_item.lock_id != lock_id:
                logger.warning(
                    action=LogAction.DB_OPERATION,
                    message=f"Lock release failed - lock ID mismatch: user={username}, expected={lock_id}, actual={lock_item.lock_id}"
                )
                return False
        except UserLockItem.DoesNotExist:
            logger.warning(
                action=LogAction.NOT_FOUND,
                message=f"Lock release failed - lock not found: user={username}, lock_id={lock_id}"
            )
            return False

        # Delete the lock with condition
        lock_item.delete(condition=UserLockItem.lock_id == lock_id)

        logger.info(
            action=LogAction.DB_OPERATION,
            message=f"Lock released successfully: user={username}, lock_id={lock_id}"
        )
        return True

    except DeleteError:
        logger.warning(
            action=LogAction.DB_OPERATION,
            message=f"Lock release failed - condition not met: user={username}, lock_id={lock_id}"
        )
        return False

    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Failed to release lock: {str(e)}"
        )
        raise CNOPDatabaseOperationException(f"Database operation failed while releasing lock: {str(e)}") from e