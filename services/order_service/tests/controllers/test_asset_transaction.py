"""
Tests for asset_transaction controller
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Mock dependencies before importing
with patch('src.controllers.asset_transaction.get_current_user', create=True), \
     patch('src.controllers.asset_transaction.get_asset_transaction_dao_dependency', create=True), \
     patch('src.controllers.asset_transaction.get_asset_dao_dependency', create=True), \
     patch('src.controllers.asset_transaction.get_user_dao_dependency', create=True), \
     patch('src.controllers.asset_transaction.validate_order_history_business_rules', create=True), \
     patch('src.controllers.asset_transaction.AssetTransactionDAO', create=True), \
     patch('src.controllers.asset_transaction.AssetDAO', create=True), \
     patch('src.controllers.asset_transaction.UserDAO', create=True), \
     patch('src.controllers.asset_transaction.DatabaseOperationException', create=True), \
     patch('src.controllers.asset_transaction.EntityNotFoundException', create=True), \
     patch('src.controllers.asset_transaction.InternalServerException', create=True), \
     patch('src.controllers.asset_transaction.AssetNotFoundException', create=True), \
     patch('src.controllers.asset_transaction.UserValidationException', create=True):

    from src.controllers.asset_transaction import get_asset_transactions


class TestAssetTransactionController:
    """Test asset transaction controller functions"""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request object"""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        return request

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        return {"username": "testuser"}

    @pytest.fixture
    def mock_asset_transaction_dao(self):
        """Mock asset transaction DAO"""
        dao = Mock()

                # Mock transaction objects
        mock_transaction1 = Mock()
        mock_transaction1.asset_id = "BTC"
        mock_transaction1.transaction_type = "BUY"
        mock_transaction1.quantity = Decimal("1.5")
        mock_transaction1.price = Decimal("45000.00")
        mock_transaction1.status = "COMPLETED"
        mock_transaction1.created_at = datetime.now(timezone.utc)

        mock_transaction2 = Mock()
        mock_transaction2.asset_id = "BTC"
        mock_transaction2.transaction_type = "SELL"
        mock_transaction2.quantity = Decimal("0.5")
        mock_transaction2.price = Decimal("46000.00")
        mock_transaction2.status = "COMPLETED"
        mock_transaction2.created_at = datetime.now(timezone.utc)

        dao.get_user_asset_transactions.return_value = [mock_transaction1, mock_transaction2]

        return dao

    @pytest.fixture
    def mock_asset_dao(self):
        """Mock asset DAO"""
        dao = Mock()
        dao.get_asset_by_id.return_value = Mock()
        return dao

    @pytest.fixture
    def mock_user_dao(self):
        """Mock user DAO"""
        dao = Mock()
        dao.get_user_by_username.return_value = Mock()
        return dao

    @pytest.fixture
    def mock_validate_order_history_business_rules(self):
        """Mock business rules validation"""
        with patch('src.controllers.asset_transaction.validate_order_history_business_rules') as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_get_asset_transactions_success(self, mock_request, mock_current_user,
                                                 mock_asset_transaction_dao, mock_asset_dao,
                                                 mock_user_dao, mock_validate_order_history_business_rules):
        """Test successful retrieval of asset transactions"""
        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        # Verify validation was called
        mock_validate_order_history_business_rules.assert_called_once_with(
            asset_id="BTC",
            username="testuser",
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        # Verify DAO calls
        mock_asset_transaction_dao.get_user_asset_transactions.assert_called_once_with(
            "testuser", "BTC", limit=50
        )

        # Verify response
        assert result.success is True
        assert result.message == "Asset transactions retrieved successfully"
        assert len(result.data) == 2
        assert result.has_more is False  # 2 < 50, so has_more should be False

                # Check first transaction
        transaction1 = result.data[0]
        assert transaction1.asset_id == "BTC"
        assert transaction1.transaction_type == "BUY"
        assert transaction1.quantity == Decimal("1.5")
        assert transaction1.price == Decimal("45000.00")
        assert transaction1.status == "COMPLETED"

        # Check second transaction
        transaction2 = result.data[1]
        assert transaction2.asset_id == "BTC"
        assert transaction2.transaction_type == "SELL"
        assert transaction2.quantity == Decimal("0.5")
        assert transaction2.price == Decimal("46000.00")
        assert transaction2.status == "COMPLETED"

    @pytest.mark.asyncio
    async def test_get_asset_transactions_with_limit_reached(self, mock_request, mock_current_user,
                                                           mock_asset_transaction_dao, mock_asset_dao,
                                                           mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions when limit is reached (has_more=True)"""
        # Mock more transactions to reach the limit
        mock_transactions = []
        for i in range(50):  # Exactly 50 transactions
            mock_transaction = Mock()
            mock_transaction.asset_id = "BTC"
            mock_transaction.transaction_type = "BUY"
            mock_transaction.quantity = Decimal("1.0")
            mock_transaction.price = Decimal("45000.00")
            mock_transaction.status = "COMPLETED"
            mock_transaction.created_at = datetime.now(timezone.utc)
            mock_transactions.append(mock_transaction)

        mock_asset_transaction_dao.get_user_asset_transactions.return_value = mock_transactions

        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        assert result.has_more is True  # 50 == 50, so has_more should be True
        assert len(result.data) == 50

    @pytest.mark.asyncio
    async def test_get_asset_transactions_with_custom_limit_and_offset(self, mock_request, mock_current_user,
                                                                     mock_asset_transaction_dao, mock_asset_dao,
                                                                     mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with custom limit and offset"""
        result = await get_asset_transactions(
            asset_id="BTC",
            limit=10,
            offset=20,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        # Verify DAO calls with custom limit
        mock_asset_transaction_dao.get_user_asset_transactions.assert_called_once_with(
            "testuser", "BTC", limit=10
        )

        assert result.success is True
        assert len(result.data) == 2



    @pytest.mark.asyncio
    async def test_get_asset_transactions_entity_not_found(self, mock_request, mock_current_user,
                                                         mock_asset_transaction_dao, mock_asset_dao,
                                                         mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with entity not found exception"""
        from src.controllers.asset_transaction import EntityNotFoundException

        mock_asset_transaction_dao.get_user_asset_transactions.side_effect = EntityNotFoundException("Not found")

        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        # Should return empty list instead of error
        assert result.success is True
        assert result.message == "No asset transactions found"
        assert len(result.data) == 0
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_asset_transactions_database_error(self, mock_request, mock_current_user,
                                                       mock_asset_transaction_dao, mock_asset_dao,
                                                       mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with database operation exception"""
        from src.controllers.asset_transaction import DatabaseOperationException, InternalServerException

        mock_asset_transaction_dao.get_user_asset_transactions.side_effect = DatabaseOperationException("DB error")

        with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
            await get_asset_transactions(
                asset_id="BTC",
                limit=50,
                offset=0,
                request=mock_request,
                current_user=mock_current_user,
                asset_transaction_dao=mock_asset_transaction_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

    @pytest.mark.asyncio
    async def test_get_asset_transactions_unexpected_error(self, mock_request, mock_current_user,
                                                         mock_asset_transaction_dao, mock_asset_dao,
                                                         mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with unexpected exception"""
        from src.controllers.asset_transaction import InternalServerException

        mock_asset_transaction_dao.get_user_asset_transactions.side_effect = Exception("Unexpected error")

        with pytest.raises(InternalServerException, match="Service temporarily unavailable"):
            await get_asset_transactions(
                asset_id="BTC",
                limit=50,
                offset=0,
                request=mock_request,
                current_user=mock_current_user,
                asset_transaction_dao=mock_asset_transaction_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

    @pytest.mark.asyncio
    async def test_get_asset_transactions_empty_result(self, mock_request, mock_current_user,
                                                     mock_asset_transaction_dao, mock_asset_dao,
                                                     mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with empty result"""
        mock_asset_transaction_dao.get_user_asset_transactions.return_value = []

        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        assert result.success is True
        assert len(result.data) == 0
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_asset_transactions_with_different_asset(self, mock_request, mock_current_user,
                                                             mock_asset_transaction_dao, mock_asset_dao,
                                                             mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with different asset ID"""
        # Mock ETH transactions
        mock_eth_transaction = Mock()
        mock_eth_transaction.asset_id = "ETH"
        mock_eth_transaction.transaction_type = "BUY"
        mock_eth_transaction.quantity = Decimal("10.0")
        mock_eth_transaction.price = Decimal("3000.00")
        mock_eth_transaction.status = "COMPLETED"
        mock_eth_transaction.created_at = datetime.now(timezone.utc)

        mock_asset_transaction_dao.get_user_asset_transactions.return_value = [mock_eth_transaction]

        result = await get_asset_transactions(
            asset_id="ETH",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        assert result.success is True
        assert len(result.data) == 1

        eth_transaction = result.data[0]
        assert eth_transaction.asset_id == "ETH"
        assert eth_transaction.transaction_type == "BUY"
        assert eth_transaction.quantity == Decimal("10.0")
        assert eth_transaction.price == Decimal("3000.00")

    @pytest.mark.asyncio
    async def test_get_asset_transactions_logging(self, mock_request, mock_current_user,
                                                mock_asset_transaction_dao, mock_asset_dao,
                                                mock_user_dao, mock_validate_order_history_business_rules):
        """Test that logging is performed correctly in get_asset_transactions"""
        with patch('src.controllers.asset_transaction.logger') as mock_logger:
            await get_asset_transactions(
                asset_id="BTC",
                limit=50,
                offset=0,
                request=mock_request,
                current_user=mock_current_user,
                asset_transaction_dao=mock_asset_transaction_dao,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao
            )

            # Verify info logging was called
            mock_logger.info.assert_called()

            # Check that the success log was called
            success_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Asset transactions retrieved successfully" in call for call in success_calls)

    @pytest.mark.asyncio
    async def test_get_asset_transactions_error_logging(self, mock_request, mock_current_user,
                                                      mock_asset_transaction_dao, mock_asset_dao,
                                                      mock_user_dao, mock_validate_order_history_business_rules):
        """Test that error logging is performed correctly in get_asset_transactions"""
        from src.controllers.asset_transaction import DatabaseOperationException

        mock_asset_transaction_dao.get_user_asset_transactions.side_effect = DatabaseOperationException("DB error")

        with patch('src.controllers.asset_transaction.logger') as mock_logger:
            try:
                await get_asset_transactions(
                    asset_id="BTC",
                    limit=50,
                    offset=0,
                    request=mock_request,
                    current_user=mock_current_user,
                    asset_transaction_dao=mock_asset_transaction_dao,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao
                )
            except:
                pass

            # Verify error logging was called
            mock_logger.error.assert_called()

            # Check that the database error log was called
            error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
            assert any("Database operation failed for asset transactions" in call for call in error_calls)

    @pytest.mark.asyncio
    async def test_get_asset_transactions_with_high_precision_values(self, mock_request, mock_current_user,
                                                                   mock_asset_transaction_dao, mock_asset_dao,
                                                                   mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with high precision quantity and price"""
        # Mock transaction with high precision values
        mock_precise_transaction = Mock()
        mock_precise_transaction.asset_id = "BTC"
        mock_precise_transaction.transaction_type = "BUY"
        mock_precise_transaction.quantity = Decimal("1.12345678")
        mock_precise_transaction.price = Decimal("45000.12345")
        mock_precise_transaction.status = "COMPLETED"
        mock_precise_transaction.created_at = datetime.now(timezone.utc)

        mock_asset_transaction_dao.get_user_asset_transactions.return_value = [mock_precise_transaction]

        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        assert result.success is True
        assert len(result.data) == 1

        precise_transaction = result.data[0]
        assert precise_transaction.quantity == Decimal("1.12345678")
        assert precise_transaction.price == Decimal("45000.12345")

    @pytest.mark.asyncio
    async def test_get_asset_transactions_with_different_statuses(self, mock_request, mock_current_user,
                                                                mock_asset_transaction_dao, mock_asset_dao,
                                                                mock_user_dao, mock_validate_order_history_business_rules):
        """Test get_asset_transactions with different transaction statuses"""
                # Mock transactions with different statuses
        mock_pending_transaction = Mock()
        mock_pending_transaction.asset_id = "BTC"
        mock_pending_transaction.transaction_type = "BUY"
        mock_pending_transaction.quantity = Decimal("1.0")
        mock_pending_transaction.price = Decimal("45000.00")
        mock_pending_transaction.status = "PENDING"
        mock_pending_transaction.created_at = datetime.now(timezone.utc)

        mock_failed_transaction = Mock()
        mock_failed_transaction.asset_id = "BTC"
        mock_failed_transaction.transaction_type = "SELL"
        mock_failed_transaction.quantity = Decimal("0.5")
        mock_failed_transaction.price = Decimal("46000.00")
        mock_failed_transaction.status = "FAILED"
        mock_failed_transaction.created_at = datetime.now(timezone.utc)

        mock_asset_transaction_dao.get_user_asset_transactions.return_value = [mock_pending_transaction, mock_failed_transaction]

        result = await get_asset_transactions(
            asset_id="BTC",
            limit=50,
            offset=0,
            request=mock_request,
            current_user=mock_current_user,
            asset_transaction_dao=mock_asset_transaction_dao,
            asset_dao=mock_asset_dao,
            user_dao=mock_user_dao
        )

        assert result.success is True
        assert len(result.data) == 2

                # Check pending transaction
        pending_transaction = result.data[0]
        assert pending_transaction.status == "PENDING"

        # Check failed transaction
        failed_transaction = result.data[1]
        assert failed_transaction.status == "FAILED"
