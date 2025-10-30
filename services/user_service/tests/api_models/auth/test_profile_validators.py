from datetime import date

from api_models.auth.profile import UserProfileUpdateRequest


def test_first_name_none_skips_validation():
    req = UserProfileUpdateRequest(first_name=None)
    assert req.first_name is None


def test_last_name_none_skips_validation():
    req = UserProfileUpdateRequest(last_name=None)
    assert req.last_name is None


def test_email_none_skips_validation():
    req = UserProfileUpdateRequest(email=None)
    assert req.email is None


def test_phone_none_skips_validation():
    req = UserProfileUpdateRequest(phone=None)
    assert req.phone is None


def test_dob_none_skips_validation():
    req = UserProfileUpdateRequest(date_of_birth=None)
    assert req.date_of_birth is None
