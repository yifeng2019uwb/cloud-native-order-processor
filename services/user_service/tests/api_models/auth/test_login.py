"""
Tests for login API models - Focus on field validation
"""
import pytest
from pydantic import ValidationError
from api_models.auth.login import UserLoginRequest, LoginResponse

# Test constants
TEST_USERNAME = "john_doe123"
TEST_PASSWORD = "SecurePassword123!"
TEST_ACCESS_TOKEN = "token123"
TEST_TOKEN_TYPE = "bearer"
TEST_EXPIRES_IN = 3600


def test_user_login_request_valid():
    """Test valid UserLoginRequest passes validation"""
    request = UserLoginRequest(username=TEST_USERNAME, password=TEST_PASSWORD)
    assert request.username == TEST_USERNAME
    assert request.password == TEST_PASSWORD


def test_user_login_request_username_validation():
    """Test username field validation"""
    # Too short
    with pytest.raises(ValidationError):
        UserLoginRequest(username="abc", password=TEST_PASSWORD)

    # Too long
    with pytest.raises(ValidationError):
        UserLoginRequest(username="a"*31, password=TEST_PASSWORD)


def test_user_login_request_password_validation():
    """Test password field validation"""
    # Too short
    with pytest.raises(ValidationError):
        UserLoginRequest(username=TEST_USERNAME, password="short")

    # Too long
    with pytest.raises(ValidationError):
        UserLoginRequest(username=TEST_USERNAME, password="a"*21)


def test_user_login_request_missing_fields():
    """Test missing required fields validation"""
    with pytest.raises(ValidationError):
        UserLoginRequest()  # Missing both username and password

    with pytest.raises(ValidationError):
        UserLoginRequest(username=TEST_USERNAME)  # Missing password

    with pytest.raises(ValidationError):
        UserLoginRequest(password=TEST_PASSWORD)  # Missing username


def test_login_response_valid():
    """Test valid LoginResponse creation"""
    response = LoginResponse(
        access_token=TEST_ACCESS_TOKEN,
        token_type=TEST_TOKEN_TYPE,
        expires_in=TEST_EXPIRES_IN
    )
    assert response.access_token == TEST_ACCESS_TOKEN
    assert response.token_type == TEST_TOKEN_TYPE
    assert response.expires_in == TEST_EXPIRES_IN