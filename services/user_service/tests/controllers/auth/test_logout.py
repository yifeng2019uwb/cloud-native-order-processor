import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from controllers.auth.logout import logout_user, logout_debug
from api_models.auth.logout import LogoutRequest, LogoutSuccessResponse

def test_logout_success():
    # Mock user data
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"

    # Mock logout data (empty request for JWT stateless approach)
    logout_data = LogoutRequest()

    # Mock the datetime to return a predictable timestamp
    with patch("controllers.auth.logout.datetime") as mock_datetime:
        mock_timestamp = MagicMock()
        mock_datetime.now.return_value = mock_timestamp

        # Call the function with current_user as a direct parameter (bypassing Depends)
        result = logout_user(logout_data, current_user=mock_user)

        # Verify result
        assert result.message == "Logged out successfully"
        assert result.success is True
        assert result.timestamp is not None

def test_logout_exception_handling():
    # Mock user data
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"

    # Mock logout data
    logout_data = LogoutRequest()

    # Mock datetime to raise an exception
    with patch("controllers.auth.logout.datetime") as mock_datetime:
        mock_datetime.now.side_effect = Exception("Time error")

        # Test that the function handles exceptions gracefully
        with pytest.raises(Exception) as exc_info:
            logout_user(logout_data, current_user=mock_user)

        assert "Time error" in str(exc_info.value)

def test_logout_debug():
    # Mock user data
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.name = "Test User"

    # Mock datetime to return a predictable timestamp
    with patch("controllers.auth.logout.datetime") as mock_datetime:
        mock_timestamp = MagicMock()
        mock_timestamp.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_datetime.now.return_value = mock_timestamp

        # Call the function with current_user as a direct parameter (bypassing Depends)
        result = logout_debug(current_user=mock_user)

        # Verify result
        assert result["message"] == "Debug endpoint working!"
        assert result["user_found"] is True
        assert result["user_email"] == "test@example.com"
        assert result["user_name"] == "Test User"
        assert "timestamp" in result
