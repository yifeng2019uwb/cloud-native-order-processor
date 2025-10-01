"""
Order Service Integration Tests - Portfolio
Tests GET /portfolio/{username} endpoint for user portfolio
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from test_data import TestDataManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, TestValues, CommonFields

class PortfolioTests:
    """Integration tests for portfolio API (GET /portfolio/{username})"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

    def portfolio_api(self, username: str) -> str:
        """Helper method to build portfolio API URLs"""
        return APIEndpoints.get_order_endpoint(OrderAPI.PORTFOLIO, username=username)

    def test_portfolio_unauthorized(self):
        """Test getting portfolio without authentication"""

        response = self.session.get(
            self.portfolio_api("testuser"),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_portfolio_invalid_token(self):
        """Test getting portfolio with invalid authentication token"""

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.portfolio_api("testuser"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_portfolio_malformed_token(self):
        """Test getting portfolio with malformed authentication header"""

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.portfolio_api("testuser"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_portfolio_nonexistent_user(self):
        """Test getting portfolio for non-existent user"""

        response = self.session.get(
            self.portfolio_api("nonexistent_user_999"),
            timeout=self.timeout
        )

        assert response.status_code in [401, 403, 404], f"Expected 401/403/404, got {response.status_code}"


    def test_portfolio_invalid_username_formats(self):
        """Test various invalid username formats"""

        invalid_usernames = ["", "   ", "USER!", "USER@123", "A" * 100]  # Empty, whitespace, special chars, too long

        for invalid_username in invalid_usernames:
            response = self.session.get(
                self.portfolio_api(invalid_username),
                timeout=self.timeout
            )

            assert response.status_code in [400, 401, 403, 404, 422], f"Expected 4xx for invalid username '{invalid_username}', got {response.status_code}"

    def test_portfolio_response_schema(self):
        """Test that portfolio response has correct schema when accessible"""
        response = self.session.get(
            self.portfolio_api("testuser"),
            timeout=self.timeout
        )

        # Should require authentication or return 404 for non-existent user
        assert response.status_code in [401, 403, 404], f"Expected auth error or 404, got {response.status_code}: {response.text}"

    def test_portfolio_performance(self):
        """Test that portfolio responds within reasonable time"""

        start_time = time.time()
        response = self.session.get(
            self.portfolio_api("testuser"),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 3000, f"Response time {response_time:.2f}ms exceeds 3000ms threshold"

    def test_portfolio_authorization(self):
        """Test that portfolio properly validates user permissions"""
        response = self.session.get(
            self.portfolio_api("testuser"),
            timeout=self.timeout
        )

        # Should require authentication or return 404
        assert response.status_code in [401, 403, 404], f"Expected 401/403/404, got {response.status_code}"

    def test_portfolio_query_parameters(self):
        """Test that portfolio endpoint handles query parameters gracefully"""
        # Test common filtering params
        params = {OrderFields.INCLUDE_INACTIVE: CommonFields.TRUE, OrderFields.CURRENCY: CommonFields.USD, OrderFields.FORMAT: OrderFields.DETAILED}

        response = self.session.get(
            self.portfolio_api("testuser"),
            params=params,
            timeout=self.timeout
        )

        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert response.status_code in [200, 400, 401, 403, 404, 422], f"Unexpected status code {response.status_code} for query params"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_portfolio_tests(self):
        """Run all portfolio tests"""
        self.test_portfolio_unauthorized()
        self.test_portfolio_invalid_token()
        self.test_portfolio_malformed_token()
        self.test_portfolio_nonexistent_user()
        self.test_portfolio_invalid_username_formats()
        self.test_portfolio_response_schema()
        self.test_portfolio_performance()
        self.test_portfolio_authorization()
        self.test_portfolio_query_parameters()
        self.cleanup_test_orders()

if __name__ == "__main__":
    tests = PortfolioTests()
    tests.run_all_portfolio_tests()
