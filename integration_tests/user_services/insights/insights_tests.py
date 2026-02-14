"""
Insights Service Integration Tests
Tests GET /insights/portfolio - validates AI insights endpoint returns summary
"""
import uuid
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI, UserAPI
from test_constants import OrderFields, TestValues, UserFields


class InsightsTests:
    """Integration tests for insights API - confirm summary is returned"""

    def __init__(self, timeout: int = 60):
        self.timeout = timeout  # Insights takes longer (LLM call to Gemini)
        self.session = requests.Session()
        self.user_manager = TestUserManager(timeout=timeout)

    def insights_api(self) -> str:
        """Helper method to build insights API URL"""
        return APIEndpoints.get_user_endpoint(UserAPI.INSIGHTS_PORTFOLIO)

    def test_insights_empty_portfolio_returns_message(self):
        """Test new user with empty portfolio returns friendly message"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.insights_api(),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'summary' in data['data']
        assert len(data['data']['summary']) > 0
        assert 'model' in data['data']

    def test_insights_with_portfolio_returns_summary(self):
        """Test user with portfolio and orders gets AI-generated summary"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        # Deposit funds
        deposit_data = {UserFields.AMOUNT: 10000}
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
            OrderFields.QUANTITY: 0.01
        }
        order_response = self.session.post(
            APIEndpoints.get_order_endpoint(OrderAPI.CREATE_ORDER),
            headers=headers,
            json=order_data,
            timeout=self.timeout
        )
        assert order_response.status_code == 201

        # Get insights - should return summary
        response = self.session.get(
            self.insights_api(),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'summary' in data['data']
        assert len(data['data']['summary']) > 0
        assert 'generated_at' in data['data']
        assert 'model' in data['data']

    def test_insights_requires_auth(self):
        """Test insights endpoint requires authentication"""
        response = self.session.get(
            self.insights_api(),
            timeout=self.timeout
        )

        assert response.status_code == 401

    def run_all_insights_tests(self):
        """Run all insights tests"""
        self.test_insights_requires_auth()
        self.test_insights_empty_portfolio_returns_message()
        self.test_insights_with_portfolio_returns_summary()


if __name__ == "__main__":
    tests = InsightsTests()
    tests.run_all_insights_tests()
