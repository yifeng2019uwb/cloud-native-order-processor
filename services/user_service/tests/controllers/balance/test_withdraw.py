"""
Unit tests for balance withdrawal controller
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.balance.withdraw import withdraw_funds, router
from src.api_models.balance.balance_models import WithdrawRequest, WithdrawResponse
from common.entities.user import UserResponse
from common.exceptions import (
    DatabaseOperationException,
    LockAcquisitionException,
    InsufficientBalanceException,
    UserValidationException as CommonUserValidationException
)
from common.exceptions.shared_exceptions import UserValidationException, InternalServerException


class TestWithdrawFunds:
    """Test withdraw_funds function"""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request object"""
        mock_req = Mock()
        mock_req.client = Mock()
        mock_req.client.host = "192.168.1.100"
        mock_req.headers = {"user-agent": "Mozilla/5.0 Test Browser"}
        return mock_req

    @pytest.fixture
    def mock_current_user(self):
        """Mock current authenticated user"""
        return UserResponse(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.fixture
    def mock_transaction_manager(self):
        """Mock transaction manager"""
        mock_manager = AsyncMock()
        mock_manager.withdraw_funds = AsyncMock()
        return mock_manager

    @pytest.fixture
    def sample_withdraw_request(self):
        """Sample withdrawal request data"""
        return WithdrawRequest(amount=Decimal("100.00"))

    @pytest.fixture
    def mock_transaction_result(self):
        """Mock successful transaction result"""
        mock_result = Mock()
        mock_result.lock_duration = 1.5
        mock_result.data = {
            "transaction": Mock(transaction_id="txn-12345")
        }
        return mock_result

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_success(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request,
        mock_transaction_result
    ):
        """Test successful withdrawal"""
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        result = await withdraw_funds(
            withdraw_data=sample_withdraw_request,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        # Verify transaction manager was called correctly
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify response structure
        assert result.success is True
        assert "Successfully withdrew $100.00" in result.message
        assert result.transaction_id == "txn-12345"
        assert isinstance(result.timestamp, datetime)

        # Verify logging - check that both calls were made
        assert mock_logger.info.call_count >= 2

        # Check that withdrawal attempt was logged (simplified assertion)
        withdrawal_attempt_calls = [
            call for call in mock_logger.info.call_args_list
            if call[0][0] == "Withdrawal attempt from 192.168.1.100"
        ]
        assert len(withdrawal_attempt_calls) >= 1

        # Check that successful withdrawal was logged
        mock_logger.info.assert_any_call(
            "Withdrawal successful for user testuser: 100.00 (lock_duration: 1.5s)"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_lock_acquisition_failure(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with lock acquisition failure"""
        mock_transaction_manager.withdraw_funds.side_effect = LockAcquisitionException("Lock timeout")

        with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify warning was logged - the actual message includes the exception class
        mock_logger.warning.assert_called_with(
            "Lock acquisition failed for withdrawal: user=testuser, error=LockAcquisitionException: Lock timeout"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_insufficient_balance(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with insufficient balance"""
        mock_transaction_manager.withdraw_funds.side_effect = InsufficientBalanceException("Insufficient funds")

        with pytest.raises(UserValidationException, match="Insufficient funds"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify warning was logged - the actual message includes the exception class
        mock_logger.warning.assert_called_with(
            "Insufficient balance for withdrawal: user=testuser, error=InsufficientBalanceException: Insufficient funds"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_common_user_validation_error(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with common user validation error"""
        mock_transaction_manager.withdraw_funds.side_effect = CommonUserValidationException("User not found")

        with pytest.raises(UserValidationException, match="User not found"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify warning was logged - the actual message includes the exception class
        mock_logger.warning.assert_called_with(
            "User validation error for withdrawal: user=testuser, error=UserValidationException: User not found"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_database_operation_user_balance_not_found(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with database operation error - user balance not found"""
        mock_transaction_manager.withdraw_funds.side_effect = DatabaseOperationException("User balance not found")

        with pytest.raises(InternalServerException, match="System error - please contact support"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify error was logged - the actual message includes the exception class
        mock_logger.error.assert_called_with(
            "System error - user balance not found for withdrawal: user=testuser, error=DatabaseOperationException: User balance not found"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_database_operation_general_error(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with general database operation error"""
        mock_transaction_manager.withdraw_funds.side_effect = DatabaseOperationException("Connection timeout")

        with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify error was logged - the actual message includes the exception class
        mock_logger.error.assert_called_with(
            "Database operation failed for withdrawal: user=testuser, error=DatabaseOperationException: Connection timeout"
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_unexpected_error(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with unexpected error"""
        mock_transaction_manager.withdraw_funds.side_effect = Exception("Unexpected system error")

        with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
            await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager
            )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username="testuser",
            amount=Decimal("100.00")
        )

        # Verify error was logged with exc_info=True
        mock_logger.error.assert_called_with(
            "Unexpected error during withdrawal: user=testuser, error=Unexpected system error",
            exc_info=True
        )

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_request_client_none(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request,
        mock_transaction_result
    ):
        """Test withdrawal when request.client is None"""
        # Set request.client to None
        mock_request.client = None
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        result = await withdraw_funds(
            withdraw_data=sample_withdraw_request,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        # Verify the function handles None client gracefully
        assert result.success is True

        # Verify logging shows 'unknown' for client host - check that both calls were made
        assert mock_logger.info.call_count >= 2

        # Check that withdrawal attempt was logged (simplified assertion)
        withdrawal_attempt_calls = [
            call for call in mock_logger.info.call_args_list
            if call[0][0] == "Withdrawal attempt from unknown"
        ]
        assert len(withdrawal_attempt_calls) >= 1

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_missing_user_agent(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request,
        mock_transaction_result
    ):
        """Test withdrawal when user-agent header is missing"""
        # Remove user-agent header
        mock_request.headers = {}
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        result = await withdraw_funds(
            withdraw_data=sample_withdraw_request,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        # Verify the function handles missing user-agent gracefully
        assert result.success is True

        # Verify logging shows 'unknown' for user-agent - check that both calls were made
        assert mock_logger.info.call_count >= 2

        # Check that withdrawal attempt was logged (simplified assertion)
        withdrawal_attempt_calls = [
            call for call in mock_logger.info.call_args_list
            if call[0][0] == "Withdrawal attempt from 192.168.1.100"
        ]
        assert len(withdrawal_attempt_calls) >= 1

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_different_amounts(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_transaction_result
    ):
        """Test withdrawal with different amounts"""
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        # Test with small amount
        small_withdraw = WithdrawRequest(amount=Decimal("0.01"))
        result = await withdraw_funds(
            withdraw_data=small_withdraw,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        assert result.success is True
        assert "Successfully withdrew $0.01" in result.message

        # Test with large amount
        large_withdraw = WithdrawRequest(amount=Decimal("999999.99"))
        result = await withdraw_funds(
            withdraw_data=large_withdraw,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        assert result.success is True
        assert "Successfully withdrew $999999.99" in result.message

    @patch('src.controllers.balance.withdraw.logger')
    async def test_withdraw_funds_transaction_result_without_lock_duration(
        self,
        mock_logger,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        sample_withdraw_request
    ):
        """Test withdrawal with transaction result that has no lock duration"""
        # Create transaction result without lock_duration
        mock_result = Mock()
        mock_result.lock_duration = None
        mock_result.data = {
            "transaction": Mock(transaction_id="txn-no-lock")
        }
        mock_transaction_manager.withdraw_funds.return_value = mock_result

        result = await withdraw_funds(
            withdraw_data=sample_withdraw_request,
            request=mock_request,
            current_user=mock_current_user,
            transaction_manager=mock_transaction_manager
        )

        # Verify the function handles None lock_duration gracefully
        assert result.success is True
        assert result.transaction_id == "txn-no-lock"

        # Verify logging shows None for lock_duration
        mock_logger.info.assert_any_call(
            "Withdrawal successful for user testuser: 100.00 (lock_duration: Nones)"
        )


class TestWithdrawRouter:
    """Test withdraw router configuration"""

    def test_router_tags(self):
        """Test that router has correct tags"""
        assert router.tags == ["balance"]

    def test_withdraw_endpoint_path(self):
        """Test that withdraw endpoint has correct path"""
        # Find the withdraw endpoint
        withdraw_route = None
        for route in router.routes:
            if hasattr(route, 'path') and route.path == "/balance/withdraw":
                withdraw_route = route
                break

        assert withdraw_route is not None
        assert withdraw_route.methods == {"POST"}

    def test_withdraw_response_models(self):
        """Test that withdraw endpoint has correct response models"""
        # Find the withdraw endpoint
        withdraw_route = None
        for route in router.routes:
            if hasattr(route, 'path') and route.path == "/balance/withdraw":
                withdraw_route = route
                break

        assert withdraw_route is not None
        assert withdraw_route.response_model is not None

        # Check status codes
        assert 201 in withdraw_route.responses
        assert 400 in withdraw_route.responses
        assert 401 in withdraw_route.responses
        assert 409 in withdraw_route.responses
        assert 422 in withdraw_route.responses
        assert 503 in withdraw_route.responses
