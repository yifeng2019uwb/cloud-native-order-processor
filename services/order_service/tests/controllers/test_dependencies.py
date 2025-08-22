"""
Tests for dependencies module - Order Service Controller Dependencies
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, Request, Depends, status


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

ORDER_DAO_SPEC = [
    'get_order',
    'save_order',
    'update_order',
    'delete_order',
    'get_orders_by_user'
]

ASSET_BALANCE_DAO_SPEC = [
    'get_asset_balance',
    'save_asset_balance',
    'update_asset_balance',
    'delete_asset_balance',
    'get_all_asset_balances'
]

ASSET_TRANSACTION_DAO_SPEC = [
    'get_asset_transactions',
    'save_asset_transaction',
    'update_asset_transaction',
    'delete_asset_transaction'
]

TRANSACTION_MANAGER_SPEC = [
    'create_buy_order_with_balance_update',
    'create_sell_order_with_balance_update',
    'cancel_order',
    'modify_order'
]

# Import the functions to test
from src.controllers.dependencies import (
    get_order_dao_dependency,
    get_user_dao_dependency,
    get_balance_dao_dependency,
    get_asset_dao_dependency,
    get_asset_balance_dao_dependency,
    get_asset_transaction_dao_dependency,
    get_transaction_manager,
    get_current_user,
    get_current_market_price
)


class TestDependencies:
    """Test dependency injection functions"""

    @pytest.fixture
    def mock_dynamodb_connection(self):
        """Mock DynamoDB connection"""
        connection = Mock()
        return connection



    def test_get_order_dao_dependency(self):
        """Test get_order_dao_dependency"""
        with patch('src.controllers.dependencies.get_order_dao') as mock_get_order_dao:
            mock_dao = Mock(spec=ORDER_DAO_SPEC)
            mock_get_order_dao.return_value = mock_dao

            result = get_order_dao_dependency()

            assert result == mock_dao
            mock_get_order_dao.assert_called_once()

    def test_get_user_dao_dependency(self):
        """Test get_user_dao_dependency"""
        with patch('src.controllers.dependencies.get_user_dao') as mock_get_user_dao:
            mock_dao = Mock(spec=USER_DAO_SPEC)
            mock_get_user_dao.return_value = mock_dao

            result = get_user_dao_dependency()

            assert result == mock_dao
            mock_get_user_dao.assert_called_once()

    def test_get_balance_dao_dependency(self):
        """Test get_balance_dao_dependency"""
        with patch('src.controllers.dependencies.get_balance_dao') as mock_get_balance_dao:
            mock_dao = Mock(spec=BALANCE_DAO_SPEC)
            mock_get_balance_dao.return_value = mock_dao

            result = get_balance_dao_dependency()

            assert result == mock_dao
            mock_get_balance_dao.assert_called_once()

    def test_get_asset_dao_dependency(self):
        """Test get_asset_dao_dependency"""
        with patch('src.controllers.dependencies.get_asset_dao') as mock_get_asset_dao:
            mock_dao = Mock(spec=ASSET_DAO_SPEC)
            mock_get_asset_dao.return_value = mock_dao

            result = get_asset_dao_dependency()

            assert result == mock_dao
            mock_get_asset_dao.assert_called_once()

    def test_get_asset_balance_dao_dependency(self):
        """Test get_asset_balance_dao_dependency"""
        with patch('src.controllers.dependencies.dynamodb_manager') as mock_dynamodb_manager, \
             patch('src.controllers.dependencies.AssetBalanceDAO') as mock_asset_balance_dao_class:

            mock_connection = Mock()
            mock_dynamodb_manager.get_connection.return_value = mock_connection

            mock_dao = Mock(spec=ASSET_BALANCE_DAO_SPEC)
            mock_asset_balance_dao_class.return_value = mock_dao

            result = get_asset_balance_dao_dependency()

            assert result == mock_dao
            mock_dynamodb_manager.get_connection.assert_called_once()
            mock_asset_balance_dao_class.assert_called_once_with(mock_connection)

    def test_get_asset_transaction_dao_dependency(self):
        """Test get_asset_transaction_dao_dependency"""
        with patch('src.controllers.dependencies.dynamodb_manager') as mock_dynamodb_manager, \
             patch('src.controllers.dependencies.AssetTransactionDAO') as mock_asset_transaction_dao_class:

            mock_connection = Mock()
            mock_dynamodb_manager.get_connection.return_value = mock_connection

            mock_dao = Mock(spec=ASSET_TRANSACTION_DAO_SPEC)
            mock_asset_transaction_dao_class.return_value = mock_dao

            result = get_asset_transaction_dao_dependency()

            assert result == mock_dao
            mock_dynamodb_manager.get_connection.assert_called_once()
            mock_asset_transaction_dao_class.assert_called_once_with(mock_connection)

    def test_get_transaction_manager(self):
        """Test get_transaction_manager"""
        with patch('src.controllers.dependencies.get_user_dao_dependency') as mock_get_user_dao, \
             patch('src.controllers.dependencies.get_balance_dao_dependency') as mock_get_balance_dao, \
             patch('src.controllers.dependencies.get_order_dao_dependency') as mock_get_order_dao, \
             patch('src.controllers.dependencies.get_asset_dao_dependency') as mock_get_asset_dao, \
             patch('src.controllers.dependencies.get_asset_balance_dao_dependency') as mock_get_asset_balance_dao, \
             patch('src.controllers.dependencies.get_asset_transaction_dao_dependency') as mock_get_asset_transaction_dao, \
             patch('src.controllers.dependencies.TransactionManager') as mock_transaction_manager_class:

            mock_user_dao = Mock(spec=USER_DAO_SPEC)
            mock_balance_dao = Mock(spec=BALANCE_DAO_SPEC)
            mock_order_dao = Mock(spec=ORDER_DAO_SPEC)
            mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)
            mock_asset_balance_dao = Mock(spec=ASSET_BALANCE_DAO_SPEC)
            mock_asset_transaction_dao = Mock(spec=ASSET_TRANSACTION_DAO_SPEC)

            mock_get_user_dao.return_value = mock_user_dao
            mock_get_balance_dao.return_value = mock_balance_dao
            mock_get_order_dao.return_value = mock_order_dao
            mock_get_asset_dao.return_value = mock_asset_dao
            mock_get_asset_balance_dao.return_value = mock_asset_balance_dao
            mock_get_asset_transaction_dao.return_value = mock_asset_transaction_dao

            mock_transaction_manager = Mock(spec=TRANSACTION_MANAGER_SPEC)
            mock_transaction_manager_class.return_value = mock_transaction_manager

            result = get_transaction_manager()

            assert result == mock_transaction_manager
            mock_transaction_manager_class.assert_called_once_with(
                user_dao=mock_user_dao,
                balance_dao=mock_balance_dao,
                order_dao=mock_order_dao,
                asset_dao=mock_asset_dao,
                asset_balance_dao=mock_asset_balance_dao,
                asset_transaction_dao=mock_asset_transaction_dao
            )

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test get_current_user with valid Gateway headers"""
        # Mock request and headers
        mock_request = Mock()

        result = await get_current_user(
            request=mock_request,
            x_source="gateway",
            x_auth_service="auth-service",
            x_user_id="testuser",
            x_user_role="customer"
        )

        assert result["username"] == "testuser"
        assert result["role"] == "customer"

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user with missing user ID header"""
        mock_request = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                x_source="gateway",
                x_auth_service="auth-service",
                x_user_id=None,
                x_user_role="customer"
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "User authentication required"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_source(self):
        """Test get_current_user with invalid source header"""
        mock_request = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                x_source="invalid-source",
                x_auth_service="auth-service",
                x_user_id="testuser",
                x_user_role="customer"
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid request source"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_auth_service(self):
        """Test get_current_user with invalid auth service header"""
        mock_request = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                x_source="gateway",
                x_auth_service="invalid-service",
                x_user_id="testuser",
                x_user_role="customer"
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid authentication service"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_source_header(self):
        """Test get_current_user with missing source header"""
        mock_request = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                x_source=None,
                x_auth_service="auth-service",
                x_user_id="testuser",
                x_user_role="customer"
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid request source"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_auth_service_header(self):
        """Test get_current_user with missing auth service header"""
        mock_request = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                x_source="gateway",
                x_auth_service=None,
                x_user_id="testuser",
                x_user_role="customer"
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid authentication service"

    @pytest.mark.asyncio
    async def test_get_current_user_default_role(self):
        """Test get_current_user with default role when not provided"""
        mock_request = Mock()

        result = await get_current_user(
            request=mock_request,
            x_source="gateway",
            x_auth_service="auth-service",
            x_user_id="testuser",
            x_user_role=None
        )

        assert result["username"] == "testuser"
        assert result["role"] == "customer"  # Default role

    def test_get_current_market_price_success(self):
        """Test get_current_market_price with valid asset"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset with price
        mock_asset = Mock()
        mock_asset.price_usd = Decimal("45000.50")

        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        result = get_current_market_price("BTC", mock_asset_dao)

        assert result == Decimal("45000.50")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_current_market_price_with_string_price(self):
        """Test get_current_market_price with string price"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset with string price
        mock_asset = Mock()
        mock_asset.price_usd = "45000.50"

        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        result = get_current_market_price("BTC", mock_asset_dao)

        assert result == Decimal("45000.50")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_current_market_price_with_float_price(self):
        """Test get_current_market_price with float price"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset with float price
        mock_asset = Mock()
        mock_asset.price_usd = 45000.50

        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        result = get_current_market_price("BTC", mock_asset_dao)

        assert result == Decimal("45000.50")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_current_market_price_with_decimal_price(self):
        """Test get_current_market_price with decimal price"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset with decimal price
        mock_asset = Mock()
        mock_asset.price_usd = Decimal("45000.50")

        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        result = get_current_market_price("BTC", mock_asset_dao)

        assert result == Decimal("45000.50")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_current_market_price_asset_not_found(self):
        """Test get_current_market_price with asset not found"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset not found
        mock_asset_dao.get_asset_by_id.return_value = None

        # The function will try to access price_usd on None, causing AttributeError
        with pytest.raises(AttributeError):
            get_current_market_price("BTC", mock_asset_dao)

        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_current_market_price_no_price(self):
        """Test get_current_market_price with asset having no price"""
        # Mock asset DAO
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset with no price
        mock_asset = Mock()
        mock_asset.price_usd = None

        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        # The function will try to convert "None" string to Decimal, causing InvalidOperation
        from decimal import InvalidOperation
        with pytest.raises(InvalidOperation):
            get_current_market_price("BTC", mock_asset_dao)

        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    @pytest.mark.asyncio
    async def test_get_current_user_logging_success(self):
        """Test that logging is performed correctly in get_current_user success case"""
        with patch('src.controllers.dependencies.logger') as mock_logger:
            mock_request = Mock()

            result = await get_current_user(
                request=mock_request,
                x_source="gateway",
                x_auth_service="auth-service",
                x_user_id="testuser",
                x_user_role="customer"
            )

            # Verify logging was called
            mock_logger.info.assert_called_once_with("User authenticated via Gateway: testuser")

    @pytest.mark.asyncio
    async def test_get_current_user_logging_failure(self):
        """Test that logging is performed correctly in get_current_user failure case"""
        with patch('src.controllers.dependencies.logger') as mock_logger:
            mock_request = Mock()

            with pytest.raises(HTTPException):
                await get_current_user(
                    request=mock_request,
                    x_source="invalid-source",
                    x_auth_service="auth-service",
                    x_user_id="testuser",
                    x_user_role="customer"
                )

            # Verify warning logging was called
            mock_logger.warning.assert_called_once_with("Invalid source header: invalid-source")
