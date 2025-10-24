"""
Dependencies for Order Service controllers
Path: services/order_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- Gateway Authentication
- Authorization
"""
from decimal import Decimal
from common.data.database.dependencies import get_order_dao, get_balance_dao, get_asset_dao, get_user_dao
from common.data.database.dynamodb_connection import get_dynamodb_manager
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.asset.asset_transaction_dao import AssetTransactionDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.core.utils.transaction_manager import TransactionManager
from common.shared.logging import BaseLogger, LoggerName
from common.data.entities.user import User
from common.auth.security.auth_dependencies import AuthenticatedUser, get_current_user
from common.auth.gateway.header_validator import get_request_id_from_request
from order_exceptions.exceptions import CNOPOrderValidationException

# Initialize our standardized logger
logger = BaseLogger(LoggerName.ORDER)


def get_order_dao_dependency() -> OrderDAO:
    """Get OrderDAO instance"""
    return get_order_dao()


def get_user_dao_dependency() -> UserDAO:
    """Get UserDAO instance for user operations"""
    return get_user_dao()


def get_balance_dao_dependency() -> BalanceDAO:
    """Get BalanceDAO instance for USD balance operations"""
    return get_balance_dao()


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance for asset validation"""
    return get_asset_dao()


def get_asset_transaction_dao_dependency() -> AssetTransactionDAO:
    """Get AssetTransactionDAO instance for asset transaction operations"""
    return AssetTransactionDAO(get_dynamodb_manager().get_connection())


def get_asset_balance_dao_dependency() -> AssetBalanceDAO:
    """Get AssetBalanceDAO instance for asset balance operations"""
    return AssetBalanceDAO(get_dynamodb_manager().get_connection())


def get_transaction_manager() -> TransactionManager:
    """
    Get TransactionManager instance with all required DAOs for atomic operations

    Returns:
        TransactionManager: Configured with all required DAOs for order and balance operations
    """
    return TransactionManager(
        user_dao=get_user_dao_dependency(),
        balance_dao=get_balance_dao_dependency(),
        order_dao=get_order_dao_dependency(),
        asset_dao=get_asset_dao_dependency(),
        asset_balance_dao=get_asset_balance_dao_dependency(),
        asset_transaction_dao=get_asset_transaction_dao_dependency()
    )


def get_current_market_price(asset_id: str, asset_dao: AssetDAO) -> Decimal:
    """
    Get current market price for an asset using AssetDAO

    Args:
        asset_id: Asset ID (e.g., 'BTC', 'ETH', 'XRP')
        asset_dao: Asset DAO instance

    Returns:
        Current market price as Decimal
    """
    asset = asset_dao.get_asset_by_id(asset_id)
    return Decimal(str(asset.price_usd))
