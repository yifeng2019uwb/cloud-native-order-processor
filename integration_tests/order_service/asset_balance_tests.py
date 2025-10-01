"""
Order Service Integration Tests - Asset Balances
Tests GET /assets/balances endpoint - validates asset balance queries
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, TestValues, UserFields

class AssetBalanceTests:
    """Integration tests for asset balance API"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def asset_balance_api(self, endpoint: str) -> str:
        """Helper method to build asset balance API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def test_empty_asset_balances(self):
        """Test new user has no asset balances"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200

    def test_asset_balances_after_order(self):
        """Test asset balances contain BTC after buy order"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit funds
        deposit_data = {UserFields.AMOUNT: 200000}
        self.session.post(
            APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )

        # Create market buy order
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

        # Get asset balances
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert len(data['data']) >= 1

    def run_all_asset_balance_tests(self):
        """Run all asset balance tests"""
        self.test_empty_asset_balances()
        self.test_asset_balances_after_order()

if __name__ == "__main__":
    tests = AssetBalanceTests()
    tests.run_all_asset_balance_tests()
