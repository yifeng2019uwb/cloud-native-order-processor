"""
Data Aggregator Service - Fetches and aggregates data from DAOs
"""
from datetime import datetime, timezone
from decimal import Decimal

from common.data.dao.user.user_dao import UserDAO
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.order.order_dao import OrderDAO
from common.shared.logging import BaseLogger, LoggerName, LogAction
from api_models.insights.portfolio_context import PortfolioContext, HoldingData, OrderData
from constants import LLM_MAX_RECENT_ORDERS, LLM_MAX_HOLDINGS_FETCH, MSG_ERROR_USER_NOT_FOUND

logger = BaseLogger(LoggerName.INSIGHTS)


class DataAggregator:
    """Aggregates portfolio data from multiple DAOs"""

    def __init__(
        self,
        user_dao: UserDAO,
        balance_dao: BalanceDAO,
        asset_balance_dao: AssetBalanceDAO,
        asset_dao: AssetDAO,
        order_dao: OrderDAO
    ):
        self.user_dao = user_dao
        self.balance_dao = balance_dao
        self.asset_balance_dao = asset_balance_dao
        self.asset_dao = asset_dao
        self.order_dao = order_dao

    def aggregate_portfolio_data(self, username: str) -> PortfolioContext:
        """
        Aggregate portfolio data for a user

        Args:
            username: Username to aggregate data for

        Returns:
            PortfolioContext: Aggregated portfolio context
        """
        # Get user
        user = self.user_dao.get_user_by_username(username)
        if not user:
            raise ValueError(f"{MSG_ERROR_USER_NOT_FOUND}: {username}")

        # Calculate account age
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days

        # Get USD balance
        balance = self.balance_dao.get_balance(username)
        usd_balance = balance.current_balance if balance else Decimal('0.00')

        # Get asset holdings
        asset_balances = self.asset_balance_dao.get_all_asset_balances(username)

        # Get current prices and calculate holdings with market data
        holdings = []
        total_portfolio_value = usd_balance

        for asset_balance in asset_balances:
            if asset_balance.quantity <= 0:
                continue

            # Get asset price data
            asset = self.asset_dao.get_asset_by_id(asset_balance.asset_id)
            if not asset or not asset.is_active:
                continue

            # Get price - convert to Decimal if needed
            price_value = asset.current_price or asset.price_usd
            if price_value is None:
                current_price = Decimal('0')
            elif isinstance(price_value, float):
                current_price = Decimal(str(price_value))
            else:
                current_price = Decimal(str(price_value))

            if current_price <= 0:
                continue

            # Calculate values
            value_usd = asset_balance.quantity * current_price
            total_portfolio_value += value_usd

            # Convert price_change_percentage_24h to Decimal
            price_change_pct = asset.price_change_percentage_24h
            if price_change_pct is None:
                price_change_pct = Decimal('0')
            elif isinstance(price_change_pct, float):
                price_change_pct = Decimal(str(price_change_pct))
            else:
                price_change_pct = Decimal(str(price_change_pct))

            holdings.append(HoldingData(
                asset_id=asset_balance.asset_id,
                quantity=asset_balance.quantity,
                current_price=current_price,
                price_change_24h_pct=price_change_pct,
                value_usd=value_usd,
                allocation_pct=Decimal('0')  # Will calculate after total is known
            ))

        # Calculate allocation percentages
        if total_portfolio_value > 0:
            for holding in holdings:
                holding.allocation_pct = (holding.value_usd / total_portfolio_value) * Decimal('100')

        # Sort by value descending
        holdings.sort(key=lambda x: x.value_usd, reverse=True)
        
        # Limit holdings to top N by value to reduce prompt size for accounts with many assets
        holdings = holdings[:LLM_MAX_HOLDINGS_FETCH]

        # Get recent orders (limited to reduce prompt size)
        orders = self.order_dao.get_orders_by_user(username, limit=LLM_MAX_RECENT_ORDERS, offset=0)
        recent_orders = []
        for order in orders:
            recent_orders.append(OrderData(
                order_type=order.order_type.value,
                asset_id=order.asset_id,
                quantity=order.quantity,
                price=order.price if order.price else Decimal('0'),
                created_at=order.created_at if order.created_at else datetime.now(timezone.utc)
            ))

        return PortfolioContext(
            username=username,
            account_age_days=account_age_days,
            usd_balance=usd_balance,
            total_portfolio_value=total_portfolio_value,
            holdings=holdings,
            recent_orders=recent_orders
        )
