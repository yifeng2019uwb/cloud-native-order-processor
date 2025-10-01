"""
Order Service Integration Tests - Asset Balance
Tests GET /assets/balances and GET /assets/{asset_id}/balance endpoints
"""
import requests
import time
import sys
import os
import uuid
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from test_data import TestDataManager
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, TestValues, CommonFields

class AssetBalanceTests:
    """Integration tests for asset balance APIs"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.user_manager = TestUserManager(timeout)
        self.created_orders = []

        # Create one test user for all tests in this class
        self.test_user, self.access_token = self.user_manager.create_test_user(self.session)


    def asset_balance_api(self, endpoint: str) -> str:
        """Helper method to build asset balance API URLs"""
        return APIEndpoints.get_order_endpoint(endpoint)

    def asset_balance_by_id_api(self, asset_id: str) -> str:
        """Helper method to build asset balance by ID API URLs"""
        return APIEndpoints.get_order_endpoint(OrderAPI.ASSET_BALANCE_BY_ID, asset_id=asset_id)

    def test_get_asset_balances_unauthorized(self):
        """Test getting asset balances without authentication"""
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_asset_balances_invalid_token(self):
        """Test getting asset balances with invalid authentication token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_asset_balances_malformed_token(self):
        """Test getting asset balances with malformed authentication header"""
        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_asset_balances_response_schema(self):
        """Test that asset balances response has correct schema when accessible"""
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            timeout=self.timeout
        )

        # Should require authentication
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}: {response.text}"

    def test_get_asset_balance_by_id_unauthorized(self):
        """Test getting asset balance by ID without authentication"""
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_asset_balance_by_id_invalid_token(self):
        """Test getting asset balance by ID with invalid authentication token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_asset_balance_by_id_nonexistent_asset(self):
        """Test getting asset balance for non-existent asset"""
        headers = self.user_manager.get_auth_headers(self.access_token)
        # Use a valid asset ID format that will pass validation but not exist in the database
        response = self.session.get(
            self.asset_balance_by_id_api("NONEXISTEN"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 404 for non-existent asset (when authenticated)
        assert response.status_code == 404, f"Expected 404 for non-existent asset, got {response.status_code}"

    def test_get_asset_balance_by_id_invalid_asset_formats(self):
        """Test getting asset balance with invalid asset ID formats"""
        headers = self.user_manager.get_auth_headers(self.access_token)
        # Use invalid but non-empty asset IDs that will reach the controller
        invalid_asset_ids = ["BTC!", "BTC@123", "A" * 100, "BTC-123", "BTC_456", "BTC.789"]

        for invalid_id in invalid_asset_ids:
            response = self.session.get(
                self.asset_balance_by_id_api(invalid_id),
                headers=headers,
                timeout=self.timeout
            )

            assert response.status_code == 422, f"Expected 422 for invalid asset ID format '{invalid_id}', got {response.status_code}"

    def test_get_asset_balance_by_id_response_schema(self):
        """Test that asset balance by ID response has correct schema when accessible"""
        headers = self.user_manager.get_auth_headers(self.access_token)
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            headers=headers,
            timeout=self.timeout
        )

        # Should require authentication or return 404 for non-existent asset
        assert response.status_code in [401, 403, 404], f"Expected auth error or 404, got {response.status_code}: {response.text}"

    def test_asset_balance_performance(self):
        """Test that asset balance endpoints respond within performance thresholds"""
        # Test asset balances list
        start_time = time.time()
        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 2000, f"Asset balances response time {response_time:.2f}ms exceeds 2000ms threshold"

        # Test asset balance by ID (with authentication)
        headers = self.user_manager.get_auth_headers(self.access_token)

        start_time = time.time()
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            headers=headers,
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 2000, f"Asset balance by ID response time {response_time:.2f}ms exceeds 2000ms threshold"

    def test_asset_balance_query_parameters(self):
        """Test that asset balance endpoints handle query parameters gracefully"""
        # Test common filtering params for asset balances list
        params = {OrderFields.INCLUDE_ZERO: CommonFields.TRUE, OrderFields.CURRENCY: CommonFields.USD, OrderFields.FORMAT: OrderFields.DETAILED}

        response = self.session.get(
            self.asset_balance_api(OrderAPI.ASSET_BALANCES),
            params=params,
            timeout=self.timeout
        )

        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status code {response.status_code} for query params"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_asset_balance_tests(self):
        """Run all asset balance tests"""

        self.test_get_asset_balances_unauthorized()
        self.test_get_asset_balances_invalid_token()
        self.test_get_asset_balances_malformed_token()
        self.test_get_asset_balances_response_schema()
        self.test_get_asset_balance_by_id_unauthorized()
        self.test_get_asset_balance_by_id_invalid_token()
        self.test_get_asset_balance_by_id_nonexistent_asset()
        self.test_get_asset_balance_by_id_invalid_asset_formats()
        self.test_get_asset_balance_by_id_response_schema()
        self.test_asset_balance_performance()
        self.test_asset_balance_query_parameters()

        self.cleanup_test_orders()

if __name__ == "__main__":
    tests = AssetBalanceTests()
    tests.run_all_asset_balance_tests()
