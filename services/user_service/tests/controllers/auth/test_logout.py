import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from src.controllers.auth.logout import logout_user
from api_models.auth.logout import LogoutRequest, LogoutSuccessResponse

@pytest.mark.asyncio
async def test_logout_valid_token():
    mock_user = MagicMock()
    mock_user.email = "john@example.com"
    # Mock get_current_user to return mock_user
    with patch("src.controllers.auth.logout.get_current_user", return_value=mock_user):
        logout_data = LogoutRequest()
        result = await logout_user(logout_data, current_user=mock_user)
        assert isinstance(result, LogoutSuccessResponse)
        assert result.message == "Logged out successfully"
        assert result.success is True
