"""
Order Service Integration Tests - List Orders
Tests GET /orders endpoint - validates order listing and filtering
"""
import requests
import time
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, CommonFields

# Use plain dictionaries for integration tests to maintain black-box testing
# No need to import service models as we test HTTP/JSON responses

class ListOrderTests:
    """Integration tests for order listing API (GET /orders)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def order_api(self, endpoint: str) -> str:
        """Helper method to build order service API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_list_orders_empty(self):
        """Test listing orders for new user returns empty list"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200

        # Parse response as dict
        response_data = response.json()

        # Assert using dict keys
        assert "data" in response_data
        assert response_data["data"] is not None
        assert isinstance(response_data["data"], list)
        assert len(response_data["data"]) == 0, "New user should have no orders"

    def test_list_orders_pagination(self):
        """Test listing orders with pagination parameters"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        params = {OrderFields.LIMIT: "10", OrderFields.OFFSET: "0"}
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            params=params,
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200

        # Parse response as dict
        response_data = response.json()

        # Assert using dict keys
        assert "data" in response_data
        assert response_data["data"] is not None
        assert "has_more" in response_data
        assert response_data["has_more"] is not None

    def test_list_orders_performance(self):
        """Test that list orders responds within reasonable time"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        start_time = time.time()
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            headers=headers,
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        assert response_time < 2000
        assert response.status_code == 200

    def run_all_list_order_tests(self):
        """Run all order listing tests"""
        self.test_list_orders_empty()
        self.test_list_orders_pagination()
        self.test_list_orders_performance()

if __name__ == "__main__":
    tests = ListOrderTests()
    tests.run_all_list_order_tests()
