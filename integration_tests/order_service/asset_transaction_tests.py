"""
Order Service Integration Tests - Asset Transactions
Tests GET /assets/{asset_id}/transactions endpoint - validates transaction history
"""
import requests
import time
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, TestValues, UserFields

class AssetTransactionTests:
    """Integration tests for asset transaction history API"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def asset_transaction_api(self, asset_id: str) -> str:
        """Helper method to build asset transaction API URLs"""
        return APIEndpoints.get_order_endpoint(OrderAPI.GET_ASSET_TRANSACTIONS_BY_ID, asset_id=asset_id)

    def test_empty_transactions(self):
        """Test new user has no asset transactions"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.asset_transaction_api(TestValues.BTC_ASSET_ID),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200

    def test_transactions_after_buy(self):
        """Test transaction history contains buy record after order"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        # Deposit and buy
        deposit_data = {UserFields.AMOUNT: 200000}
        self.session.post(
            APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )

        order_data = {
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.ORDER_TYPE: "market_buy",
            OrderFields.QUANTITY: 0.5
        }
        self.session.post(
            APIEndpoints.get_order_endpoint(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )

        # Get transactions
        response = self.session.get(
            self.asset_transaction_api(TestValues.BTC_ASSET_ID),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']) >= 1

    def test_transactions_performance(self):
        """Test transactions endpoint responds quickly"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        start_time = time.time()
        response = self.session.get(
            self.asset_transaction_api(TestValues.BTC_ASSET_ID),
            headers=headers,
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        assert response_time < 3000
        assert response.status_code == 200

    def run_all_transaction_tests(self):
        """Run all asset transaction tests"""
        self.test_empty_transactions()
        self.test_transactions_after_buy()
        self.test_transactions_performance()

if __name__ == "__main__":
    tests = AssetTransactionTests()
    tests.run_all_transaction_tests()
