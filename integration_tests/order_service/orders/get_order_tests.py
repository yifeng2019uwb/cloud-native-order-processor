"""
Order Service Integration Tests - Get Order
Tests GET /orders/{order_id} endpoint - validates order retrieval
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
from test_constants import OrderFields

# Use plain dictionaries for integration tests to maintain black-box testing
# No need to import service models as we test HTTP/JSON responses

class GetOrderTests:
    """Integration tests for getting order by ID"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def order_api(self, endpoint: str) -> str:
        """Helper method to build order service API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_get_nonexistent_order(self):
        """Test getting non-existent order (should return 404)"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.order_api(OrderAPI.ORDER_BY_ID).replace('{order_id}', 'nonexistent_order_123'),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 404

    def test_get_order_invalid_id_format(self):
        """Test getting order with invalid ID format"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.order_api(OrderAPI.ORDER_BY_ID).replace('{order_id}', 'invalid@#$'),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_get_order_performance(self):
        """Test that get order responds within reasonable time"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        start_time = time.time()
        response = self.session.get(
            self.order_api(OrderAPI.ORDER_BY_ID).replace('{order_id}', 'test_order_123'),
            headers=headers,
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        assert response_time < 2000

    def run_all_get_order_tests(self):
        """Run all get order tests"""
        self.test_get_nonexistent_order()
        self.test_get_order_invalid_id_format()
        self.test_get_order_performance()

if __name__ == "__main__":
    tests = GetOrderTests()
    tests.run_all_get_order_tests()
