"""
Tests for get_balance controller
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.controllers.balance.get_balance import get_user_balance, router
from src.api_models.balance.balance_models import BalanceResponse
from common.data.entities.user import Balance, User
from common.exceptions.shared_exceptions import CNOPUserNotFoundException, CNOPInternalServerException


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = Mock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request


class TestGetUserBalance:
    """Test cases for get_user_balance function"""

    @pytest.fixture
    def mock_current_user(self):
        """Mock current user"""
        user = Mock(spec=User)
        user.username = "testuser123"
        return user

    @pytest.fixture
    def mock_balance_dao(self):
        """Mock balance DAO"""
        dao = Mock()
        return dao

    @pytest.fixture
    def sample_balance(self):
        """Sample balance data"""

        balance = Mock(spec=Balance)
        balance.current_balance = Decimal('1250.75')
        balance.updated_at = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        return balance

    def test_get_user_balance_success(self, mock_current_user, mock_balance_dao, sample_balance):
        """Test successful balance retrieval"""
        mock_balance_dao.get_balance.return_value = sample_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('1250.75')
        assert result.updated_at == datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.assert_called_once_with("testuser123")

    def test_get_user_balance_zero_balance(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when user has zero balance"""

        zero_balance = Mock(spec=Balance)
        zero_balance.current_balance = Decimal('0.00')
        zero_balance.updated_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.return_value = zero_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('0.00')
        assert result.updated_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_get_user_balance_negative_balance(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when user has negative balance (overdraft)"""

        negative_balance = Mock(spec=Balance)
        negative_balance.current_balance = Decimal('-50.25')
        negative_balance.updated_at = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.return_value = negative_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('-50.25')
        assert result.updated_at == datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

    def test_get_user_balance_large_amount(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval with large amount"""

        large_balance = Mock(spec=Balance)
        large_balance.current_balance = Decimal('999999.99')
        large_balance.updated_at = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.return_value = large_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('999999.99')
        assert result.updated_at == datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

    def test_get_user_balance_decimal_precision(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval with precise decimal amounts"""

        precise_balance = Mock(spec=Balance)
        precise_balance.current_balance = Decimal('123.456789')
        precise_balance.updated_at = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.return_value = precise_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=mock_current_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('123.456789')
        assert result.updated_at == datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

    def test_get_user_balance_user_not_found_exception(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when UserNotFoundException is raised"""
        mock_balance_dao.get_balance.side_effect = CNOPUserNotFoundException("User not found")

        # UserNotFoundException should be re-raised without modification
        with pytest.raises(CNOPUserNotFoundException, match="User not found"):
            get_user_balance(
                request=create_mock_request(),
                current_user=mock_current_user,
                balance_dao=mock_balance_dao
            )

    def test_get_user_balance_generic_exception(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when generic exception occurs"""
        mock_balance_dao.get_balance.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPInternalServerException, match="Failed to get balance: Database connection failed"):
            get_user_balance(
                request=create_mock_request(),
                current_user=mock_current_user,
                balance_dao=mock_balance_dao
            )

    def test_get_user_balance_database_error(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when database error occurs"""
        mock_balance_dao.get_balance.side_effect = Exception("Table does not exist")

        with pytest.raises(CNOPInternalServerException, match="Failed to get balance: Table does not exist"):
            get_user_balance(
                request=create_mock_request(),
                current_user=mock_current_user,
                balance_dao=mock_balance_dao
            )

    def test_get_user_balance_network_error(self, mock_current_user, mock_balance_dao):
        """Test balance retrieval when network error occurs"""
        mock_balance_dao.get_balance.side_effect = Exception("Connection timeout")

        with pytest.raises(CNOPInternalServerException, match="Failed to get balance: Connection timeout"):
            get_user_balance(
                request=create_mock_request(),
                current_user=mock_current_user,
                balance_dao=mock_balance_dao
            )

    def test_get_user_balance_different_user(self, mock_balance_dao):
        """Test balance retrieval for different user"""

        different_user = Mock(spec=User)
        different_user.username = "anotheruser456"

        different_balance = Mock(spec=Balance)
        different_balance.current_balance = Decimal('500.00')
        different_balance.updated_at = datetime(2024, 1, 10, 10, 0, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.return_value = different_balance

        result = get_user_balance(
            request=create_mock_request(),
            current_user=different_user,
            balance_dao=mock_balance_dao
        )

        assert result.current_balance == Decimal('500.00')
        assert result.updated_at == datetime(2024, 1, 10, 10, 0, 0, tzinfo=timezone.utc)

        mock_balance_dao.get_balance.assert_called_once_with("anotheruser456")


class TestGetBalanceRouter:
    """Test cases for get_balance router configuration"""

    def test_router_tags(self):
        """Test router tags configuration"""
        assert router.tags == ["balance"]

    def test_router_endpoint_path(self):
        """Test router endpoint path"""
        assert router.routes[0].path == "/balance"

    def test_router_response_models(self):
        """Test router response models"""
        route = router.routes[0]
        assert route.response_model is not None

    def test_router_responses_documentation(self):
        """Test router responses documentation"""
        route = router.routes[0]
        assert route.responses is not None
        assert 200 in route.responses
        assert 401 in route.responses
        assert 404 in route.responses
        assert 503 in route.responses
