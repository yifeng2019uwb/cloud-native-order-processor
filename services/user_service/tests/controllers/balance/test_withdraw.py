"""
Unit tests for balance withdrawal controller
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock, ANY
from common.data.entities.user.balance_enums import TransactionType
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.balance.withdraw import withdraw_funds, router
from src.api_models.balance.balance_models import WithdrawRequest, WithdrawResponse
from common.data.entities.user import User
from common.exceptions.shared_exceptions import (
    CNOPInsufficientBalanceException,
    CNOPInternalServerException,
    CNOPUserNotFoundException,
)
from user_exceptions import CNOPDailyLimitExceededException
from common.exceptions import CNOPLockAcquisitionException, CNOPDatabaseOperationException
from user_exceptions import CNOPUserValidationException


TEST_USERNAME = "testuser"
TEST_TRANSACTION_ID = "txn-12345"

class TestWithdrawFunds:
    """Test withdraw_funds function"""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request object with minimal attributes"""
        mock_req = Mock()
        mock_req.headers = {}
        return mock_req

    @pytest.fixture
    def mock_current_user(self):
        """Mock current authenticated user"""
        return User(
            username=TEST_USERNAME,
            email="test@example.com",
            password="[HASHED]",
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
        mock_result.transaction = Mock(transaction_id=TEST_TRANSACTION_ID)
        return mock_result

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO for daily limit check (get_user_transactions used by get_daily_total)"""
        dao = MagicMock()
        dao.get_user_transactions.return_value = ([], None)
        return dao

    @pytest.mark.asyncio
    async def test_withdraw_funds_success(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request,
        mock_transaction_result
    ):
        """Test successful withdrawal"""
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            result = await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        # Verify transaction manager was called correctly
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )

        # Verify response structure
        assert result.success is True
        assert "Successfully withdrew $100.00" in result.message
        assert result.transaction_id == TEST_TRANSACTION_ID
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_withdraw_funds_lock_acquisition_failure(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with lock acquisition failure"""
        mock_transaction_manager.withdraw_funds.side_effect = CNOPLockAcquisitionException("Lock timeout")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )


    @pytest.mark.asyncio
    async def test_withdraw_funds_daily_limit_exceeded(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal when daily limit is exceeded (service layer validation)"""
        # Mock: already withdrawn 5000 today (transactions sum to 5000), limit is 5000, requesting 100 more
        mock_tx = MagicMock()
        mock_tx.transaction_type = TransactionType.WITHDRAW
        mock_tx.amount = Decimal("-5000")
        mock_tx.created_at = datetime.now(timezone.utc)
        mock_balance_dao.get_user_transactions.return_value = ([mock_tx], None)

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPDailyLimitExceededException, match="Daily withdrawal limit exceeded"):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        mock_transaction_manager.withdraw_funds.assert_not_called()

    @pytest.mark.asyncio
    async def test_withdraw_funds_insufficient_balance(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with insufficient balance"""
        mock_transaction_manager.withdraw_funds.side_effect = CNOPInsufficientBalanceException("Insufficient funds")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPUserValidationException, match="Insufficient funds"):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )


    @pytest.mark.asyncio
    async def test_withdraw_funds_common_user_validation_error(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with common user validation error"""
        mock_transaction_manager.withdraw_funds.side_effect = CNOPUserValidationException("User not found")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPUserValidationException, match="User not found"):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )

    @pytest.mark.asyncio
    async def test_withdraw_funds_database_operation_user_balance_not_found(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with database operation error - user balance not found"""
        mock_transaction_manager.withdraw_funds.side_effect = CNOPDatabaseOperationException("User balance not found")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )


    @pytest.mark.asyncio
    async def test_withdraw_funds_database_operation_general_error(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with general database operation error"""
        mock_transaction_manager.withdraw_funds.side_effect = CNOPDatabaseOperationException("Connection timeout")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )


    @pytest.mark.asyncio
    async def test_withdraw_funds_unexpected_error(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with unexpected error"""
        mock_transaction_manager.withdraw_funds.side_effect = Exception("Unexpected system error")

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
                await withdraw_funds(
                    withdraw_data=sample_withdraw_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Verify transaction manager was called
        mock_transaction_manager.withdraw_funds.assert_called_once_with(
            username=TEST_USERNAME,
            amount=Decimal("100.00")
        )



    @pytest.mark.asyncio
    async def test_withdraw_funds_different_amounts(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        mock_transaction_result
    ):
        """Test withdrawal with different amounts"""
        mock_transaction_manager.withdraw_funds.return_value = mock_transaction_result

        # Use high limit so both small and large amounts pass daily limit check
        with patch("services.balance_limit.os.getenv", return_value="1000000"):
            # Test with small amount
            small_withdraw = WithdrawRequest(amount=Decimal("0.01"))
            result = await withdraw_funds(
                withdraw_data=small_withdraw,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

            assert result.success is True
            assert "Successfully withdrew $0.01" in result.message

            # Test with large amount
            large_withdraw = WithdrawRequest(amount=Decimal("999999.99"))
            result = await withdraw_funds(
                withdraw_data=large_withdraw,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        assert result.success is True
        assert "Successfully withdrew $999999.99" in result.message

    @pytest.mark.asyncio
    async def test_withdraw_funds_transaction_result_without_lock_duration(
        self,
        mock_request,
        mock_current_user,
        mock_transaction_manager,
        mock_balance_dao,
        sample_withdraw_request
    ):
        """Test withdrawal with transaction result that has no lock duration"""
        # Create transaction result without lock_duration
        transaction_id = "txn-no-lock"
        mock_result = Mock()
        mock_result.transaction = Mock(transaction_id=transaction_id)
        mock_transaction_manager.withdraw_funds.return_value = mock_result

        with patch("services.balance_limit.os.getenv", return_value="5000"):
            result = await withdraw_funds(
                withdraw_data=sample_withdraw_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        # Verify the function handles None lock_duration gracefully
        assert result.success is True
        assert result.transaction_id == transaction_id
