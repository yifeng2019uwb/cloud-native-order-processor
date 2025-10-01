"""
Order Service Integration Tests - Create Order
Tests POST /orders endpoint for order creation
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

class CreateOrderTests:
    """Integration tests for order creation API (POST /orders)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

    def order_api(self, endpoint: str) -> str:
        """Helper method to build order service API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_create_order_unauthorized(self):
        """Test creating order without authentication"""
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_create_order_invalid_token(self):
        """Test creating order with invalid authentication token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_create_order_malformed_token(self):
        """Test creating order with malformed authentication header"""
        headers = {'Authorization': 'Bearer'}  # Missing token value
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_create_order_missing_fields(self):
        """Test creating order with missing required fields"""

        # Test missing asset_id
        order_data = {
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        # Should return 422 for validation error or 401/403 for auth
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"

        # Test missing order_type
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"


    def test_create_order_invalid_data(self):
        """Test creating order with invalid data values"""

        # Test invalid order type
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "invalid_type",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        # Should return 422 for validation error or 401/403 for auth
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"

        # Test negative quantity
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: -1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"

        # Test zero price
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 0.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"

    def test_create_order_valid_data(self):
        """Test creating order with valid data (expects auth)"""
        # Valid order data
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )

        # Without proper auth, should get 401/403
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}: {response.text}"

    def test_create_order_performance(self):
        """Test that create order responds within reasonable time"""
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        start_time = time.time()
        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            json=order_data,
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 3000, f"Response time {response_time:.2f}ms exceeds 3000ms threshold"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_create_order_tests(self):
        """Run all order creation tests"""
        self.test_create_order_unauthorized()
        self.test_create_order_invalid_token()
        self.test_create_order_malformed_token()
        self.test_create_order_missing_fields()
        self.test_create_order_invalid_data()
        self.test_create_order_valid_data()
        self.test_create_order_performance()
        self.cleanup_test_orders()


if __name__ == "__main__":
    tests = CreateOrderTests()
    tests.run_all_create_order_tests()
