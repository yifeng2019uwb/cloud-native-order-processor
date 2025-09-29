"""
Tests for asset_balance controller
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
    mock_request.headers = {"X-Request-ID": request_id}
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

ASSET_BALANCE_DAO_SPEC = [
    'get_asset_balance',
    'save_asset_balance',
    'update_asset_balance',
    'delete_asset_balance',
    'get_all_asset_balances'
]

# Mock dependencies before importing
with patch('src.controllers.asset_balance.get_current_user', create=True), \
     patch('src.controllers.asset_balance.get_asset_balance_dao_dependency', create=True), \
     patch('src.controllers.asset_balance.get_user_dao_dependency', create=True), \
     patch('src.controllers.asset_balance.get_asset_dao_dependency', create=True), \
     patch('src.controllers.asset_balance.validate_user_permissions', create=True), \
     patch('src.controllers.asset_balance.AssetBalanceDAO', create=True), \
     patch('src.controllers.asset_balance.UserDAO', create=True), \
     patch('src.controllers.asset_balance.AssetDAO', create=True), \
    patch('src.controllers.asset_balance.CNOPDatabaseOperationException', create=True), \
    patch('src.controllers.asset_balance.CNOPEntityNotFoundException', create=True), \
    patch('src.controllers.asset_balance.CNOPInternalServerException', create=True), \
    patch('src.controllers.asset_balance.CNOPAssetNotFoundException', create=True):

    from src.controllers.asset_balance import (
        get_real_market_data, get_user_asset_balances, get_user_asset_balance
    )


class TestAssetBalanceController:
    """Test asset balance controller functions"""

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
    def mock_asset_balance_dao(self):
        """Mock asset balance DAO"""
        dao = Mock(spec=ASSET_BALANCE_DAO_SPEC)

        # Mock asset balance object
        mock_balance = Mock()
        mock_balance.asset_id = "BTC"
        mock_balance.quantity = Decimal("1.5")
        mock_balance.created_at = datetime.now(timezone.utc)
        mock_balance.updated_at = datetime.now(timezone.utc)

        dao.get_all_asset_balances.return_value = [mock_balance]
        dao.get_asset_balance.return_value = mock_balance

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

        # Mock asset object
        mock_asset = Mock()
        mock_asset.name = "Bitcoin"
        mock_asset.price_usd = Decimal("45000.50")

        dao.get_asset_by_id.return_value = mock_asset

        return dao

    @pytest.fixture
    def mock_validate_user_permissions(self):
        """Mock user permissions validation"""
        with patch('src.controllers.asset_balance.validate_user_permissions') as mock:
            yield mock

    def test_get_real_market_data_success(self, mock_asset_dao):
        """Test get_real_market_data with successful asset retrieval"""
        result = get_real_market_data(mock_asset_dao, "BTC")

        assert result["asset_name"] == "Bitcoin"
        assert result["current_price"] == 45000.50
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

    def test_get_real_market_data_asset_not_found(self, mock_asset_dao):
        """Test get_real_market_data when asset is not found"""
        mock_asset_dao.get_asset_by_id.return_value = None

        result = get_real_market_data(mock_asset_dao, "INVALID")

        assert result["asset_name"] == "INVALID"
        assert result["current_price"] == 0.0
        mock_asset_dao.get_asset_by_id.assert_called_once_with("INVALID")

    def test_get_real_market_data_exception_fallback(self, mock_asset_dao):
        """Test get_real_market_data with exception fallback"""
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Database error")

        result = get_real_market_data(mock_asset_dao, "BTC")

        assert result["asset_name"] == "BTC"
        assert result["current_price"] == 0.0
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")


    def test_get_user_asset_balances_success(self, mock_request, mock_current_user,
                                                   mock_asset_balance_dao, mock_user_dao,
                                                   mock_asset_dao, mock_validate_user_permissions):
        """Test successful retrieval of all asset balances"""
        result = get_user_asset_balances(
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        # Verify validation was called
        mock_validate_user_permissions.assert_called_once_with(
            username="testuser",
            action="view_asset_balances",
            user_dao=mock_user_dao
        )

        # Verify DAO calls
        mock_asset_balance_dao.get_all_asset_balances.assert_called_once_with("testuser")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify response
        assert result.success is True
        assert result.message == "Asset balances retrieved successfully"
        assert len(result.data) == 1

        balance_data = result.data[0]
        assert balance_data.asset_id == "BTC"
        assert balance_data.asset_name == "Bitcoin"
        assert balance_data.quantity == Decimal("1.5")
        assert balance_data.current_price == 45000.50
        assert balance_data.total_value == 67500.75  # 1.5 * 45000.50


    def test_get_user_asset_balances_database_error(self, mock_request, mock_current_user,
                                                         mock_asset_balance_dao, mock_user_dao,
                                                         mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balances with database operation exception"""

        mock_asset_balance_dao.get_all_asset_balances.side_effect = CNOPDatabaseOperationException("DB error")

        with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
            get_user_asset_balances(
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    def test_get_user_asset_balances_unexpected_error(self, mock_request, mock_current_user,
                                                           mock_asset_balance_dao, mock_user_dao,
                                                           mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balances with unexpected exception"""
        mock_asset_balance_dao.get_all_asset_balances.side_effect = Exception("Unexpected error")

        with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
            get_user_asset_balances(
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    def test_get_user_asset_balance_success(self, mock_request, mock_current_user,
                                                 mock_asset_balance_dao, mock_user_dao,
                                                 mock_asset_dao, mock_validate_user_permissions):
        """Test successful retrieval of specific asset balance"""
        result = get_user_asset_balance(
            asset_id="BTC",
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        # Verify validation was called
        mock_validate_user_permissions.assert_called_once_with(
            username="testuser",
            action="view_asset_balance",
            user_dao=mock_user_dao
        )

        # Verify DAO calls
        mock_asset_balance_dao.get_asset_balance.assert_called_once_with("testuser", "BTC")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify response
        assert result.success is True
        assert result.message == "Asset balance retrieved successfully"
        assert result.data.asset_id == "BTC"
        assert result.data.asset_name == "Bitcoin"
        assert result.data.quantity == Decimal("1.5")
        assert result.data.current_price == 45000.50
        assert result.data.total_value == 67500.75


    def test_get_user_asset_balance_not_found(self, mock_request, mock_current_user,
                                                   mock_asset_balance_dao, mock_user_dao,
                                                   mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balance with entity not found exception"""

        mock_asset_balance_dao.get_asset_balance.side_effect = CNOPEntityNotFoundException("Not found")

        with pytest.raises(CNOPAssetNotFoundException, match="Asset balance for BTC not found"):
            get_user_asset_balance(
                asset_id="BTC",
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    def test_get_user_asset_balance_database_error(self, mock_request, mock_current_user,
                                                        mock_asset_balance_dao, mock_user_dao,
                                                        mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balance with database operation exception"""

        mock_asset_balance_dao.get_asset_balance.side_effect = CNOPDatabaseOperationException("DB error")

        with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
            get_user_asset_balance(
                asset_id="BTC",
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    def test_get_user_asset_balance_unexpected_error(self, mock_request, mock_current_user,
                                                          mock_asset_balance_dao, mock_user_dao,
                                                          mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balance with unexpected exception"""

        mock_asset_balance_dao.get_asset_balance.side_effect = Exception("Unexpected error")

        with pytest.raises(CNOPInternalServerException, match="Service temporarily unavailable"):
            get_user_asset_balance(
                asset_id="BTC",
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )


    def test_get_user_asset_balances_multiple_assets(self, mock_request, mock_current_user,
                                                          mock_asset_balance_dao, mock_user_dao,
                                                          mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balances with multiple assets"""
        # Create multiple mock balances
        mock_balance1 = Mock()
        mock_balance1.asset_id = "BTC"
        mock_balance1.quantity = Decimal("1.5")
        mock_balance1.created_at = datetime.now(timezone.utc)
        mock_balance1.updated_at = datetime.now(timezone.utc)

        mock_balance2 = Mock()
        mock_balance2.asset_id = "ETH"
        mock_balance2.quantity = Decimal("10.0")
        mock_balance2.created_at = datetime.now(timezone.utc)
        mock_balance2.updated_at = datetime.now(timezone.utc)

        mock_asset_balance_dao.get_all_asset_balances.return_value = [mock_balance1, mock_balance2]

        # Mock different asset data for ETH
        mock_eth_asset = Mock()
        mock_eth_asset.name = "Ethereum"
        mock_eth_asset.price_usd = Decimal("3000.00")

        mock_asset_dao.get_asset_by_id.side_effect = [
            mock_asset_dao.get_asset_by_id.return_value,  # BTC
            mock_eth_asset  # ETH
        ]

        result = get_user_asset_balances(
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert len(result.data) == 2

        # Check BTC data
        btc_data = result.data[0]
        assert btc_data.asset_id == "BTC"
        assert btc_data.asset_name == "Bitcoin"
        assert btc_data.total_value == 67500.75

        # Check ETH data
        eth_data = result.data[1]
        assert eth_data.asset_id == "ETH"
        assert eth_data.asset_name == "Ethereum"
        assert eth_data.total_value == 30000.00


    def test_get_user_asset_balances_empty_list(self, mock_request, mock_current_user,
                                                     mock_asset_balance_dao, mock_user_dao,
                                                     mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balances with no assets"""
        mock_asset_balance_dao.get_all_asset_balances.return_value = []

        result = get_user_asset_balances(
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.success is True
        assert len(result.data) == 0


    def test_get_user_asset_balance_with_zero_price(self, mock_request, mock_current_user,
                                                         mock_asset_balance_dao, mock_user_dao,
                                                         mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balance with asset having zero price"""
        # Mock asset with zero price
        mock_zero_price_asset = Mock()
        mock_zero_price_asset.name = "Zero Asset"
        mock_zero_price_asset.price_usd = Decimal("0.00")

        mock_asset_dao.get_asset_by_id.return_value = mock_zero_price_asset

        result = get_user_asset_balance(
            asset_id="ZERO",
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        assert result.data.current_price == 0.0
        assert result.data.total_value == 0.0


    def test_get_user_asset_balance_with_high_precision_quantity(self, mock_request, mock_current_user,
                                                                      mock_asset_balance_dao, mock_user_dao,
                                                                      mock_asset_dao, mock_validate_user_permissions):
        """Test get_user_asset_balance with high precision quantity"""
        # Mock balance with high precision quantity
        mock_precise_balance = Mock()
        mock_precise_balance.asset_id = "BTC"
        mock_precise_balance.quantity = Decimal("1.12345678")
        mock_precise_balance.created_at = datetime.now(timezone.utc)
        mock_precise_balance.updated_at = datetime.now(timezone.utc)

        mock_asset_balance_dao.get_asset_balance.return_value = mock_precise_balance

        result = get_user_asset_balance(
            asset_id="BTC",
            request=mock_request,
            current_user=mock_current_user,
            asset_balance_dao=mock_asset_balance_dao,
            user_dao=mock_user_dao,
            asset_dao=mock_asset_dao
        )

        expected_total = float(Decimal("1.12345678")) * 45000.50
        assert result.data.quantity == Decimal("1.12345678")
        assert result.data.total_value == expected_total

    def test_get_real_market_data_with_none_asset(self, mock_asset_dao):
        """Test get_real_market_data when asset is None"""
        mock_asset_dao.get_asset_by_id.return_value = None

        result = get_real_market_data(mock_asset_dao, "NONE")

        assert result["asset_name"] == "NONE"
        assert result["current_price"] == 0.0

    def test_get_real_market_data_with_missing_price(self, mock_asset_dao):
        """Test get_real_market_data when asset has no price"""
        mock_asset_no_price = Mock()
        mock_asset_no_price.name = "No Price Asset"
        mock_asset_no_price.price_usd = None

        mock_asset_dao.get_asset_by_id.return_value = mock_asset_no_price

        result = get_real_market_data(mock_asset_dao, "NOPRICE")

        # Should handle None price gracefully by falling back to asset_id
        assert result["asset_name"] == "NOPRICE"
        assert result["current_price"] == 0.0


    def test_get_user_asset_balances_logging(self, mock_request, mock_current_user,
                                                  mock_asset_balance_dao, mock_user_dao,
                                                  mock_asset_dao, mock_validate_user_permissions):
        """Test that logging is performed correctly in get_user_asset_balances"""
        with patch('src.controllers.asset_balance.logger') as mock_logger:
            get_user_asset_balances(
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )

            # Verify info logging was called
            mock_logger.info.assert_called()

            # Check that the success log was called
            success_calls = [call[1]["message"] for call in mock_logger.info.call_args_list]
            assert any("Asset balances retrieved successfully" in call for call in success_calls)


    def test_get_user_asset_balance_logging(self, mock_request, mock_current_user,
                                                 mock_asset_balance_dao, mock_user_dao,
                                                 mock_asset_dao, mock_validate_user_permissions):
        """Test that logging is performed correctly in get_user_asset_balance"""
        with patch('src.controllers.asset_balance.logger') as mock_logger:
            get_user_asset_balance(
                asset_id="BTC",
                request=mock_request,
                current_user=mock_current_user,
                asset_balance_dao=mock_asset_balance_dao,
                user_dao=mock_user_dao,
                asset_dao=mock_asset_dao
            )

            # Verify info logging was called
            mock_logger.info.assert_called()

            # Check that the success log was called
            success_calls = [call[1]["message"] for call in mock_logger.info.call_args_list]
            assert any("Asset balance retrieved successfully" in call for call in success_calls)


    def test_get_user_asset_balance_error_logging(self, mock_request, mock_current_user,
                                                       mock_asset_balance_dao, mock_user_dao,
                                                       mock_asset_dao, mock_validate_user_permissions):
        """Test that error logging is performed correctly in get_user_asset_balance"""

        mock_asset_balance_dao.get_asset_balance.side_effect = CNOPEntityNotFoundException("Not found")

        with patch('src.controllers.asset_balance.logger') as mock_logger:
            try:
                get_user_asset_balance(
                    asset_id="BTC",
                    request=mock_request,
                    current_user=mock_current_user,
                    asset_balance_dao=mock_asset_balance_dao,
                    user_dao=mock_user_dao,
                    asset_dao=mock_asset_dao
                )
            except:
                pass

            # Verify info logging was called for not found
            mock_logger.info.assert_called()

            # Check that the not found log was called
            info_calls = [call[1]["message"] for call in mock_logger.info.call_args_list]
            assert any("Asset balance not found" in call for call in info_calls)
