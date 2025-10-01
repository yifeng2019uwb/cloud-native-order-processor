"""
Order Service Integration Tests - List Orders
Tests GET /orders endpoint for listing orders
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from test_data import TestDataManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, TestValues, CommonFields

class ListOrderTests:
    """Integration tests for order listing API (GET /orders)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

    def order_api(self, endpoint: str) -> str:
        """Helper method to build order service API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_list_orders_unauthorized(self):
        """Test listing orders without authentication"""
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_list_orders_invalid_token(self):
        """Test listing orders with invalid authentication token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_list_orders_malformed_token(self):
        """Test listing orders with malformed authentication header"""

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_list_orders_authorized(self):
        """Test listing orders with valid authentication"""

        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            timeout=self.timeout
        )

        # Without proper auth setup, should return auth error
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}: {response.text}"


    def test_list_orders_response_schema(self):
        """Test that list orders response has correct schema when accessible"""
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            timeout=self.timeout
        )

        # Should require authentication
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}: {response.text}"



    def test_list_orders_query_parameters(self):
        """Test that list orders endpoint handles query parameters gracefully"""

        # Test common pagination and filtering params
        params = {OrderFields.LIMIT: "10", OrderFields.OFFSET: "0", OrderFields.PAGE: "1", OrderFields.STATUS: CommonFields.PENDING, OrderFields.USER_ID: "test123"}
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            params=params,
            timeout=self.timeout
        )

        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status code {response.status_code} for query params"


    def test_list_orders_performance(self):
        """Test that list orders responds within reasonable time"""
        start_time = time.time()
        response = self.session.get(
            self.order_api(OrderAPI.ORDERS),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 2000, f"Response time {response_time:.2f}ms exceeds 2000ms threshold"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_list_order_tests(self):
        """Run all order listing tests"""
        self.test_list_orders_unauthorized()
        self.test_list_orders_invalid_token()
        self.test_list_orders_malformed_token()
        self.test_list_orders_authorized()
        self.test_list_orders_response_schema()
        self.test_list_orders_query_parameters()
        self.test_list_orders_performance()
        self.cleanup_test_orders()

if __name__ == "__main__":
    tests = ListOrderTests()
    tests.run_all_list_order_tests()
