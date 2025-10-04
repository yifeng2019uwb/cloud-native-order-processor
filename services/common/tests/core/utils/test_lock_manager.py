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
from src.core.utils.lock_manager import (LOCK_TIMEOUTS, UserLock, UserLockItem, acquire_lock,
                                         release_lock)
from tests.data.dao.mock_constants import MockDatabaseMethods
from src.data.exceptions import (CNOPDatabaseOperationException,
                                 CNOPLockAcquisitionException)


class TestUserLock:
    """Test UserLock context manager"""

    @pytest.mark.asyncio
    async def test_user_lock_success(self):
        """Test successful lock acquisition and release"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('src.core.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.return_value = "lock-123"
                mock_release.return_value = True

                async with UserLock(username, operation, timeout):
                    pass

                mock_acquire.assert_called_once_with(username, operation, timeout)
                mock_release.assert_called_once_with(username, "lock-123")

    @pytest.mark.asyncio
    async def test_user_lock_acquisition_failed(self):
        """Test lock acquisition failure"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.acquire_lock') as mock_acquire:
            mock_acquire.side_effect = CNOPLockAcquisitionException("Lock failed")

            with pytest.raises(CNOPLockAcquisitionException):
                async with UserLock(username, operation, timeout):
                    pass

    @pytest.mark.asyncio
    async def test_user_lock_release_on_exception(self):
        """Test lock release when exception occurs in context"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('src.core.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.return_value = "lock-123"
                mock_release.return_value = True

                with pytest.raises(ValueError):
                    async with UserLock(username, operation, timeout):
                        raise ValueError("Test exception")

                mock_release.assert_called_once_with(username, "lock-123")

    @pytest.mark.asyncio
    async def test_user_lock_no_release_if_not_acquired(self):
        """Test that lock is not released if acquisition failed"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('src.core.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.side_effect = CNOPLockAcquisitionException("Lock failed")

                with pytest.raises(CNOPLockAcquisitionException):
                    async with UserLock(username, operation, timeout):
                        pass

                mock_release.assert_not_called()


class TestAcquireLock:
    """Test acquire_lock function"""

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.SAVE)
    def test_acquire_lock_success(self, mock_save, mock_get):
        """Test successful lock acquisition"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        # Mock that no existing lock exists
        mock_get.side_effect = UserLockItem.DoesNotExist()
        mock_save.return_value = None

        lock_id = acquire_lock(username, operation, timeout)

        assert lock_id is not None
        assert isinstance(lock_id, str)
        assert "lock_" in lock_id

        # Verify PynamoDB operations were called
        mock_get.assert_called_once()
        mock_save.assert_called_once()

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.SAVE)
    def test_acquire_lock_conditional_check_failed(self, mock_save, mock_get):
        """Test lock acquisition when lock already exists"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        # Mock that an existing lock exists and is still valid
        existing_lock = UserLockItem()
        existing_lock.lock_id = "existing_lock_123"
        existing_lock.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        mock_get.return_value = existing_lock
        mock_save.side_effect = Exception("Conditional check failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while acquiring lock"):
            acquire_lock(username, operation, timeout)

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.SAVE)
    def test_acquire_lock_database_error(self, mock_save, mock_get):
        """Test lock acquisition when database error occurs"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while acquiring lock"):
            acquire_lock(username, operation, timeout)


class TestReleaseLock:
    """Test release_lock function"""

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.DELETE)
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

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.DELETE)
    def test_release_lock_conditional_check_failed(self, mock_delete, mock_get):
        """Test lock release when lock was already released"""
        username = "test-user-123"
        lock_id = "lock-123"

        # Mock that lock doesn't exist or has different lock_id
        mock_get.side_effect = UserLockItem.DoesNotExist()

        result = release_lock(username, lock_id)

        assert result is False

    @patch.object(UserLockItem, MockDatabaseMethods.GET)
    @patch.object(UserLockItem, MockDatabaseMethods.DELETE)
    def test_release_lock_database_error(self, mock_delete, mock_get):
        """Test lock release when database error occurs"""
        username = "test-user-123"
        lock_id = "lock-123"

        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException, match="Database operation failed while releasing lock"):
            release_lock(username, lock_id)
