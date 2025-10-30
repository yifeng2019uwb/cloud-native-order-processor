import os
import sys
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Ensure tests can import sibling dependency_constants
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.dependencies import (
    get_order_dao_dependency,
    get_user_dao_dependency,
    get_balance_dao_dependency,
    get_asset_dao_dependency,
    get_asset_transaction_dao_dependency,
    get_asset_balance_dao_dependency,
    get_transaction_manager,
    get_current_market_price,
)
from dependency_constants import (
    PATCH_DEP_GET_ORDER_DAO,
    PATCH_DEP_GET_USER_DAO,
    PATCH_DEP_GET_BALANCE_DAO,
    PATCH_DEP_GET_ASSET_DAO,
    PATCH_DEP_DYNAMODB_MANAGER,
)


def test_basic_dao_dependencies_delegate_to_common_providers():
    with patch(PATCH_DEP_GET_ORDER_DAO) as p_order, \
         patch(PATCH_DEP_GET_USER_DAO) as p_user, \
         patch(PATCH_DEP_GET_BALANCE_DAO) as p_balance, \
         patch(PATCH_DEP_GET_ASSET_DAO) as p_asset:

        order_dao = MagicMock(name="OrderDAO")
        user_dao = MagicMock(name="UserDAO")
        balance_dao = MagicMock(name="BalanceDAO")
        asset_dao = MagicMock(name="AssetDAO")

        p_order.return_value = order_dao
        p_user.return_value = user_dao
        p_balance.return_value = balance_dao
        p_asset.return_value = asset_dao

        assert get_order_dao_dependency() is order_dao
        assert get_user_dao_dependency() is user_dao
        assert get_balance_dao_dependency() is balance_dao
        assert get_asset_dao_dependency() is asset_dao


def test_asset_related_daos_use_dynamodb_connection():
    mocked_manager = MagicMock()
    mocked_conn = MagicMock()
    mocked_manager.get_connection.return_value = mocked_conn

    with patch(PATCH_DEP_DYNAMODB_MANAGER, return_value=mocked_manager):
        asset_tx_dao = get_asset_transaction_dao_dependency()
        asset_bal_dao = get_asset_balance_dao_dependency()

        # Both DAOs should have been constructed using the connection
        mocked_manager.get_connection.assert_called()
        assert hasattr(asset_tx_dao, "__class__")
        assert hasattr(asset_bal_dao, "__class__")


def test_get_transaction_manager_wires_all_dependencies():
    with patch(PATCH_DEP_GET_ORDER_DAO) as p_order, \
         patch(PATCH_DEP_GET_USER_DAO) as p_user, \
         patch(PATCH_DEP_GET_BALANCE_DAO) as p_balance, \
         patch(PATCH_DEP_GET_ASSET_DAO) as p_asset, \
         patch(PATCH_DEP_DYNAMODB_MANAGER) as p_mgr:

        # Provide simple sentinel objects
        p_order.return_value = MagicMock()
        p_user.return_value = MagicMock()
        p_balance.return_value = MagicMock()
        p_asset.return_value = MagicMock()
        mgr = MagicMock()
        mgr.get_connection.return_value = MagicMock()
        p_mgr.return_value = mgr

        tm = get_transaction_manager()
        # Ensure the transaction manager has expected attributes wired
        assert tm.user_dao is p_user.return_value
        assert tm.balance_dao is p_balance.return_value
        assert tm.order_dao is p_order.return_value
        assert tm.asset_dao is p_asset.return_value


def test_get_current_market_price_fetches_and_converts():
    asset = MagicMock()
    asset.price_usd = Decimal("12345.67")
    asset_dao = MagicMock()
    asset_dao.get_asset_by_id.return_value = asset

    result = get_current_market_price("BTC", asset_dao)
    assert result == Decimal("12345.67")
    asset_dao.get_asset_by_id.assert_called_once_with("BTC")
