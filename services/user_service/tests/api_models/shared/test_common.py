"""
Tests for shared common API models - Focus on field validation
"""
import pytest
from pydantic import ValidationError
from api_models.shared.common import UserBaseInfo
from datetime import datetime, date

# Test constants
TEST_USERNAME = "john_doe123"
TEST_EMAIL = "john.doe@example.com"
TEST_FIRST_NAME = "John"
TEST_LAST_NAME = "Doe"
TEST_MARKETING_CONSENT = False
TEST_CREATED_AT = datetime(2025, 7, 9, 10, 30, 0)
TEST_UPDATED_AT = datetime(2025, 7, 9, 10, 30, 0)


def test_user_base_info_valid():
    """Test valid UserBaseInfo creation"""
    user_info = UserBaseInfo(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    assert user_info.username == TEST_USERNAME
    assert user_info.email == TEST_EMAIL
    assert user_info.first_name == TEST_FIRST_NAME
    assert user_info.last_name == TEST_LAST_NAME
    assert user_info.marketing_emails_consent == TEST_MARKETING_CONSENT


def test_user_base_info_missing_required_fields():
    """Test UserBaseInfo with missing required fields"""
    with pytest.raises(ValidationError):
        UserBaseInfo()  # Missing all required fields

    with pytest.raises(ValidationError):
        UserBaseInfo(username=TEST_USERNAME)  # Missing email and other required fields


def test_user_base_info_invalid_email():
    """Test UserBaseInfo with invalid email format"""
    # UserBaseInfo uses str field, not EmailStr, so it won't validate email format
    # This test verifies that invalid email strings are accepted (no validation)
    user_info = UserBaseInfo(
        username=TEST_USERNAME,
        email="invalid-email",  # Invalid email format but accepted as str
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    assert user_info.email == "invalid-email"


def test_user_base_info_username_validation():
    """Test UserBaseInfo username field validation"""
    # UserBaseInfo uses str field, so it accepts any string
    # This test verifies that any username string is accepted (no validation)
    user_info = UserBaseInfo(
        username="abc",  # Short username but accepted as str
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    assert user_info.username == "abc"

    # Long username also accepted
    user_info = UserBaseInfo(
        username="a"*31,  # Long username but accepted as str
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    assert user_info.username == "a"*31