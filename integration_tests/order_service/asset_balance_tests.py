"""
Order Service Integration Tests - Asset Balance
Tests GET /assets/balances and GET /assets/{asset_id}/balance endpoints
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

class AssetBalanceTests:
    """Integration tests for asset balance APIs"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

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

        if response.status_code == 200:
            data = response.json()

            # Check if response has expected structure
            if "asset_balances" in data:
                balances = data["asset_balances"]
                assert isinstance(balances, list), "Asset balances should be a list"

                if balances:
                    balance = balances[0]
                    # Check for common balance fields
                    expected_fields = ["asset_id", "quantity", "current_value", "last_updated"]
                    for field in expected_fields:
                        if field in balance:
                            assert balance[field] is not None, f"Field {field} should not be None"
            else:
                # Alternative response structure
                assert "balances" in data or "data" in data, "Response should contain asset balances data"
        else:
            # For non-200 responses, ensure they're proper error responses
            assert response.status_code in [401, 403, 500], f"Unexpected status code: {response.status_code}"

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
        response = self.session.get(
            self.asset_balance_by_id_api("NONEXISTENT_ASSET_12345"),
            timeout=self.timeout
        )

        # Should return 404 for non-existent asset
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_get_asset_balance_by_id_invalid_asset_formats(self):
        """Test getting asset balance with invalid asset ID formats"""
        invalid_asset_ids = ["", "   ", "BTC!", "BTC@123", "A" * 100]

        for invalid_id in invalid_asset_ids:
            response = self.session.get(
                self.asset_balance_by_id_api(invalid_id),
                timeout=self.timeout
            )

            # Should return 400, 404, or 422 for invalid formats
            assert response.status_code in [400, 404, 422], f"Expected 4xx for invalid ID '{invalid_id}', got {response.status_code}"

    def test_get_asset_balance_by_id_response_schema(self):
        """Test that asset balance by ID response has correct schema when accessible"""
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()

            # Check if response has expected structure
            if "asset_balance" in data:
                balance = data["asset_balance"]
                assert "asset_id" in balance, "Asset balance should contain asset_id"
                assert "quantity" in balance, "Asset balance should contain quantity"
                assert "current_value" in balance, "Asset balance should contain current_value"
            else:
                # Alternative response structure
                assert "asset_id" in data, "Response should contain asset_id"
                assert "quantity" in data, "Response should contain quantity"
        else:
            # For non-200 responses, ensure they're proper error responses
            assert response.status_code in [401, 403, 404, 500], f"Unexpected status code: {response.status_code}"

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

        # Test asset balance by ID
        start_time = time.time()
        response = self.session.get(
            self.asset_balance_by_id_api("BTC"),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 2000, f"Asset balance by ID response time {response_time:.2f}ms exceeds 2000ms threshold"

    def test_asset_balance_query_parameters(self):
        """Test that asset balance endpoints handle query parameters gracefully"""
        # Test common filtering params for asset balances list
        params = {"include_zero": "true", "currency": "USD", "format": "detailed"}

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
        failed_tests = []

        # GET Asset Balances Tests
        try:
            self.test_get_asset_balances_unauthorized()
        except Exception as e:
            failed_tests.append("Asset Balances (Unauthorized)")

        try:
            self.test_get_asset_balances_invalid_token()
        except Exception as e:
            failed_tests.append("Asset Balances (Invalid Token)")

        try:
            self.test_get_asset_balances_malformed_token()
        except Exception as e:
            failed_tests.append("Asset Balances (Malformed Token)")

        try:
            self.test_get_asset_balances_response_schema()
        except Exception as e:
            failed_tests.append("Asset Balances Response Schema")

        # GET Asset Balance by ID Tests
        try:
            self.test_get_asset_balance_by_id_unauthorized()
        except Exception as e:
            failed_tests.append("Asset Balance by ID (Unauthorized)")

        try:
            self.test_get_asset_balance_by_id_invalid_token()
        except Exception as e:
            failed_tests.append("Asset Balance by ID (Invalid Token)")

        try:
            self.test_get_asset_balance_by_id_nonexistent_asset()
        except Exception as e:
            failed_tests.append("Asset Balance by ID (Non-existent Asset)")

        try:
            self.test_get_asset_balance_by_id_invalid_asset_formats()
        except Exception as e:
            failed_tests.append("Asset Balance by ID (Invalid Asset Formats)")

        try:
            self.test_get_asset_balance_by_id_response_schema()
        except Exception as e:
            failed_tests.append("Asset Balance by ID Response Schema")

        # Performance and Query Parameter Tests
        try:
            self.test_asset_balance_performance()
        except Exception as e:
            failed_tests.append("Asset Balance Performance")

        try:
            self.test_asset_balance_query_parameters()
        except Exception as e:
            failed_tests.append("Asset Balance Query Parameters")

        self.cleanup_test_orders()

        # Check if any tests failed
        if failed_tests:
            raise AssertionError(f"Asset balance tests failed: {', '.join(failed_tests)}")

if __name__ == "__main__":
    tests = AssetBalanceTests()
    try:
        tests.run_all_asset_balance_tests()
        print("🎉 All asset balance tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Asset balance tests failed: {e}")
        sys.exit(1)
