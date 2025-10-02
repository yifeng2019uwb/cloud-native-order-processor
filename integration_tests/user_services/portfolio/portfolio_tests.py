"""
User Service Integration Tests - Portfolio
Tests GET /portfolio endpoint - validates portfolio aggregation
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, TestValues, UserFields, CommonFields

class PortfolioTests:
    """Integration tests for portfolio API - focus on portfolio data accuracy"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def portfolio_api(self) -> str:
        """Helper method to build portfolio API URLs"""
        return APIEndpoints.get_user_endpoint(UserAPI.PORTFOLIO)

    def test_empty_portfolio(self):
        """Test new user has empty portfolio"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.get(
            self.portfolio_api(),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['asset_count'] == 0

    def test_portfolio_after_order(self):
        """Test portfolio contains assets after placing an order"""
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
        order_response = self.session.post(
            APIEndpoints.get_order_endpoint(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )
        assert order_response.status_code == 201

        # Get portfolio - should now contain BTC
        response = self.session.get(
            self.portfolio_api(),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['asset_count'] >= 1

    def run_all_portfolio_tests(self):
        """Run all portfolio tests"""
        self.test_empty_portfolio()
        self.test_portfolio_after_order()

if __name__ == "__main__":
    tests = PortfolioTests()
    tests.run_all_portfolio_tests()
