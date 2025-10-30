import pytest
from unittest.mock import patch, MagicMock

from controllers.auth.profile import get_profile, update_profile
from api_models.auth.profile import UserProfileUpdateRequest
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPEntityNotFoundException as CNOPUserNotFoundException
from fastapi import HTTPException

from ...dependency_constants import (
    PATCH_GET_REQUEST_ID,
    PATCH_VALIDATE_EMAIL_UNIQUENESS,
    PATCH_VALIDATE_AGE_REQUIREMENTS,
    PATCH_USER_PROFILE_RESPONSE,
)


TEST_REQUEST_ID = "test-request-id"
TEST_USERNAME = "jane"
TEST_EMAIL = "jane@example.com"


def create_mock_request():
    req = MagicMock()
    req.headers = {"X-Request-ID": TEST_REQUEST_ID}
    return req


def create_user(**overrides):
    base = dict(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password="p",
        first_name="Jane",
        last_name="Doe",
        phone="123",
        date_of_birth=None,
        marketing_emails_consent=True,
        role="user",
        created_at="2024-01-01T00:00:00+00:00",
        updated_at="2024-01-02T00:00:00+00:00",
    )
    base.update(overrides)
    return User(**base)


def test_get_profile_exception_wrapped_internal_error():
    current_user = create_user()
    with patch(PATCH_GET_REQUEST_ID, return_value=TEST_REQUEST_ID), \
         patch(PATCH_USER_PROFILE_RESPONSE, side_effect=RuntimeError("boom")):
        with pytest.raises(HTTPException) as exc:
            get_profile(create_mock_request(), current_user=current_user)
        assert exc.value.status_code == 500


def test_update_profile_not_found_raises_user_not_found():
    current_user = create_user()
    mock_user_dao = MagicMock()
    mock_user_dao.update_user.return_value = None

    with patch(PATCH_GET_REQUEST_ID, return_value=TEST_REQUEST_ID):
        with pytest.raises(CNOPUserNotFoundException):
            update_profile(UserProfileUpdateRequest(), create_mock_request(), current_user=current_user, user_dao=mock_user_dao)


def test_update_profile_general_exception_wrapped():
    current_user = create_user()
    mock_user_dao = MagicMock()
    mock_user_dao.update_user.side_effect = RuntimeError("db down")

    with patch(PATCH_GET_REQUEST_ID, return_value=TEST_REQUEST_ID):
        with pytest.raises(HTTPException) as exc:
            update_profile(UserProfileUpdateRequest(), create_mock_request(), current_user=current_user, user_dao=mock_user_dao)
        assert exc.value.status_code == 500


def test_update_profile_age_validation_called_when_dob_present():
    current_user = create_user()
    mock_user_dao = MagicMock()
    mock_user_dao.update_user.return_value = current_user

    profile_data = UserProfileUpdateRequest(date_of_birth="2000-01-01")

    with patch(PATCH_GET_REQUEST_ID, return_value=TEST_REQUEST_ID), \
         patch(PATCH_VALIDATE_AGE_REQUIREMENTS) as mock_age:
        _ = update_profile(profile_data, create_mock_request(), current_user=current_user, user_dao=mock_user_dao)
        assert mock_age.called
