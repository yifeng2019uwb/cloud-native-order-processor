"""
Order Service Integration Tests - Create Order
Tests POST /orders endpoint - validates order creation and validation
"""
import requests
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, TestValues, UserFields

# Use plain dictionaries for integration tests to maintain black-box testing
# No need to import service models as we test HTTP/JSON responses

class CreateOrderTests:
    """Integration tests for order creation - focus on validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def order_api(self, endpoint: str) -> str:
        """Helper method to build order service API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_create_order_success(self):
        """Test successful order creation"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        # Deposit funds first (within daily limit of 10000)
        deposit_data = {UserFields.AMOUNT: 10000}
        deposit_resp = self.session.post(
            APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert deposit_resp.status_code == 201, f"Deposit failed: {deposit_resp.text}"

        # Create market order (0.1 BTC fits in 10000 balance)
        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "market_buy",
            OrderFields.QUANTITY: 0.1
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 201

        # Parse response as dict
        response_data = response.json()

        # Assert using dict keys
        assert "data" in response_data
        assert response_data["data"] is not None
        assert OrderFields.ORDER_ID in response_data["data"]
        assert response_data["data"][OrderFields.ASSET_ID] == TestValues.BTC_ASSET_ID

    def test_create_order_missing_asset_id(self):
        """Test order creation with missing asset_id is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
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

        assert response.status_code == 422

    def test_create_order_missing_order_type(self):
        """Test order creation with missing order_type is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_create_order_negative_quantity(self):
        """Test order creation with negative quantity is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: -1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_create_order_zero_quantity(self):
        """Test order creation with zero quantity is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_create_order_negative_price(self):
        """Test order creation with negative price is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "buy",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: -50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_create_order_invalid_order_type(self):
        """Test order creation with invalid order_type is rejected"""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "invalid_type",
            OrderFields.QUANTITY: 1.0,
            OrderFields.PRICE: 50000.00
        }

        response = self.session.post(
            self.order_api(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def run_all_create_order_tests(self):
        """Run all order creation tests"""
        self.test_create_order_success()
        self.test_create_order_missing_asset_id()
        self.test_create_order_missing_order_type()
        self.test_create_order_negative_quantity()
        self.test_create_order_zero_quantity()
        self.test_create_order_negative_price()
        self.test_create_order_invalid_order_type()

if __name__ == "__main__":
    tests = CreateOrderTests()
    tests.run_all_create_order_tests()
