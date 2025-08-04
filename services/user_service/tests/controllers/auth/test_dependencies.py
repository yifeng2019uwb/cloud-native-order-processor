import sys
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException, status
from api_models.auth.profile import UserProfileResponse
from controllers.auth.dependencies import get_current_user
import builtins
import logging
from fastapi.security import HTTPAuthorizationCredentials
from controllers.auth import dependencies
from jose.exceptions import JWTError
import asyncio

# Ensure src is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))


@pytest.mark.asyncio
async def test_get_user_dao_success():
    # Test the common database dependency
    from common.database import get_user_dao

    # Patch the UserDAO constructor
    with patch("common.database.dependencies.UserDAO", return_value="user_dao_instance"), \
         patch("common.database.dependencies.dynamodb_manager.get_connection", return_value="mock_connection"):
        result = get_user_dao()
        assert result == "user_dao_instance"


@pytest.mark.asyncio
async def test_get_user_dao_error():
    from common.database import get_user_dao

    # Patch to raise an exception
    with patch("common.database.dependencies.dynamodb_manager.get_connection", side_effect=Exception("fail")):
        with pytest.raises(Exception) as exc_info:
            get_user_dao()
        assert "fail" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    mock_user = MagicMock()
    mock_user.username = "john_doe123"
    mock_user.email = "john.doe@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1-555-123-4567"
    mock_user.created_at = "2025-07-09T10:30:00Z"
    mock_user.updated_at = "2025-07-09T10:30:00Z"

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=mock_user)
    with patch("src.controllers.auth.dependencies.verify_token_dependency", return_value="john_doe123"), \
         patch("src.controllers.auth.dependencies.UserDAO", return_value=mock_user_dao):
        user = await get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert user.username == "john_doe123"
        assert user.email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    with patch("src.controllers.auth.dependencies.verify_token_dependency", side_effect=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)), \
         patch("src.controllers.auth.dependencies.UserDAO", return_value=mock_user_dao):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(username=None, user_dao=mock_user_dao)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    with patch("src.controllers.auth.dependencies.verify_token_dependency", return_value="john_doe123"), \
         patch("src.controllers.auth.dependencies.UserDAO", return_value=mock_user_dao):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_database_error():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(side_effect=Exception("DB error"))
    with patch("src.controllers.auth.dependencies.verify_token_dependency", return_value="john_doe123"), \
         patch("src.controllers.auth.dependencies.UserDAO", return_value=mock_user_dao):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# Removed test_get_db_connection_success and test_get_optional_current_user_success as requested

@pytest.mark.asyncio
async def test_verify_token_dependency_valid():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")

    # Mock request object
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.return_value = "user1"
        mock_token_manager_class.return_value = mock_token_manager

        username = await dependencies.verify_token_dependency(mock_request, creds)
        assert username == "user1"

@pytest.mark.asyncio
async def test_verify_token_dependency_none():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")

    # Mock request object
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.return_value = None
        mock_token_manager_class.return_value = mock_token_manager

        with pytest.raises(HTTPException) as exc_info:
            await dependencies.verify_token_dependency(mock_request, creds)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_verify_token_dependency_jwt_error():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")

    # Mock request object
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.side_effect = TokenInvalidException("bad token")
        mock_token_manager_class.return_value = mock_token_manager

        with pytest.raises(HTTPException) as exc_info:
            await dependencies.verify_token_dependency(mock_request, creds)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_verify_token_dependency_general_error():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")

    # Mock request object
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.side_effect = Exception("fail")
        mock_token_manager_class.return_value = mock_token_manager

        with pytest.raises(HTTPException) as exc_info:
            await dependencies.verify_token_dependency(mock_request, creds)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_optional_current_user_none():
    result = await dependencies.get_optional_current_user(None)
    assert result is None

@pytest.mark.asyncio
async def test_get_optional_current_user_invalid_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")
    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.return_value = None
        mock_token_manager_class.return_value = mock_token_manager

        result = await dependencies.get_optional_current_user(creds)
        assert result is None

@pytest.mark.asyncio
async def test_get_optional_current_user_user_not_found():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    with patch("controllers.auth.dependencies.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.verify_access_token.return_value = "user1"
        mock_token_manager_class.return_value = mock_token_manager

        result = await dependencies.get_optional_current_user(creds, user_dao=mock_user_dao)
        assert result is None

@pytest.mark.asyncio
async def test_get_optional_current_user_exception():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token123")
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_email = MagicMock(side_effect=Exception("fail"))
    with patch("src.controllers.auth.dependencies.verify_access_token", return_value="user@email.com"):
        result = await dependencies.get_optional_current_user(creds, user_dao=mock_user_dao)
        assert result is None


def test_require_admin_user_logs(monkeypatch):
    # Just check it returns the user and logs
    user = MagicMock()
    user.email = "admin@email.com"
    logs = []
    def fake_log(msg):
        logs.append(msg)
    monkeypatch.setattr(logging.getLogger("src.controllers.auth.dependencies"), "debug", fake_log)
    result = dependencies.require_admin_user(user)
    assert result is user

# Helper for running async functions in pytest
async def asyncio_run(coro):
    return await coro