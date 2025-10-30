import pytest
from unittest.mock import patch, MagicMock

from controllers.portfolio.asset_balance_controller import get_user_asset_balance
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException
from user_exceptions import CNOPUserValidationException
from ...dependency_constants import PATCH_VALIDATE_USER_PERMISSIONS


TEST_USERNAME = "alice"
TEST_ASSET_ID = "BTC"
TEST_ASSET_NAME = "Bitcoin"
TEST_CURRENT_PRICE = 30000
TEST_QTY_SMALL = 2
TEST_QTY_LARGE = 5
EXPECTED_STATUS_NOT_FOUND = 404
EXPECTED_STATUS_FORBIDDEN = 403
ZERO_PRICE = 0.0


def create_user(username: str = TEST_USERNAME) -> User:
    return User(
        username=username,
        email=f"{username}@example.com",
        first_name="Alice",
        last_name="Doe",
        password="p",
        role="user",
        marketing_emails_consent=True,
    )


def test_get_user_asset_balance_success():
    current_user = create_user()
    # DAOs
    mock_user_dao = MagicMock()
    mock_balance_dao = MagicMock()
    mock_asset_balance_dao = MagicMock()
    mock_asset_dao = MagicMock()

    # Balance object
    balance = MagicMock()
    balance.asset_id = TEST_ASSET_ID
    balance.quantity = TEST_QTY_SMALL
    balance.created_at = "2024-01-01T00:00:00Z"
    balance.updated_at = "2024-01-02T00:00:00Z"
    mock_asset_balance_dao.get_asset_balance.return_value = balance

    # Asset price
    asset = MagicMock()
    asset.name = TEST_ASSET_NAME
    asset.current_price = TEST_CURRENT_PRICE
    mock_asset_dao.get_asset_by_id.return_value = asset

    with patch(PATCH_VALIDATE_USER_PERMISSIONS) as mock_validate:
        result = get_user_asset_balance(
            current_user=current_user,
            user_dao=mock_user_dao,
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            asset_dao=mock_asset_dao,
            asset_id=TEST_ASSET_ID,
        )

        assert result.asset_id == TEST_ASSET_ID
        assert result.asset_name == TEST_ASSET_NAME
        assert result.current_price == float(TEST_CURRENT_PRICE)
        assert result.total_value == float(TEST_QTY_SMALL) * float(TEST_CURRENT_PRICE)
        mock_validate.assert_called_once()


def test_get_user_asset_balance_not_found_returns_404():
    current_user = create_user()
    mock_user_dao = MagicMock()
    mock_balance_dao = MagicMock()
    mock_asset_balance_dao = MagicMock()
    mock_asset_dao = MagicMock()

    mock_asset_balance_dao.get_asset_balance.return_value = None

    with patch(PATCH_VALIDATE_USER_PERMISSIONS):
        with pytest.raises(Exception) as exc:
            get_user_asset_balance(
                current_user=current_user,
                user_dao=mock_user_dao,
                balance_dao=mock_balance_dao,
                asset_balance_dao=mock_asset_balance_dao,
                asset_dao=mock_asset_dao,
                asset_id=TEST_ASSET_ID,
            )
        assert getattr(exc.value, "status_code", 0) == EXPECTED_STATUS_NOT_FOUND


def test_get_user_asset_balance_price_lookup_failure_uses_zero():
    current_user = create_user()
    mock_user_dao = MagicMock()
    mock_balance_dao = MagicMock()
    mock_asset_balance_dao = MagicMock()
    mock_asset_dao = MagicMock()

    balance = MagicMock()
    balance.asset_id = TEST_ASSET_ID
    balance.quantity = TEST_QTY_LARGE
    balance.created_at = "2024-01-01T00:00:00Z"
    balance.updated_at = "2024-01-02T00:00:00Z"
    mock_asset_balance_dao.get_asset_balance.return_value = balance

    mock_asset_dao.get_asset_by_id.side_effect = RuntimeError("coingecko down")

    with patch(PATCH_VALIDATE_USER_PERMISSIONS):
        result = get_user_asset_balance(
            current_user=current_user,
            user_dao=MagicMock(),
            balance_dao=mock_balance_dao,
            asset_balance_dao=mock_asset_balance_dao,
            asset_dao=mock_asset_dao,
            asset_id=TEST_ASSET_ID,
        )
        assert result.current_price == ZERO_PRICE
        assert result.total_value == ZERO_PRICE


def test_get_user_asset_balance_permission_denied_returns_403():
    current_user = create_user()
    mock_asset_balance_dao = MagicMock()

    with patch(PATCH_VALIDATE_USER_PERMISSIONS, side_effect=CNOPUserValidationException("denied")):
        with pytest.raises(Exception) as exc:
            get_user_asset_balance(
                current_user=current_user,
                user_dao=MagicMock(),
                balance_dao=MagicMock(),
                asset_balance_dao=mock_asset_balance_dao,
                asset_dao=MagicMock(),
                asset_id=TEST_ASSET_ID,
            )
        assert getattr(exc.value, "status_code", 0) == EXPECTED_STATUS_FORBIDDEN


def test_get_user_asset_balance_dao_raises_specific_not_found_maps_404():
    current_user = create_user()
    mock_asset_balance_dao = MagicMock()
    mock_asset_balance_dao.get_asset_balance.side_effect = CNOPAssetBalanceNotFoundException("nope")

    with patch(PATCH_VALIDATE_USER_PERMISSIONS):
        with pytest.raises(Exception) as exc:
            get_user_asset_balance(
                current_user=current_user,
                user_dao=MagicMock(),
                balance_dao=MagicMock(),
                asset_balance_dao=mock_asset_balance_dao,
                asset_dao=MagicMock(),
                asset_id=TEST_ASSET_ID,
            )
        assert getattr(exc.value, "status_code", 0) == EXPECTED_STATUS_NOT_FOUND
