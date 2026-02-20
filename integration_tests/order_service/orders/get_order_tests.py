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
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, UserFields, TestValues, CommonFields

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

    def test_get_order_idor_user_b_cannot_get_user_a_order(self):
        """IDOR: User B cannot get User A's order — expect 404 (ownership check from JWT)."""
        # User A: create user, deposit, create order
        user_a = f'testuser_a_{uuid.uuid4().hex[:8]}'
        token_a = self.user_manager.create_test_user(self.session, user_a)
        headers_a = self.user_manager.build_auth_headers(token_a)

        deposit_data = {UserFields.AMOUNT: 10000}
        deposit_resp = self.session.post(
            APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers_a,
            timeout=self.timeout
        )
        assert deposit_resp.status_code == 201, f"Deposit failed: {deposit_resp.text}"

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "market_buy",
            OrderFields.QUANTITY: 0.1
        }
        create_resp = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers_a,
            json=order_data,
            timeout=self.timeout
        )
        assert create_resp.status_code == 201, f"Create order failed: {create_resp.text}"
        order_id = create_resp.json()[CommonFields.DATA][OrderFields.ORDER_ID]

        # User B: different user, try to GET User A's order
        user_b = f'testuser_b_{uuid.uuid4().hex[:8]}'
        token_b = self.user_manager.create_test_user(self.session, user_b)
        headers_b = self.user_manager.build_auth_headers(token_b)

        response = self.session.get(
            self.order_api(OrderAPI.ORDER_BY_ID).replace('{order_id}', order_id),
            headers=headers_b,
            timeout=self.timeout
        )

        assert response.status_code == 404, (
            f"IDOR: User B must not get User A's order; expected 404, got {response.status_code}"
        )

    def run_all_get_order_tests(self):
        """Run all get order tests"""
        self.test_get_nonexistent_order()
        self.test_get_order_invalid_id_format()
        self.test_get_order_performance()
        self.test_get_order_idor_user_b_cannot_get_user_a_order()

if __name__ == "__main__":
    tests = GetOrderTests()
    tests.run_all_get_order_tests()
