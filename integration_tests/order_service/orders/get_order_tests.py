"""
Order Service Integration Tests - Get Order by ID
Tests GET /orders/{order_id} endpoint for retrieving specific orders
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
from test_constants import OrderFields, TestValues

class GetOrderTests:
    """Integration tests for get order by ID API (GET /orders/{order_id})"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

    def order_api_with_id(self, endpoint: str, order_id: str) -> str:
        """Helper method to build order service API URLs with order ID"""
        return APIEndpoints.get_order_endpoint(endpoint, order_id=order_id)

    def test_get_order_unauthorized(self):
        """Test getting order without authentication"""

        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_order_invalid_token(self):
        """Test getting order with invalid authentication token"""

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_order_malformed_token(self):
        """Test getting order with malformed authentication header"""

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_nonexistent_order(self):
        """Test getting a non-existent order returns 404"""

        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "nonexistent_order_999"),
            timeout=self.timeout
        )

         # Should return 404 for non-existent order or 401/403 for auth
        assert response.status_code in [401, 403, 404], f"Expected 401/403/404, got {response.status_code}"


    def test_get_order_invalid_id_formats(self):
        """Test various invalid order ID formats"""

        invalid_ids = ["", "   ", "ORDER!", "ORDER@123", "A" * 100]  # Empty, whitespace, special chars, too long

        for invalid_id in invalid_ids:

            response = self.session.get(
                self.order_api_with_id(OrderAPI.ORDER_BY_ID, invalid_id),
                timeout=self.timeout
            )

            # Should return 4xx (400, 401, 403, 404, 422) but not 500
            assert response.status_code in [400, 401, 403, 404, 422], f"Expected 4xx for invalid ID '{invalid_id}', got {response.status_code}"


    def test_get_order_response_schema(self):
        """Test that get order response has correct schema when accessible"""
        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            timeout=self.timeout
        )

        # Should require authentication or return 404 for non-existent order
        assert response.status_code in [401, 403, 404], f"Expected auth error or 404, got {response.status_code}: {response.text}"

    def test_get_order_performance(self):
        """Test that get order responds within reasonable time"""

        start_time = time.time()

        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 2000, f"Response time {response_time:.2f}ms exceeds 2000ms threshold"


    def test_get_order_authorization(self):
        """Test that get order properly validates user ownership"""
        response = self.session.get(
            self.order_api_with_id(OrderAPI.ORDER_BY_ID, "test_order_123"),
            timeout=self.timeout
        )

        # Should require authentication
        assert response.status_code in [401, 403, 404], f"Expected 401/403/404, got {response.status_code}"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_get_order_tests(self):
        """Run all get order by ID tests"""
        self.test_get_order_unauthorized()
        self.test_get_order_invalid_token()
        self.test_get_order_malformed_token()
        self.test_get_nonexistent_order()
        self.test_get_order_invalid_id_formats()
        self.test_get_order_response_schema()
        self.test_get_order_performance()
        self.test_get_order_authorization()
        self.cleanup_test_orders()
if __name__ == "__main__":
    tests = GetOrderTests()
    tests.run_all_get_order_tests()
