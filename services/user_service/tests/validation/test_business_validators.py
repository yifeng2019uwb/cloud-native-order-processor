import pytest
from unittest.mock import MagicMock

from validation.business_validators import (
    validate_user_permissions,
    validate_email_uniqueness,
)
from common.exceptions.shared_exceptions import CNOPUserNotFoundException
from user_exceptions import CNOPUserValidationException


TEST_USERNAME = "alice"
TEST_EMAIL = "alice@example.com"


def test_validate_user_permissions_user_not_found_raises_validation():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.return_value = None

    with pytest.raises(CNOPUserValidationException):
        validate_user_permissions(TEST_USERNAME, "any", mock_user_dao)


def test_validate_user_permissions_unexpected_exception_wrapped():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.side_effect = RuntimeError("db down")

    with pytest.raises(CNOPUserValidationException) as exc:
        validate_user_permissions(TEST_USERNAME, "any", mock_user_dao)
    assert "Permission validation failed" in str(exc.value)


def test_validate_email_uniqueness_exclude_same_username_returns_true():
    mock_user_dao = MagicMock()
    existing_user = MagicMock()
    existing_user.username = TEST_USERNAME
    mock_user_dao.get_user_by_email.return_value = existing_user

    result = validate_email_uniqueness(TEST_EMAIL, mock_user_dao, exclude_username=TEST_USERNAME)
    assert result is True
