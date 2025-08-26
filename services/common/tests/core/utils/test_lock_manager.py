"""
Tests for Lock Manager
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
import uuid
from botocore.exceptions import ClientError

from src.core.utils.lock_manager import (
    UserLock, acquire_lock, release_lock, LOCK_TIMEOUTS
)
from src.data.exceptions import CNOPDatabaseOperationException, CNOPLockAcquisitionException, CNOPLockTimeoutException


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

    def test_acquire_lock_success(self):
        """Test successful lock acquisition"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            lock_id = acquire_lock(username, operation, timeout)

            assert lock_id is not None
            assert isinstance(lock_id, str)
            assert "lock_" in lock_id

            # Verify DynamoDB put_item was called
            mock_table.put_item.assert_called_once()
            call_args = mock_table.put_item.call_args

            # Check the item structure
            item = call_args[1]['Item']
            assert item['Pk'] == f"USER#{username}"
            assert item['Sk'] == "LOCK"
            assert item['operation'] == operation
            assert 'lock_id' in item
            assert 'expires_at' in item

    def test_acquire_lock_conditional_check_failed(self):
        """Test lock acquisition when lock already exists"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            # Simulate conditional check failure
            error_response = {
                'Error': {
                    'Code': 'ConditionalCheckFailedException',
                    'Message': 'Conditional check failed'
                }
            }
            mock_table.put_item.side_effect = ClientError(error_response, 'PutItem')

            with pytest.raises(CNOPLockAcquisitionException, match="Lock acquisition failed"):
                acquire_lock(username, operation, timeout)

    def test_acquire_lock_database_error(self):
        """Test lock acquisition when database error occurs"""
        username = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            # Simulate database error
            mock_table.put_item.side_effect = Exception("Database connection failed")

            with pytest.raises(CNOPDatabaseOperationException, match="Failed to acquire lock"):
                acquire_lock(username, operation, timeout)


class TestReleaseLock:
    """Test release_lock function"""

    def test_release_lock_success(self):
        """Test successful lock release"""
        username = "test-user-123"
        lock_id = "lock-123"

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            result = release_lock(username, lock_id)

            assert result is True

            # Verify DynamoDB delete_item was called
            mock_table.delete_item.assert_called_once()
            call_args = mock_table.delete_item.call_args

            # Check the key structure
            key = call_args[1]['Key']
            assert key['Pk'] == f"USER#{username}"
            assert key['Sk'] == "LOCK"

    def test_release_lock_conditional_check_failed(self):
        """Test lock release when lock was already released"""
        username = "test-user-123"
        lock_id = "lock-123"

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            # Simulate conditional check failure
            error_response = {
                'Error': {
                    'Code': 'ConditionalCheckFailedException',
                    'Message': 'Conditional check failed'
                }
            }
            mock_table.delete_item.side_effect = ClientError(error_response, 'DeleteItem')

            result = release_lock(username, lock_id)

            assert result is False

    def test_release_lock_database_error(self):
        """Test lock release when database error occurs"""
        username = "test-user-123"
        lock_id = "lock-123"

        with patch('src.core.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.users_table = mock_table

            # Simulate database error
            mock_table.delete_item.side_effect = Exception("Database connection failed")

            with pytest.raises(CNOPDatabaseOperationException, match="Failed to release lock"):
                release_lock(username, lock_id)
