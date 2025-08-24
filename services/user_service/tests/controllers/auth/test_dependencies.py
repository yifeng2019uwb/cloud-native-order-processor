"""
Tests for auth dependencies module
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# Import the functions to test
from src.controllers.auth.dependencies import (
    verify_gateway_headers,
    get_current_user,
    get_optional_current_user,
    require_admin_user
)

# Import models
from common.entities.user import UserResponse


@pytest.mark.asyncio
async def test_verify_gateway_headers_valid():
    """Test verify_gateway_headers with valid headers"""
    mock_request = MagicMock()

    result = await verify_gateway_headers(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="testuser",
        x_user_role="customer"
    )

    assert result == "testuser"


@pytest.mark.asyncio
async def test_verify_gateway_headers_invalid_source():
    """Test verify_gateway_headers with invalid source header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await verify_gateway_headers(
            request=mock_request,
            x_source="invalid-source",
            x_auth_service="auth-service",
            x_user_id="testuser",
            x_user_role="customer"
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Invalid request source"


@pytest.mark.asyncio
async def test_verify_gateway_headers_invalid_auth_service():
    """Test verify_gateway_headers with invalid auth service header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await verify_gateway_headers(
            request=mock_request,
            x_source="gateway",
            x_auth_service="invalid-service",
            x_user_id="testuser",
            x_user_role="customer"
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Invalid authentication service"


@pytest.mark.asyncio
async def test_verify_gateway_headers_missing_user_id():
    """Test verify_gateway_headers with missing user ID"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await verify_gateway_headers(
            request=mock_request,
            x_source="gateway",
            x_auth_service="auth-service",
            x_user_id=None,
            x_user_role="customer"
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "User authentication required"


@pytest.mark.asyncio
async def test_verify_gateway_headers_missing_source():
    """Test verify_gateway_headers with missing source header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await verify_gateway_headers(
            request=mock_request,
            x_source=None,
            x_auth_service="auth-service",
            x_user_id="testuser",
            x_user_role="customer"
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Invalid request source"


@pytest.mark.asyncio
async def test_verify_gateway_headers_missing_auth_service():
    """Test verify_gateway_headers with missing auth service header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await verify_gateway_headers(
            request=mock_request,
            x_source="gateway",
            x_auth_service=None,
            x_user_id="testuser",
            x_user_role="customer"
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Invalid authentication service"


@pytest.mark.asyncio
async def test_get_current_user_success():
    """Test get_current_user with valid Gateway headers"""
    mock_user = MagicMock()
    mock_user.username = "john_doe123"
    mock_user.email = "john.doe@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1-555-123-4567"
    mock_user.date_of_birth = None
    mock_user.marketing_emails_consent = False
    mock_user.role = "customer"
    mock_user.created_at = "2025-07-09T10:30:00Z"
    mock_user.updated_at = "2025-07-09T10:30:00Z"

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=mock_user)

    with patch("src.controllers.auth.dependencies.verify_gateway_headers", return_value="john_doe123"):
        user = get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert user.username == "john_doe123"
        assert user.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    """Test get_current_user when user not found"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)

    with patch("src.controllers.auth.dependencies.verify_gateway_headers", return_value="john_doe123"):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_database_error():
    """Test get_current_user when database error occurs"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(side_effect=Exception("DB error"))

    with patch("src.controllers.auth.dependencies.verify_gateway_headers", return_value="john_doe123"):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(username="john_doe123", user_dao=mock_user_dao)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_optional_current_user_with_headers():
    """Test get_optional_current_user with valid headers"""
    mock_user = MagicMock()
    mock_user.username = "john_doe123"
    mock_user.email = "john.doe@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1-555-123-4567"
    mock_user.date_of_birth = None
    mock_user.marketing_emails_consent = False
    mock_user.role = "customer"
    mock_user.created_at = "2025-07-09T10:30:00Z"
    mock_user.updated_at = "2025-07-09T10:30:00Z"

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=mock_user)

    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is not None
    assert result.username == "john_doe123"


def test_get_optional_current_user_missing_headers():
    """Test get_optional_current_user with missing headers"""
    mock_user_dao = MagicMock()
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source=None,
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_invalid_headers():
    """Test get_optional_current_user with invalid headers"""
    mock_user_dao = MagicMock()
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="invalid-source",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_user_not_found():
    """Test get_optional_current_user when user not found"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_exception():
    """Test get_optional_current_user when exception occurs"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(side_effect=Exception("fail"))
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_require_admin_user():
    """Test require_admin_user function"""
    mock_user = MagicMock()
    mock_user.email = "admin@example.com"

    result = require_admin_user(current_user=mock_user)

    assert result == mock_user