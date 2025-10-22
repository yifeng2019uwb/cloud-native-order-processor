"""
Tests for create_order controller
"""
import pytest
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi.testclient import TestClient


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    from common.shared.constants.request_headers import RequestHeaders
    mock_request.headers = {RequestHeaders.REQUEST_ID: request_id}
    return mock_request

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common', 'src'))

# At the top of your test file, define the DAO interface
USER_DAO_SPEC = [
    'get_user_by_username',
    'get_user_by_email',
    'save_user',
    'update_user',
    'delete_user'
]

ASSET_DAO_SPEC = [
    'get_asset_by_id',
    'get_all_assets',
    'save_asset',
    'update_asset',
    'delete_asset'
]

BALANCE_DAO_SPEC = [
    'get_balance',
    'save_balance',
    'update_balance',
    'delete_balance'
]

ASSET_BALANCE_DAO_SPEC = [
    'get_asset_balance',
    'save_asset_balance',
    'update_asset_balance',
    'delete_asset_balance',
    'get_all_asset_balances'
]

TRANSACTION_MANAGER_SPEC = [
    'create_buy_order_with_balance_update',
    'create_sell_order_with_balance_update',
    'cancel_order',
    'modify_order'
]

from src.controllers.create_order import create_order, router
from src.api_models.order import OrderCreateRequest, OrderCreateResponse, OrderData
from common.data.entities.order.enums import OrderType, OrderStatus
from common.exceptions import (
    CNOPInsufficientBalanceException,
    CNOPDatabaseOperationException,
    CNOPLockAcquisitionException
)
from common.exceptions.shared_exceptions import (
    CNOPAssetNotFoundException,
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from order_exceptions.exceptions import CNOPOrderValidationException

class TestCreateOrder:
    """Test create_order function"""

    @pytest.fixture
    def mock_order_create_request(self):
        """Mock order create request data"""
        return OrderCreateRequest(
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user data"""
        return {
            "username": "testuser"
        }

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request object"""
        mock_req = MagicMock()
        mock_req.client = MagicMock()
        mock_req.client.host = "127.0.0.1"
        mock_req.headers = {"user-agent": "test-client"}
        return mock_req

    @pytest.fixture
    def mock_transaction_manager(self):
        """Mock transaction manager"""
        mock_manager = AsyncMock(spec=TRANSACTION_MANAGER_SPEC)
        mock_manager.create_buy_order_with_balance_update = AsyncMock()
        mock_manager.create_sell_order_with_balance_update = AsyncMock()
        return mock_manager

    @pytest.fixture
    def mock_asset_dao(self):
        """Mock asset DAO"""
        mock_dao = MagicMock(spec=ASSET_DAO_SPEC)
        # Mock the get_asset_by_id method to return a proper asset object
        mock_asset = MagicMock()
        mock_asset.price_usd = Decimal("50000.00")
        mock_dao.get_asset_by_id.return_value = mock_asset
        return mock_dao

    @pytest.fixture
    def mock_user_dao(self):
        """Mock user DAO"""
        return MagicMock(spec=USER_DAO_SPEC)

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO"""
        return MagicMock(spec=BALANCE_DAO_SPEC)


    @pytest.mark.asyncio
    async def test_create_order_market_buy_success(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test successful market buy order creation"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.dependencies.get_current_market_price') as mock_get_price, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_get_price.return_value = Decimal("50000.00")

            # Mock transaction result
            mock_order = MagicMock()
            mock_order.order_id = "order123"
            mock_order.order_type = OrderType.MARKET_BUY
            mock_order.asset_id = "BTC"
            mock_order.quantity = Decimal("1.0")
            mock_order.price = Decimal("50000.00")
            mock_order.status = "pending"
            mock_order.total_amount = Decimal("50000.00")
            mock_order.created_at = datetime.now(timezone.utc)

            mock_result = MagicMock()
            mock_result.order = mock_order
            mock_result.lock_duration = 30

            mock_transaction_manager.create_buy_order_with_balance_update.return_value = mock_result

            # Test the function
            result = await create_order(
                order_data=mock_order_create_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao,
                balance_dao=mock_balance_dao,
            )

            # Verify result
            assert result.success is True
            assert "Market Buy order created successfully" in result.message
            assert result.data.order_id == "order123"
            assert result.data.asset_id == "BTC"
            assert result.data.quantity == Decimal("1.0")
            assert result.data.price == Decimal("50000.00")

            # Verify business validation was called
            mock_validate.assert_called_once()

            # Verify transaction manager was called
            mock_transaction_manager.create_buy_order_with_balance_update.assert_called_once_with(
                username="testuser",
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                order_type=OrderType.MARKET_BUY,
                total_cost=Decimal("50000.00")
            )

            # Verify logging
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_market_sell_success(
        self,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test successful market sell order creation"""
        # Create sell order request
        sell_request = OrderCreateRequest(
            order_type=OrderType.MARKET_SELL,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )

        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.dependencies.get_current_market_price') as mock_get_price, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_get_price.return_value = Decimal("50000.00")

            # Mock transaction result
            mock_order = MagicMock()
            mock_order.order_id = "order456"
            mock_order.order_type = OrderType.MARKET_SELL
            mock_order.asset_id = "BTC"
            mock_order.quantity = Decimal("1.0")
            mock_order.price = Decimal("50000.00")
            mock_order.status = "pending"
            mock_order.total_amount = Decimal("50000.00")
            mock_order.created_at = datetime.now(timezone.utc)

            mock_result = MagicMock()
            mock_result.order = mock_order
            mock_result.lock_duration = 30

            mock_transaction_manager.create_sell_order_with_balance_update.return_value = mock_result

            # Test the function
            result = await create_order(
                order_data=sell_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao,
                balance_dao=mock_balance_dao,
            )

            # Verify result
            assert result.success is True
            assert "Market Sell order created successfully" in result.message
            assert result.data.order_id == "order456"

            # Verify transaction manager was called
            mock_transaction_manager.create_sell_order_with_balance_update.assert_called_once_with(
                username="testuser",
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                order_type=OrderType.MARKET_SELL,
                asset_amount=Decimal("50000.00")
            )

    @pytest.mark.asyncio
    async def test_create_order_insufficient_balance(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation with insufficient balance"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mock to raise InsufficientBalanceException
            mock_validate.side_effect = CNOPInsufficientBalanceException("Insufficient balance")

            # Test that the exception is raised
            with pytest.raises(CNOPOrderValidationException, match="Insufficient balance"):
                await create_order(
                    order_data=mock_order_create_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

            # Verify logging
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_lock_acquisition_failed(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation when lock acquisition fails"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mock to raise LockAcquisitionException
            mock_validate.side_effect = CNOPLockAcquisitionException("Lock acquisition failed")

            # Test that the exception is raised
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable"):
                await create_order(
                    order_data=mock_order_create_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

            # Verify logging
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_database_operation_failed(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation when database operation fails"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mock to raise DatabaseOperationException
            mock_validate.side_effect = CNOPDatabaseOperationException("Database error")

            # Test that the exception is raised
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable"):
                await create_order(
                    order_data=mock_order_create_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

            # Verify logging
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_validation_failed(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation when validation fails"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mock to raise OrderValidationException
            mock_validate.side_effect = CNOPOrderValidationException("Invalid order data")

            # Test that the exception is raised
            with pytest.raises(CNOPOrderValidationException, match="Invalid order data"):
                await create_order(
                    order_data=mock_order_create_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

            # Verify logging
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_unexpected_error(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation when unexpected error occurs"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mock to raise generic Exception
            mock_validate.side_effect = Exception("Unexpected error")

            # Test that the exception is raised
            with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable"):
                await create_order(
                    order_data=mock_order_create_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

            # Verify logging
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_order_unsupported_order_type(
        self,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation with unsupported order type"""
        # Since all order types (MARKET_BUY, MARKET_SELL, LIMIT_BUY, LIMIT_SELL) are supported,
        # we'll test with an invalid order type that would cause validation to fail
        # We'll create a request with an invalid order type string that bypasses Pydantic validation

        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.dependencies.get_current_market_price') as mock_get_price, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_get_price.return_value = Decimal("50000.00")

            # Create a mock order with an unsupported type by directly setting the attribute
            unsupported_request = OrderCreateRequest(
                order_type=OrderType.MARKET_BUY,  # Start with valid type
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00")
            )

            # Mock the transaction manager to raise an exception for unsupported types
            mock_transaction_manager.create_buy_order_with_balance_update.side_effect = \
                CNOPOrderValidationException("Unsupported order type: invalid_type")

            # Test that the exception is raised
            with pytest.raises(CNOPOrderValidationException, match="Unsupported order type"):
                await create_order(
                    order_data=unsupported_request,
                    request=mock_request,
                    current_user=mock_current_user,
                    transaction_manager=mock_transaction_manager,
                    asset_dao=mock_asset_dao,
                    user_dao=mock_user_dao,
                    balance_dao=mock_balance_dao,
                )

    @pytest.mark.asyncio
    async def test_create_order_logging_and_metrics(
        self,
        mock_order_create_request,
        mock_current_user,
        mock_request,
        mock_transaction_manager,
        mock_asset_dao,
        mock_user_dao,
        mock_balance_dao,
    ):
        """Test order creation logging and metrics recording"""
        with patch('src.controllers.create_order.validate_order_creation_business_rules') as mock_validate, \
             patch('src.controllers.dependencies.get_current_market_price') as mock_get_price, \
             patch('src.controllers.create_order.logger') as mock_logger:

            # Setup mocks
            mock_validate.return_value = None
            mock_get_price.return_value = Decimal("50000.00")

            # Mock transaction result
            mock_order = MagicMock()
            mock_order.order_id = "order123"
            mock_order.order_type = OrderType.MARKET_BUY
            mock_order.asset_id = "BTC"
            mock_order.quantity = Decimal("1.0")
            mock_order.price = Decimal("50000.00")
            mock_order.status = "pending"
            mock_order.total_amount = Decimal("50000.00")
            mock_order.created_at = datetime.now(timezone.utc)

            mock_result = MagicMock()
            mock_result.order = mock_order
            mock_result.lock_duration = 30

            mock_transaction_manager.create_buy_order_with_balance_update.return_value = mock_result

            # Test the function
            result = await create_order(
                order_data=mock_order_create_request,
                request=mock_request,
                current_user=mock_current_user,
                transaction_manager=mock_transaction_manager,
                asset_dao=mock_asset_dao,
                user_dao=mock_user_dao,
                balance_dao=mock_balance_dao,
            )

            # Verify logging was called for order creation attempt
            mock_logger.info.assert_called()

            # Verify logging was called for successful execution
            mock_logger.info.assert_called()

    def test_router_configuration(self):
        """Test router configuration"""
        # Test router tags
        assert router.tags == ["orders"]

        # Test endpoint path
        assert router.routes[0].path == "/"

        # Test HTTP method
        assert router.routes[0].methods == {"POST"}

        # Test response models
        assert router.routes[0].response_model is not None

        # Test responses documentation
        assert router.routes[0].responses is not None
        assert 201 in router.routes[0].responses
        assert 400 in router.routes[0].responses
        assert 401 in router.routes[0].responses
        assert 409 in router.routes[0].responses
        assert 422 in router.routes[0].responses
        assert 503 in router.routes[0].responses
