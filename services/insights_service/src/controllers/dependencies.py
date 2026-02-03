"""
Dependencies for Insights Service Controllers
"""
from functools import lru_cache

from common.data.dao.user.user_dao import UserDAO
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.order.order_dao import OrderDAO
from common.data.database.dependencies import (
    get_user_dao,
    get_balance_dao,
    get_asset_balance_dao,
    get_asset_dao,
    get_order_dao
)

from services.data_aggregator import DataAggregator
from services.llm_service import LLMService


@lru_cache()
def get_data_aggregator() -> DataAggregator:
    """Get DataAggregator instance"""
    return DataAggregator(
        user_dao=get_user_dao(),
        balance_dao=get_balance_dao(),
        asset_balance_dao=get_asset_balance_dao(),
        asset_dao=get_asset_dao(),
        order_dao=get_order_dao()
    )


@lru_cache()
def get_llm_service() -> LLMService:
    """Get LLMService instance"""
    try:
        return LLMService()
    except ValueError as e:
        # API key not configured - service will return 503
        return None
