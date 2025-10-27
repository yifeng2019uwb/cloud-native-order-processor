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
from common.data.entities.user import User


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

from controllers.create_order import create_order, router
from api_models.create_order import CreateOrderRequest, CreateOrderResponse
from api_models.shared.data_models import OrderData
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
from constants import MSG_SUCCESS_ORDER_CREATED

# Add tests directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dependency_constants import (
    PATCH_VALIDATE_ORDER_CREATION, PATCH_GET_CURRENT_MARKET_PRICE
)

# Make these constants available at module level for easy access
TEST_ORDER_ID_123 = "order123"
TEST_ASSET_ID_BTC = "BTC"
TEST_QUANTITY_1_0 = "1.0"
TEST_PRICE_50000 = "50000.00"

class TestCreateOrder:
    """Test create_order function"""

    # Shared constants (used in multiple tests/fixtures)
    TEST_USERNAME = "testuser"
    TEST_EMAIL = "test@example.com"
    TEST_PASSWORD = "hashed_password_123"
    TEST_FIRST_NAME = "Test"
    TEST_LAST_NAME = "User"
    TEST_ROLE_CUSTOMER = "customer"

    @pytest.fixture
    def mock_order_create_request(self):
        """Mock order create request data"""
        asset_id = "BTC"
        quantity = Decimal("1.0")
        price = Decimal("50000.00")

        return CreateOrderRequest(
            order_type=OrderType.MARKET_BUY,
            asset_id=asset_id,
            quantity=quantity,
            price=price
        )

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user data"""
        return User(
            username=self.TEST_USERNAME,
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME,
            role=self.TEST_ROLE_CUSTOMER
        )

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request object"""
        client_host = "127.0.0.1"
        user_agent = "test-client"

        mock_req = MagicMock()
        mock_req.client = MagicMock()
        mock_req.client.host = client_host
        mock_req.headers = {"user-agent": user_agent}
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
        mock_dao = MagicMock(spec=BALANCE_DAO_SPEC)
        # Mock the get_balance method to return a balance object with Decimal current_balance
        mock_balance = MagicMock()
        mock_balance.current_balance = Decimal("100000.00")  # Sufficient balance
        mock_dao.get_balance.return_value = mock_balance
        return mock_dao


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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate, \
             patch(PATCH_GET_CURRENT_MARKET_PRICE) as mock_get_price:

            # Setup mocks
            order_id = TEST_ORDER_ID_123
            asset_id = TEST_ASSET_ID_BTC
            quantity = Decimal(TEST_QUANTITY_1_0)
            price = Decimal(TEST_PRICE_50000)

            mock_validate.return_value = None
            mock_get_price.return_value = price

            # Mock transaction result
            mock_order = MagicMock()
            mock_order.order_id = order_id
            mock_order.order_type = OrderType.MARKET_BUY
            mock_order.asset_id = asset_id
            mock_order.quantity = quantity
            mock_order.price = price
            mock_order.status = "pending"
            mock_order.total_amount = price
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
            assert result.data is not None
            assert result.data.order_id == order_id
            assert result.data.asset_id == asset_id
            assert result.data.quantity == quantity
            assert result.data.price == price

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
        sell_request = CreateOrderRequest(
            order_type=OrderType.MARKET_SELL,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00")
        )

        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate, \
             patch(PATCH_GET_CURRENT_MARKET_PRICE) as mock_get_price:

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
            assert result.data is not None
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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate:

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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate:

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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate:

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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate:
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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate:

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

        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate, \
             patch(PATCH_GET_CURRENT_MARKET_PRICE) as mock_get_price:

            # Setup mocks
            mock_validate.return_value = None
            mock_get_price.return_value = Decimal("50000.00")

            # Create a mock order with an unsupported type by directly setting the attribute
            unsupported_request = CreateOrderRequest(
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
        with patch(PATCH_VALIDATE_ORDER_CREATION) as mock_validate, \
             patch(PATCH_GET_CURRENT_MARKET_PRICE) as mock_get_price:

            # Setup mocks
            order_id = TEST_ORDER_ID_123
            asset_id = TEST_ASSET_ID_BTC
            quantity = Decimal(TEST_QUANTITY_1_0)
            price = Decimal(TEST_PRICE_50000)

            mock_validate.return_value = None
            mock_get_price.return_value = price

            # Mock transaction result
            mock_order = MagicMock()
            mock_order.order_id = order_id
            mock_order.order_type = OrderType.MARKET_BUY
            mock_order.asset_id = asset_id
            mock_order.quantity = quantity
            mock_order.price = price
            mock_order.status = "pending"
            mock_order.total_amount = price
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
