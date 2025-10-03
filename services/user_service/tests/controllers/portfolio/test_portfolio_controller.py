"""
Tests for portfolio controller
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from common.exceptions import (
    CNOPDatabaseOperationException
)
from common.exceptions.shared_exceptions import (
    CNOPAssetNotFoundException,
    CNOPEntityNotFoundException,
    CNOPInternalServerException
)


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    from common.shared.constants.request_headers import RequestHeaders
    mock_request.headers = {RequestHeaders.REQUEST_ID: request_id}
    return mock_request

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'common', 'src'))

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
    'get_assets_by_ids',
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

# Import the function directly - we'll mock dependencies in individual tests
from src.controllers.portfolio.portfolio_controller import get_user_portfolio


class TestPortfolioController:
    """Test portfolio controller functions"""

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
        from common.data.entities.user import User
        return User(
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            first_name="Test",
            last_name="User",
            role="customer"
        )

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO"""
        dao = Mock(spec=BALANCE_DAO_SPEC)

        # Mock USD balance object
        mock_usd_balance = Mock()
        mock_usd_balance.current_balance = Decimal("10000.00")

        dao.get_balance.return_value = mock_usd_balance

        return dao

    @pytest.fixture
    def mock_asset_balance_dao(self):
        """Mock asset balance DAO"""
        dao = Mock(spec=ASSET_BALANCE_DAO_SPEC)

        # Mock asset balance objects
        mock_btc_balance = Mock()
        mock_btc_balance.asset_id = "BTC"
        mock_btc_balance.quantity = Decimal("1.5")

        mock_eth_balance = Mock()
        mock_eth_balance.asset_id = "ETH"
        mock_eth_balance.quantity = Decimal("10.0")

        dao.get_all_asset_balances.return_value = [mock_btc_balance, mock_eth_balance]

        return dao

    @pytest.fixture
    def mock_user_dao(self):
        """Mock user DAO"""
        dao = Mock(spec=USER_DAO_SPEC)
        dao.get_user_by_username.return_value = Mock()
        return dao

    @pytest.fixture
    def mock_asset_dao(self):
        """Mock asset DAO"""
        dao = Mock(spec=ASSET_DAO_SPEC)

        # Mock asset objects with price_usd
        mock_btc_asset = Mock()
        mock_btc_asset.asset_id = "BTC"
        mock_btc_asset.price_usd = Decimal("45000.00")

        mock_eth_asset = Mock()
        mock_eth_asset.asset_id = "ETH"
        mock_eth_asset.price_usd = Decimal("3000.00")

        def mock_get_asset_by_id(asset_id):
            if asset_id == "BTC":
                return mock_btc_asset
            elif asset_id == "ETH":
                return mock_eth_asset
            else:
                return None

        def mock_get_assets_by_ids(asset_ids):
            result = {}
            for asset_id in asset_ids:
                if asset_id == "BTC":
                    result[asset_id] = mock_btc_asset
                elif asset_id == "ETH":
                    result[asset_id] = mock_eth_asset
            return result

        dao.get_asset_by_id.side_effect = mock_get_asset_by_id
        dao.get_assets_by_ids.side_effect = mock_get_assets_by_ids

        return dao



    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_success(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                            mock_balance_dao, mock_asset_balance_dao,
                                            mock_user_dao, mock_asset_dao):
        """Test successful retrieval of user portfolio"""
        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        # Verify validation was called
        mock_validate_user_permissions.assert_called_once_with(
            username="testuser",
            action="view_portfolio",
            user_dao=mock_user_dao
        )

        # Verify DAO calls
        mock_balance_dao.get_balance.assert_called_once_with("testuser")
        mock_asset_balance_dao.get_all_asset_balances.assert_called_once_with("testuser")

        # Verify response
        assert result.success is True
        assert result.message == "Portfolio retrieved successfully"

        # Check portfolio data
        portfolio_data = result.data
        assert portfolio_data["username"] == "testuser"
        assert portfolio_data["usd_balance"] == Decimal("10000.00")
        assert portfolio_data["asset_count"] == 2

        # Check asset calculations
        assets = portfolio_data["assets"]
        assert len(assets) == 2

        # BTC asset
        btc_asset = assets[0]
        assert btc_asset.asset_id == "BTC"
        assert btc_asset.quantity == Decimal("1.5")
        assert btc_asset.current_price == Decimal("45000.00")
        assert btc_asset.market_value == Decimal("67500.00")  # 1.5 * 45000

        # ETH asset
        eth_asset = assets[1]
        assert eth_asset.asset_id == "ETH"
        assert eth_asset.quantity == Decimal("10.0")
        assert eth_asset.current_price == Decimal("3000.00")
        assert eth_asset.market_value == Decimal("30000.00")  # 10.0 * 3000

        # Check total values
        assert portfolio_data["total_asset_value"] == Decimal("97500.00")  # 67500 + 30000
        assert portfolio_data["total_portfolio_value"] == Decimal("107500.00")  # 10000 + 97500

        # Check percentages (approximate due to decimal precision)
        btc_percentage = float(btc_asset.percentage)
        eth_percentage = float(eth_asset.percentage)
        assert 62.0 < btc_percentage < 63.0  # 67500/107500 ≈ 62.79%
        assert 27.0 < eth_percentage < 28.0  # 30000/107500 ≈ 27.91%


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_unauthorized_access(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                        mock_balance_dao, mock_asset_balance_dao,
                                                        mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio with unauthorized access attempt"""
        from user_exceptions import CNOPUserValidationException

        # Mock validation to raise exception
        mock_validate_user_permissions.side_effect = CNOPUserValidationException("User not found")

        with pytest.raises(CNOPUserValidationException, match="User not found"):
            get_user_portfolio(
                request=mock_request,
                current_user=mock_current_user,
                balance_dao=mock_balance_dao,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_no_usd_balance(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                    mock_balance_dao, mock_asset_balance_dao,
                                                    mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio when user has no USD balance"""
        # Mock no USD balance
        mock_balance_dao.get_balance.return_value = None

        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True

        portfolio_data = result.data
        assert portfolio_data["usd_balance"] == Decimal("0")
        assert portfolio_data["total_portfolio_value"] == Decimal("97500.00")  # Only asset value


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_no_assets(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                            mock_balance_dao, mock_asset_balance_dao,
                                            mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio when user has no assets"""
        # Mock no asset balances
        mock_asset_balance_dao.get_all_asset_balances.return_value = []

        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True

        portfolio_data = result.data
        assert portfolio_data["asset_count"] == 0
        assert len(portfolio_data["assets"]) == 0
        assert portfolio_data["total_asset_value"] == Decimal("0")
        assert portfolio_data["total_portfolio_value"] == Decimal("10000.00")  # Only USD balance


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_zero_total_value(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                    mock_balance_dao, mock_asset_balance_dao,
                                                    mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio when total portfolio value is zero"""
        # Mock zero USD balance and no assets
        mock_balance_dao.get_balance.return_value = None
        mock_asset_balance_dao.get_all_asset_balances.return_value = []

        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True

        portfolio_data = result.data
        assert portfolio_data["total_portfolio_value"] == Decimal("0")

        # Percentages should be zero when total is zero
        assets = portfolio_data["assets"]
        assert len(assets) == 0


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_database_error(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                mock_balance_dao, mock_asset_balance_dao,
                                                mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio with database operation exception"""

        mock_balance_dao.get_balance.side_effect = CNOPDatabaseOperationException("DB error")

        with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
            get_user_portfolio(
                request=mock_request,
                current_user=mock_current_user,
                balance_dao=mock_balance_dao,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_unexpected_error(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                    mock_balance_dao, mock_asset_balance_dao,
                                                    mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio with unexpected exception"""

        mock_balance_dao.get_balance.side_effect = Exception("Unexpected error")

        with pytest.raises(CNOPInternalServerException, match="The service is temporarily unavailable. Please try again later."):
            get_user_portfolio(
                request=mock_request,
                current_user=mock_current_user,
                balance_dao=mock_balance_dao,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_with_high_precision_values(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                            mock_balance_dao, mock_asset_balance_dao,
                                                            mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio with high precision quantity and price values"""
        # Mock high precision asset balance
        mock_precise_balance = Mock()
        mock_precise_balance.asset_id = "BTC"
        mock_precise_balance.quantity = Decimal("1.12345678")

        mock_asset_balance_dao.get_all_asset_balances.return_value = [mock_precise_balance]

                # Mock high precision price in asset DAO
        mock_precise_asset = Mock()
        mock_precise_asset.price_usd = Decimal("45000.12345")

        # Override the side_effect for this specific test
        def mock_get_assets_by_ids_precise(asset_ids):
            result = {}
            for asset_id in asset_ids:
                if asset_id == "BTC":
                    result[asset_id] = mock_precise_asset
            return result

        mock_asset_dao.get_assets_by_ids.side_effect = mock_get_assets_by_ids_precise

        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True

        portfolio_data = result.data
        assets = portfolio_data["assets"]
        assert len(assets) == 1

        btc_asset = assets[0]
        assert btc_asset.quantity == Decimal("1.12345678")
        assert btc_asset.current_price == Decimal("45000.12345")

        # Calculate expected market value
        expected_market_value = Decimal("1.12345678") * Decimal("45000.12345")
        assert btc_asset.market_value == expected_market_value


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_logging(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                        mock_balance_dao, mock_asset_balance_dao,
                                        mock_user_dao, mock_asset_dao):
        """Test that logging is performed correctly in get_user_portfolio"""
        with patch('src.controllers.portfolio.portfolio_controller.logger') as mock_logger:
            get_user_portfolio(
                request=mock_request,
                current_user=mock_current_user,
                balance_dao=mock_balance_dao,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )

            # Verify info logging was called
            mock_logger.info.assert_called()

            # Check that the success log was called
            success_calls = [call[1]["message"] for call in mock_logger.info.call_args_list]
            assert any("Portfolio retrieved successfully" in call for call in success_calls)


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_unauthorized_logging(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                        mock_balance_dao, mock_asset_balance_dao,
                                                        mock_user_dao, mock_asset_dao):
        """Test that unauthorized access logging is performed correctly"""
        from user_exceptions import CNOPUserValidationException
        from src.validation.business_validators import validate_user_permissions

        # Mock user_dao to return None (user not found)
        mock_user_dao.get_user_by_username.return_value = None

        # Make the mock call the real function
        mock_validate_user_permissions.side_effect = lambda username, action, user_dao: validate_user_permissions(username, action, user_dao)

        with patch('src.validation.business_validators.logger') as mock_logger:
            with pytest.raises(CNOPUserValidationException):
                get_user_portfolio(
                    request=mock_request,
                    current_user=mock_current_user,
                    balance_dao=mock_balance_dao,
                    asset_balance_dao=mock_asset_balance_dao,
                    user_dao=mock_user_dao,
                    asset_dao=mock_asset_dao
                )

            # Verify warning logging was called for validation error
            mock_logger.warning.assert_called()

            # Check that the validation error log was called
            warning_calls = [call[1]["message"] for call in mock_logger.warning.call_args_list]
            assert any("User not found for permission check" in call for call in warning_calls)


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_error_logging(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                mock_balance_dao, mock_asset_balance_dao,
                                                mock_user_dao, mock_asset_dao):
        """Test that error logging is performed correctly in get_user_portfolio"""

        mock_balance_dao.get_balance.side_effect = CNOPDatabaseOperationException("DB error")

        with patch('src.controllers.portfolio.portfolio_controller.logger') as mock_logger:
            try:
                get_user_portfolio(
                    request=mock_request,
                    current_user=mock_current_user,
                    balance_dao=mock_balance_dao,
                    asset_balance_dao=mock_asset_balance_dao,
                    user_dao=mock_user_dao,
                    asset_dao=mock_asset_dao
                )
            except:
                pass

            # Verify error logging was called
            mock_logger.error.assert_called()

            # Check that the database error log was called
            error_calls = [call[1]["message"] for call in mock_logger.error.call_args_list]
            assert any("Database operation failed for portfolio" in call for call in error_calls)


    @patch('src.controllers.portfolio.portfolio_controller.validate_user_permissions')
    def test_get_user_portfolio_with_single_asset(self, mock_validate_user_permissions, mock_request, mock_current_user,
                                                    mock_balance_dao, mock_asset_balance_dao,
                                                    mock_user_dao, mock_asset_dao):
        """Test get_user_portfolio with single asset (100% allocation)"""
        # Mock single asset balance
        mock_single_balance = Mock()
        mock_single_balance.asset_id = "BTC"
        mock_single_balance.quantity = Decimal("1.0")

        mock_asset_balance_dao.get_all_asset_balances.return_value = [mock_single_balance]

        # Mock zero USD balance to make asset 100% of portfolio
        mock_balance_dao.get_balance.return_value = None

        result = get_user_portfolio(
            request=mock_request,
            current_user=mock_current_user,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True

        portfolio_data = result.data
        assets = portfolio_data["assets"]
        assert len(assets) == 1

        btc_asset = assets[0]
        assert btc_asset.asset_id == "BTC"
        assert btc_asset.market_value == Decimal("45000.00")
        assert btc_asset.percentage == Decimal("100")  # 100% allocation
        assert portfolio_data["total_portfolio_value"] == Decimal("45000.00")
