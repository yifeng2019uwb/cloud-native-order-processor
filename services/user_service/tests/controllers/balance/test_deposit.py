"""
Tests for deposit controller
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.balance.deposit import deposit_funds, router
from src.api_models.balance.balance_models import DepositRequest, DepositResponse
from common.data.entities.user import User
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPEntityNotFoundException,
    CNOPLockAcquisitionException
)
from common.exceptions.shared_exceptions import (
    CNOPInternalServerException,
    CNOPUserNotFoundException,
)
from user_exceptions import CNOPDailyLimitExceededException


class TestDepositFunds:
    """Test cases for deposit_funds function"""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request object"""
        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.headers = {"user-agent": "test-agent"}
        return request

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        user = Mock(spec=User)
        user.username = "testuser123"
        return user

    @pytest.fixture
    def mock_transaction_manager(self):
        """Mock transaction manager"""
        manager = AsyncMock()
        return manager

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO for daily limit check (get_user_transactions used by get_daily_total)"""
        dao = MagicMock()
        # Empty transactions -> daily_total = 0
        dao.get_user_transactions.return_value = ([], None)
        return dao

    @pytest.fixture
    def sample_deposit_request(self):
        """Sample deposit request data"""
        return DepositRequest(amount=Decimal('100.00'))

    @pytest.fixture
    def mock_transaction_result(self):
        """Mock transaction result"""
        result = Mock()
        result.transaction = Mock(transaction_id="txn_12345")
        return result

    @pytest.mark.asyncio
    async def test_deposit_success(self, mock_request, mock_current_user,
                                 mock_transaction_manager, mock_balance_dao,
                                 sample_deposit_request, mock_transaction_result):
        """Test successful deposit"""
        mock_transaction_manager.deposit_funds.return_value = mock_transaction_result

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            result = await deposit_funds(
                deposit_data=sample_deposit_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        assert result.success is True
        assert result.message == "Successfully deposited $100.00"
        assert result.transaction_id == "txn_12345"
        assert isinstance(result.timestamp, datetime)

        mock_balance_dao.get_user_transactions.assert_called()
        mock_transaction_manager.deposit_funds.assert_called_once_with(
            username="testuser123",
            amount=Decimal('100.00')
        )

    @pytest.mark.asyncio
    async def test_deposit_daily_limit_exceeded(self, mock_request, mock_current_user,
                                               mock_transaction_manager, mock_balance_dao,
                                               sample_deposit_request):
        """Test deposit when daily limit is exceeded (service layer validation)"""
        # Mock: already deposited 10000 today (transactions sum to 10000), limit is 10000, requesting 100 more
        from common.data.entities.user.balance_enums import TransactionType
        mock_tx = MagicMock()
        mock_tx.transaction_type = TransactionType.DEPOSIT
        mock_tx.amount = Decimal("10000")
        mock_tx.created_at = datetime.now(timezone.utc)
        mock_balance_dao.get_user_transactions.return_value = ([mock_tx], None)

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            with pytest.raises(CNOPDailyLimitExceededException, match="Daily deposit limit exceeded"):
                await deposit_funds(
                    deposit_data=sample_deposit_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

        # Transaction manager should NOT be called - limit checked in service layer first
        mock_transaction_manager.deposit_funds.assert_not_called()

    @pytest.mark.asyncio
    async def test_deposit_lock_acquisition_failure(self, mock_request, mock_current_user,
                                                  mock_transaction_manager, mock_balance_dao,
                                                  sample_deposit_request):
        """Test deposit when lock acquisition fails"""
        mock_transaction_manager.deposit_funds.side_effect = CNOPLockAcquisitionException("Lock failed")

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
                await deposit_funds(
                    deposit_data=sample_deposit_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

    @pytest.mark.asyncio
    async def test_deposit_user_balance_not_found(self, mock_request, mock_current_user,
                                                mock_transaction_manager, mock_balance_dao,
                                                sample_deposit_request):
        """Test deposit when user balance not found"""
        mock_transaction_manager.deposit_funds.side_effect = CNOPEntityNotFoundException("Balance not found")

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            with pytest.raises(CNOPUserNotFoundException, match="User balance not found"):
                await deposit_funds(
                    deposit_data=sample_deposit_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

    @pytest.mark.asyncio
    async def test_deposit_database_operation_failure(self, mock_request, mock_current_user,
                                                    mock_transaction_manager, mock_balance_dao,
                                                    sample_deposit_request):
        """Test deposit when database operation fails"""
        mock_transaction_manager.deposit_funds.side_effect = CNOPDatabaseOperationException("DB error")

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
                await deposit_funds(
                    deposit_data=sample_deposit_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

    @pytest.mark.asyncio
    async def test_deposit_unexpected_exception(self, mock_request, mock_current_user,
                                              mock_transaction_manager, mock_balance_dao,
                                              sample_deposit_request):
        """Test deposit when unexpected exception occurs"""
        mock_transaction_manager.deposit_funds.side_effect = Exception("Unexpected error")

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
                await deposit_funds(
                    deposit_data=sample_deposit_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    balance_dao=mock_balance_dao
                )

    @pytest.mark.asyncio
    async def test_deposit_request_client_none(self, mock_request, mock_current_user,
                                             mock_transaction_manager, mock_balance_dao,
                                             sample_deposit_request, mock_transaction_result):
        """Test deposit when request.client is None"""
        mock_request.client = None
        mock_transaction_manager.deposit_funds.return_value = mock_transaction_result

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            result = await deposit_funds(
                deposit_data=sample_deposit_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        assert result.success is True
        # Should handle None client gracefully

    @pytest.mark.asyncio
    async def test_deposit_missing_user_agent(self, mock_request, mock_current_user,
                                            mock_transaction_manager, mock_balance_dao,
                                            sample_deposit_request, mock_transaction_result):
        """Test deposit when user-agent header is missing"""
        mock_request.headers = {}
        mock_transaction_manager.deposit_funds.return_value = mock_transaction_result

        with patch("services.balance_limit.os.getenv", return_value="10000"):
            result = await deposit_funds(
                deposit_data=sample_deposit_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                balance_dao=mock_balance_dao
            )

        assert result.success is True
        # Should handle missing user-agent gracefully


class TestDepositRouter:
    """Test cases for deposit router configuration"""

    def test_router_tags(self):
        """Test router tags configuration"""
        assert router.tags == ["balance"]

    def test_router_endpoint_path(self):
        """Test router endpoint path"""
        assert router.routes[0].path == "/balance/deposit"

    def test_router_response_models(self):
        """Test router response models"""
        route = router.routes[0]
        assert route.response_model is not None
        assert route.status_code == status.HTTP_201_CREATED

    def test_router_responses_documentation(self):
        """Test router responses documentation - responses section removed"""
        route = router.routes[0]
        # We removed the responses section, so just verify the route exists
        assert route is not None
        assert route.path == '/balance/deposit'
