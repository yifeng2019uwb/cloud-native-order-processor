"""
Tests for Lock Manager
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
import uuid

from common.utils.lock_manager import (
    UserLock, acquire_lock, release_lock, get_lock_info,
    cleanup_expired_locks, LOCK_TIMEOUTS
)
from common.exceptions import DatabaseOperationException, LockAcquisitionException, LockTimeoutException


class TestUserLock:
    """Test UserLock context manager"""

    @pytest.mark.asyncio
    async def test_user_lock_success(self):
        """Test successful lock acquisition and release"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('common.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.return_value = "lock-123"
                mock_release.return_value = True

                async with UserLock(user_id, operation, timeout):
                    pass

                mock_acquire.assert_called_once_with(user_id, operation, timeout)
                mock_release.assert_called_once_with(user_id, "lock-123")

    @pytest.mark.asyncio
    async def test_user_lock_acquisition_failed(self):
        """Test lock acquisition failure"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.acquire_lock') as mock_acquire:
            mock_acquire.side_effect = LockAcquisitionException("Lock failed")

            with pytest.raises(LockAcquisitionException):
                async with UserLock(user_id, operation, timeout):
                    pass

    @pytest.mark.asyncio
    async def test_user_lock_release_on_exception(self):
        """Test lock release when exception occurs in context"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('common.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.return_value = "lock-123"
                mock_release.return_value = True

                with pytest.raises(ValueError):
                    async with UserLock(user_id, operation, timeout):
                        raise ValueError("Test exception")

                mock_release.assert_called_once_with(user_id, "lock-123")

    @pytest.mark.asyncio
    async def test_user_lock_no_release_if_not_acquired(self):
        """Test that lock is not released if acquisition failed"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.acquire_lock') as mock_acquire:
            with patch('common.utils.lock_manager.release_lock') as mock_release:
                mock_acquire.side_effect = LockAcquisitionException("Lock failed")

                with pytest.raises(LockAcquisitionException):
                    async with UserLock(user_id, operation, timeout):
                        pass

                mock_release.assert_not_called()


class TestAcquireLock:
    """Test acquire_lock function"""

    @pytest.mark.asyncio
    async def test_acquire_lock_success(self):
        """Test successful lock acquisition"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            lock_id = await acquire_lock(user_id, operation, timeout)

            assert lock_id is not None
            assert isinstance(lock_id, str)
            assert "lock_" in lock_id

            # Verify DynamoDB put_item was called
            mock_table.put_item.assert_called_once()
            call_args = mock_table.put_item.call_args

            # Check the item structure
            item = call_args[1]['Item']
            assert item['PK'] == f"USER#{user_id}"
            assert item['SK'] == "LOCK"
            assert item['operation'] == operation
            assert 'lock_id' in item
            assert 'expires_at' in item

    @pytest.mark.asyncio
    async def test_acquire_lock_conditional_check_failed(self):
        """Test lock acquisition when lock already exists"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate conditional check failure
            from botocore.exceptions import ClientError
            error_response = {
                'Error': {
                    'Code': 'ConditionalCheckFailedException',
                    'Message': 'Conditional check failed'
                }
            }
            mock_table.put_item.side_effect = ClientError(error_response, 'PutItem')

            with pytest.raises(LockAcquisitionException, match="Lock acquisition failed"):
                await acquire_lock(user_id, operation, timeout)

    @pytest.mark.asyncio
    async def test_acquire_lock_database_error(self):
        """Test lock acquisition when database error occurs"""
        user_id = "test-user-123"
        operation = "deposit"
        timeout = 10

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate database error
            mock_table.put_item.side_effect = Exception("Database connection failed")

            with pytest.raises(DatabaseOperationException, match="Failed to acquire lock"):
                await acquire_lock(user_id, operation, timeout)


class TestReleaseLock:
    """Test release_lock function"""

    @pytest.mark.asyncio
    async def test_release_lock_success(self):
        """Test successful lock release"""
        user_id = "test-user-123"
        lock_id = "lock-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            result = await release_lock(user_id, lock_id)

            assert result is True

            # Verify DynamoDB delete_item was called
            mock_table.delete_item.assert_called_once()
            call_args = mock_table.delete_item.call_args

            # Check the key structure
            key = call_args[1]['Key']
            assert key['PK'] == f"USER#{user_id}"
            assert key['SK'] == "LOCK"

    @pytest.mark.asyncio
    async def test_release_lock_conditional_check_failed(self):
        """Test lock release when lock was already released"""
        user_id = "test-user-123"
        lock_id = "lock-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate conditional check failure
            from botocore.exceptions import ClientError
            error_response = {
                'Error': {
                    'Code': 'ConditionalCheckFailedException',
                    'Message': 'Conditional check failed'
                }
            }
            mock_table.delete_item.side_effect = ClientError(error_response, 'DeleteItem')

            result = await release_lock(user_id, lock_id)

            assert result is False

    @pytest.mark.asyncio
    async def test_release_lock_database_error(self):
        """Test lock release when database error occurs"""
        user_id = "test-user-123"
        lock_id = "lock-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate database error
            mock_table.delete_item.side_effect = Exception("Database connection failed")

            with pytest.raises(DatabaseOperationException, match="Failed to release lock"):
                await release_lock(user_id, lock_id)


class TestGetLockInfo:
    """Test get_lock_info function"""

    @pytest.mark.asyncio
    async def test_get_lock_info_exists_and_valid(self):
        """Test getting lock info when lock exists and is valid"""
        user_id = "test-user-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Mock valid lock item
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            mock_item = {
                'lock_id': 'lock-123',
                'operation': 'deposit',
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            mock_table.get_item.return_value = {'Item': mock_item}

            result = await get_lock_info(user_id)

            assert result is not None
            assert result['lock_id'] == 'lock-123'
            assert result['operation'] == 'deposit'
            assert result['expires_at'] == expires_at.isoformat()

    @pytest.mark.asyncio
    async def test_get_lock_info_not_exists(self):
        """Test getting lock info when lock doesn't exist"""
        user_id = "test-user-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            mock_table.get_item.return_value = {}

            result = await get_lock_info(user_id)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_lock_info_expired(self):
        """Test getting lock info when lock is expired"""
        user_id = "test-user-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Mock expired lock item
            expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
            mock_item = {
                'lock_id': 'lock-123',
                'operation': 'deposit',
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            mock_table.get_item.return_value = {'Item': mock_item}

            result = await get_lock_info(user_id)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_lock_info_database_error(self):
        """Test getting lock info when database error occurs"""
        user_id = "test-user-123"

        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate database error
            mock_table.get_item.side_effect = Exception("Database connection failed")

            with pytest.raises(DatabaseOperationException, match="Failed to get lock info"):
                await get_lock_info(user_id)


class TestCleanupExpiredLocks:
    """Test cleanup_expired_locks function"""

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_success(self):
        """Test successful cleanup of expired locks"""
        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Mock expired locks
            mock_items = [
                {
                    'PK': 'USER#user1',
                    'SK': 'LOCK',
                    'lock_id': 'lock-1'
                },
                {
                    'PK': 'USER#user2',
                    'SK': 'LOCK',
                    'lock_id': 'lock-2'
                }
            ]
            mock_table.scan.return_value = {'Items': mock_items}

            result = await cleanup_expired_locks()

            assert result == 2

            # Verify scan was called
            mock_table.scan.assert_called_once()
            call_args = mock_table.scan.call_args

            # Check scan parameters
            assert call_args[1]['FilterExpression'] == "SK = :sk AND expires_at < :now"
            assert ':sk' in call_args[1]['ExpressionAttributeValues']
            assert ':now' in call_args[1]['ExpressionAttributeValues']

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_no_locks(self):
        """Test cleanup when no expired locks exist"""
        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            mock_table.scan.return_value = {'Items': []}

            result = await cleanup_expired_locks()

            assert result == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_partial_failure(self):
        """Test cleanup when some locks fail to delete"""
        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Mock expired locks
            mock_items = [
                {
                    'PK': 'USER#user1',
                    'SK': 'LOCK',
                    'lock_id': 'lock-1'
                },
                {
                    'PK': 'USER#user2',
                    'SK': 'LOCK',
                    'lock_id': 'lock-2'
                }
            ]
            mock_table.scan.return_value = {'Items': mock_items}

            # First delete succeeds, second fails
            mock_table.delete_item.side_effect = [None, Exception("Delete failed")]

            result = await cleanup_expired_locks()

            # Should still return 1 for the successful deletion
            assert result == 1

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_database_error(self):
        """Test cleanup when database error occurs"""
        with patch('common.utils.lock_manager.dynamodb_manager') as mock_db_manager:
            mock_table = MagicMock()
            mock_db_manager.get_connection.return_value.table = mock_table

            # Simulate database error
            mock_table.scan.side_effect = Exception("Database connection failed")

            with pytest.raises(DatabaseOperationException, match="Failed to cleanup expired locks"):
                await cleanup_expired_locks()


class TestLockTimeouts:
    """Test LOCK_TIMEOUTS configuration"""

    def test_lock_timeouts_configuration(self):
        """Test that all required lock timeouts are defined"""
        required_operations = [
            "deposit", "withdraw", "buy_order", "sell_order", "get_balance"
        ]

        for operation in required_operations:
            assert operation in LOCK_TIMEOUTS
            assert isinstance(LOCK_TIMEOUTS[operation], int)
            assert LOCK_TIMEOUTS[operation] > 0

    def test_lock_timeouts_reasonable_values(self):
        """Test that lock timeouts have reasonable values"""
        # For a personal project, timeouts should be relatively short
        assert LOCK_TIMEOUTS["deposit"] <= 10
        assert LOCK_TIMEOUTS["withdraw"] <= 15
        assert LOCK_TIMEOUTS["buy_order"] <= 30
        assert LOCK_TIMEOUTS["sell_order"] <= 30
        assert LOCK_TIMEOUTS["get_balance"] <= 5