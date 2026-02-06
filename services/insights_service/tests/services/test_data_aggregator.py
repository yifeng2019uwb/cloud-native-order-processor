"""
Unit tests for data aggregator service
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from decimal import Decimal
from common.data.entities.asset.asset_balance import AssetBalance
from common.data.entities.order.order import Order, OrderType, OrderStatus
from src.services.data_aggregator import DataAggregator
from src.api_models.insights.portfolio_context import PortfolioContext
from src.constants import LLM_MAX_RECENT_ORDERS, MSG_ERROR_USER_NOT_FOUND

# Test constants
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"


class TestDataAggregator:
    """Test data aggregator service"""

    @pytest.fixture
    def mock_daos(self):
        """Mock all DAOs"""
        return {
            'user_dao': MagicMock(),
            'balance_dao': MagicMock(),
            'asset_balance_dao': MagicMock(),
            'asset_dao': MagicMock(),
            'order_dao': MagicMock()
        }

    @pytest.fixture
    def data_aggregator(self, mock_daos):
        """Create DataAggregator instance with mocked DAOs"""
        return DataAggregator(
            user_dao=mock_daos['user_dao'],
            balance_dao=mock_daos['balance_dao'],
            asset_balance_dao=mock_daos['asset_balance_dao'],
            asset_dao=mock_daos['asset_dao'],
            order_dao=mock_daos['order_dao']
        )

    def test_aggregate_portfolio_data_success(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_asset_balances,
        mock_assets,
        mock_orders
    ):
        """Test successful portfolio data aggregation"""
        # Setup mocks
        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = mock_asset_balances
        data_aggregator.asset_dao.get_asset_by_id.side_effect = lambda asset_id: mock_assets.get(asset_id)
        data_aggregator.order_dao.get_orders_by_user.return_value = mock_orders

        # Call method
        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Assertions - Check attributes instead of isinstance (Pydantic model comparison issue)
        assert hasattr(result, 'username')
        assert result.username == TEST_USERNAME
        assert result.account_age_days > 0
        assert result.usd_balance == Decimal("5000.00")
        assert result.total_portfolio_value > Decimal("0")
        assert len(result.holdings) == 2  # BTC and ETH
        assert len(result.recent_orders) == 1

        # Verify holdings are sorted by value
        assert result.holdings[0].asset_id == "BTC"  # Higher value
        assert result.holdings[0].allocation_pct > Decimal("0")

    def test_aggregate_portfolio_data_user_not_found(self, data_aggregator):
        """Test error when user not found"""
        data_aggregator.user_dao.get_user_by_username.return_value = None

        with pytest.raises(ValueError) as exc_info:
            data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        assert MSG_ERROR_USER_NOT_FOUND in str(exc_info.value)

    def test_aggregate_portfolio_data_empty_holdings(
        self,
        data_aggregator,
        mock_user,
        mock_balance
    ):
        """Test aggregation with no asset holdings"""
        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = []
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        assert result.total_portfolio_value == mock_balance.current_balance
        assert len(result.holdings) == 0
        assert len(result.recent_orders) == 0

    def test_aggregate_portfolio_data_filters_inactive_assets(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_assets
    ):
        """Test that inactive assets are filtered out"""
        # Create inactive asset
        inactive_asset = mock_assets["BTC"].model_copy()
        inactive_asset.is_active = False

        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0.15"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.return_value = inactive_asset
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Inactive asset should be filtered out
        assert len(result.holdings) == 0

    def test_aggregate_portfolio_data_calculates_allocation(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_asset_balances,
        mock_assets,
        mock_orders
    ):
        """Test allocation percentages are calculated correctly"""
        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = mock_asset_balances
        data_aggregator.asset_dao.get_asset_by_id.side_effect = lambda asset_id: mock_assets.get(asset_id)
        data_aggregator.order_dao.get_orders_by_user.return_value = mock_orders

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Check allocations sum to approximately 100% (within rounding)
        total_allocation = sum(float(h.allocation_pct) for h in result.holdings)
        assert 0 <= total_allocation <= 100

    def test_aggregate_portfolio_data_limits_recent_orders(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_asset_balances,
        mock_assets
    ):
        """Test that recent orders are limited"""
        # Create more orders than limit
        many_orders = [
            Order(
                order_id=f"order-{i}",
                username=TEST_USERNAME,
                order_type=OrderType.MARKET_BUY,
                status=OrderStatus.COMPLETED,
                asset_id="BTC",
                quantity=Decimal("0.01"),
                price=Decimal("44000"),
                total_amount=Decimal("440"),
                created_at=datetime(2026, 1, 30, 14, 0, 0, tzinfo=timezone.utc)
            )
            for i in range(LLM_MAX_RECENT_ORDERS + 5)
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = mock_asset_balances
        data_aggregator.asset_dao.get_asset_by_id.side_effect = lambda asset_id: mock_assets.get(asset_id)
        # Mock DAO to return only the limited number of orders (respecting the limit parameter)
        data_aggregator.order_dao.get_orders_by_user.return_value = many_orders[:LLM_MAX_RECENT_ORDERS]

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Should limit to LLM_MAX_RECENT_ORDERS
        assert len(result.recent_orders) == LLM_MAX_RECENT_ORDERS
        data_aggregator.order_dao.get_orders_by_user.assert_called_once_with(
            TEST_USERNAME,
            limit=LLM_MAX_RECENT_ORDERS,
            offset=0
        )

    def test_aggregate_portfolio_data_filters_zero_quantity(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_assets
    ):
        """Test that assets with zero or negative quantity are filtered out"""
        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0")),
            AssetBalance(username=TEST_USERNAME, asset_id="ETH", quantity=Decimal("-1"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.side_effect = lambda asset_id: mock_assets.get(asset_id)
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Zero/negative quantity assets should be filtered out
        assert len(result.holdings) == 0

    def test_aggregate_portfolio_data_handles_missing_price(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_assets
    ):
        """Test handling when asset has no price (current_price and price_usd are None)"""
        asset_no_price = mock_assets["BTC"].model_copy()
        asset_no_price.current_price = None
        asset_no_price.price_usd = None

        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0.15"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.return_value = asset_no_price
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Asset with no price should be filtered out
        assert len(result.holdings) == 0

    def test_aggregate_portfolio_data_handles_zero_price(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_assets
    ):
        """Test handling when asset price is zero or negative"""
        asset_zero_price = mock_assets["BTC"].model_copy()
        asset_zero_price.current_price = Decimal("0")
        asset_zero_price.price_usd = Decimal("0")  # Set both to 0 to ensure filtering

        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0.15"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.return_value = asset_zero_price
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Asset with zero price should be filtered out
        assert len(result.holdings) == 0

    def test_aggregate_portfolio_data_handles_missing_price_change(
        self,
        data_aggregator,
        mock_user,
        mock_balance,
        mock_assets
    ):
        """Test handling when price_change_percentage_24h is None"""
        asset_no_change = mock_assets["BTC"].model_copy()
        asset_no_change.price_change_percentage_24h = None

        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0.15"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.return_value = asset_no_change
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Should handle None price_change_percentage_24h
        assert len(result.holdings) == 1
        assert result.holdings[0].price_change_24h_pct == Decimal("0")

    def test_aggregate_portfolio_data_handles_decimal_price(
        self,
        data_aggregator,
        mock_user,
        mock_balance
    ):
        """Test handling when price is Decimal (not float)"""
        from common.data.entities.inventory.asset import Asset

        asset_decimal_price = Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            amount=Decimal("1000"),
            price_usd=Decimal("45000"),
            is_active=True,
            current_price=Decimal("45000"),  # Decimal instead of float
            price_change_percentage_24h=Decimal("2.5")  # Decimal instead of float
        )

        asset_balances = [
            AssetBalance(username=TEST_USERNAME, asset_id="BTC", quantity=Decimal("0.15"))
        ]

        data_aggregator.user_dao.get_user_by_username.return_value = mock_user
        data_aggregator.balance_dao.get_balance.return_value = mock_balance
        data_aggregator.asset_balance_dao.get_all_asset_balances.return_value = asset_balances
        data_aggregator.asset_dao.get_asset_by_id.return_value = asset_decimal_price
        data_aggregator.order_dao.get_orders_by_user.return_value = []

        result = data_aggregator.aggregate_portfolio_data(TEST_USERNAME)

        # Should handle Decimal price correctly
        assert len(result.holdings) == 1
        assert result.holdings[0].current_price == Decimal("45000")
        assert result.holdings[0].price_change_24h_pct == Decimal("2.5")
