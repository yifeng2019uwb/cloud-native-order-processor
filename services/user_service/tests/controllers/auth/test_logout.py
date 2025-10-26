"""
Tests for logout controller - Focus on business logic
"""
import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from controllers.auth.logout import logout_user
from api_models.auth.logout import LogoutRequest, LogoutResponse

TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"

def test_logout_success():
    """Test successful logout"""
    # Mock user data
    mock_user = MagicMock()
    mock_user.email = TEST_EMAIL
    mock_user.username = TEST_USERNAME

    # Mock logout data (empty request for JWT stateless approach)
    logout_data = LogoutRequest()

    # Call the function with current_user as a direct parameter (bypassing Depends)
    result = logout_user(logout_data, current_user=mock_user)

    # Verify result
    assert isinstance(result, LogoutResponse)
    assert result.message == "Logged out successfully"


def test_logout_with_different_users():
    """Test logout with different user scenarios"""
    # Test with different user
    mock_user = MagicMock()
    mock_user.email = "different@example.com"
    mock_user.username = "differentuser"

    logout_data = LogoutRequest()
    result = logout_user(logout_data, current_user=mock_user)

    assert isinstance(result, LogoutResponse)
    assert result.message == "Logged out successfully"
