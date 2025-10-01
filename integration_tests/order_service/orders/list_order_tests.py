"""
Order Service Integration Tests - List Orders
Tests GET /orders endpoint - validates order listing and filtering
"""
import requests
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, CommonFields

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
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert CommonFields.ORDERS in data or CommonFields.DATA in data

    def test_list_orders_pagination(self):
        """Test listing orders with pagination parameters"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        params = {OrderFields.LIMIT: "10", OrderFields.OFFSET: "0"}
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            params=params,
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200

    def test_list_orders_performance(self):
        """Test that list orders responds within reasonable time"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

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
