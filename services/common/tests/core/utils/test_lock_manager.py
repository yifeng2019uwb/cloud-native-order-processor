"""
Tests for Lock Manager
"""

import uuid
# Standard library imports
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest
from botocore.exceptions import ClientError

# Local imports
from src.core.utils import lock_manager
from src.core.utils.lock_manager import (LockType, LockTimeout, UserLock, UserLockItem, acquire_lock,
                                         release_lock)
from tests.utils.dependency_constants import MODEL_SAVE, MODEL_GET, MODEL_DELETE
from src.data.exceptions import (CNOPDatabaseOperationException,
                                 CNOPLockAcquisitionException)

TEST_LOCK_VALUE = "lock-123"
TEST_USERNAME = "testuser123"
TEST_OPERATION = LockType.DEPOSIT


class TestUserLock:
    """Test UserLock context manager"""

    # Define patch paths as class constants
    PATH_ACQUIRE_LOCK = f'{lock_manager.__name__}.acquire_lock'
    PATH_RELEASE_LOCK = f'{lock_manager.__name__}.release_lock'

    @pytest.mark.asyncio
    async def test_user_lock_success(self):
        """Test successful lock acquisition and release"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:
                mock_acquire_lock.return_value = TEST_LOCK_VALUE
                mock_release_lock.return_value = True

                async with UserLock(username, operation):
                    pass

                mock_acquire_lock.assert_called_once_with(username, operation, 2)
                mock_release_lock.assert_called_once_with(username, TEST_LOCK_VALUE)

    @pytest.mark.asyncio
    async def test_user_lock_acquisition_failed(self):
        """Test lock acquisition failure"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock:
            mock_acquire_lock.side_effect = CNOPLockAcquisitionException("Lock failed")

            with pytest.raises(CNOPLockAcquisitionException):
                async with UserLock(username, operation):
                    pass

    @pytest.mark.asyncio
    async def test_user_lock_release_on_exception(self):
        """Test lock release when exception occurs in context"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:
                mock_acquire_lock.return_value = TEST_LOCK_VALUE
                mock_release_lock.return_value = True

                with pytest.raises(ValueError):
                    async with UserLock(username, operation):
                        raise ValueError("Test exception")

                mock_release_lock.assert_called_once_with(username, TEST_LOCK_VALUE)

    @pytest.mark.asyncio
    async def test_user_lock_no_release_if_not_acquired(self):
        """Test that lock is not released if acquisition failed"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        with patch(self.PATH_ACQUIRE_LOCK) as mock_acquire_lock, \
             patch(self.PATH_RELEASE_LOCK) as mock_release_lock:
                mock_acquire_lock.side_effect = CNOPLockAcquisitionException("Lock failed")

                with pytest.raises(CNOPLockAcquisitionException):
                    async with UserLock(username, operation):
                        pass

                mock_release_lock.assert_not_called()


class TestAcquireLock:
    """Test acquire_lock function"""

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_SAVE)
    def test_acquire_lock_success(self, mock_save, mock_get):
        """Test successful lock acquisition"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        # Mock that no existing lock exists
        mock_get.side_effect = UserLockItem.DoesNotExist()
        mock_save.return_value = None

        lock_id = acquire_lock(username, operation)

        assert lock_id is not None
        assert isinstance(lock_id, str)
        assert "lock_" in lock_id

        # Verify PynamoDB operations were called
        mock_get.assert_called_once()
        mock_save.assert_called_once()

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_SAVE)
    def test_acquire_lock_conditional_check_failed(self, mock_save, mock_get):
        """Test lock acquisition when lock already exists"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        # Mock that an existing lock exists and is still valid
        existing_lock = UserLockItem()
        existing_lock.lock_id = "existing_lock_123"
        existing_lock.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        mock_get.return_value = existing_lock
        mock_save.side_effect = Exception("Conditional check failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while acquiring lock"):
            acquire_lock(username, operation)

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_SAVE)
    def test_acquire_lock_database_error(self, mock_save, mock_get):
        """Test lock acquisition when database error occurs"""
        username = "test-user-123"
        operation = LockType.DEPOSIT

        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while acquiring lock"):
            acquire_lock(username, operation)


class TestReleaseLock:
    """Test release_lock function"""

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_DELETE)
    def test_release_lock_success(self, mock_delete, mock_get):
        """Test successful lock release"""
        username = "test-user-123"
        lock_id = "lock-123"

        # Mock existing lock
        existing_lock = UserLockItem()
        existing_lock.lock_id = lock_id
        mock_get.return_value = existing_lock
        mock_delete.return_value = None

        result = release_lock(username, lock_id)

        assert result is True

        # Verify PynamoDB operations were called
        mock_get.assert_called_once()
        mock_delete.assert_called_once()

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_DELETE)
    def test_release_lock_conditional_check_failed(self, mock_delete, mock_get):
        """Test lock release when lock was already released"""
        username = "test-user-123"
        lock_id = "lock-123"

        # Mock that lock doesn't exist or has different lock_id
        mock_get.side_effect = UserLockItem.DoesNotExist()

        result = release_lock(username, lock_id)

        assert result is False

    @patch.object(UserLockItem, MODEL_GET)
    @patch.object(UserLockItem, MODEL_DELETE)
    def test_release_lock_database_error(self, mock_delete, mock_get):
        """Test lock release when database error occurs"""
        username = "test-user-123"
        lock_id = "lock-123"

        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while releasing lock"):
            release_lock(username, lock_id)
