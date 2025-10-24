"""
User Service Dependencies

This module provides dependency injection functions for the User Service,
including a simplified transaction manager that only uses available DAOs.
"""
from common.data.database.dependencies import get_user_dao, get_balance_dao, get_asset_dao, get_asset_balance_dao
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.core.utils import TransactionManager
from common.shared.logging import BaseLogger, LoggerName
# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)


def get_transaction_manager() -> TransactionManager:
    """
    Get TransactionManager instance with User Service available DAOs

    User Service only has access to user_dao and balance_dao,
    so we create a simplified TransactionManager for balance operations.
    """
    return TransactionManager(
        user_dao=get_user_dao(),
        balance_dao=get_balance_dao(),
        order_dao=None,  # Not available in User Service
        asset_dao=get_asset_dao(),  # Available for portfolio operations
        asset_balance_dao=get_asset_balance_dao(),  # Available for portfolio operations
        asset_transaction_dao=None  # Not available in User Service
    )


def get_balance_dao_dependency() -> BalanceDAO:
    """Get BalanceDAO instance for balance operations"""
    return get_balance_dao()


def get_asset_balance_dao_dependency() -> AssetBalanceDAO:
    """Get AssetBalanceDAO instance for asset balance operations"""
    return get_asset_balance_dao()


def get_user_dao_dependency() -> UserDAO:
    """Get UserDAO instance for user operations"""
    return get_user_dao()


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance for asset operations"""
    return get_asset_dao()
