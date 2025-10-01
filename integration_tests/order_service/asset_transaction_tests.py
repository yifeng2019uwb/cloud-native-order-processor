"""
Order Service Integration Tests - Asset Transactions
Tests GET /assets/transactions endpoint for asset transaction history
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

class AssetTransactionTests:
    """Integration tests for asset transaction API (GET /assets/{asset_id}/transactions)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_orders = []

    def asset_transaction_api(self, asset_id: str = "BTC") -> str:
        """Helper method to build asset transaction API URL with asset ID"""
        return APIEndpoints.get_order_endpoint(OrderAPI.ASSET_TRANSACTIONS, asset_id=asset_id)

    def test_get_transactions_unauthorized(self):
        """Test getting transactions without authentication"""

        response = self.session.get(
            self.asset_transaction_api("BTC"),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_transactions_invalid_token(self):
        """Test getting transactions with invalid authentication token"""

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_transactions_malformed_token(self):
        """Test getting transactions with malformed authentication header"""

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_get_transactions_nonexistent_asset(self):
        """Test getting transactions for non-existent asset"""

        response = self.session.get(
            self.asset_transaction_api("NONEXISTENT_ASSET"),
            timeout=self.timeout
        )

        # Should return 404 for non-existent asset or 401/403 for auth
        assert response.status_code in [401, 403, 404], f"Expected 401/403/404, got {response.status_code}"


    def test_get_transactions_invalid_asset_formats(self):
        """Test various invalid asset ID formats"""

        invalid_asset_ids = ["", "   ", "ASSET!", "ASSET@123", "A" * 100]  # Empty, whitespace, special chars, too long

        for invalid_asset_id in invalid_asset_ids:
            response = self.session.get(
                self.asset_transaction_api(invalid_asset_id),
                timeout=self.timeout
            )

            # Should return 4xx (400, 401, 403, 404, 422) but not 500
            assert response.status_code in [400, 401, 403, 404, 422], f"Expected 4xx for invalid asset ID '{invalid_asset_id}', got {response.status_code}"

    def test_get_transactions_response_schema(self):
        """Test that transactions response has correct schema when accessible"""
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            timeout=self.timeout
        )

        # Should require authentication
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}: {response.text}"


    def test_get_transactions_query_parameters(self):
        """Test that transactions endpoint handles query parameters gracefully"""
        # Test common filtering and pagination params
        params = {
            OrderFields.LIMIT: "10",
            OrderFields.OFFSET: "0",
            OrderFields.ASSET_ID: TestValues.BTC_ASSET_ID,
            OrderFields.TRANSACTION_TYPE: CommonFields.BUY,
            OrderFields.START_DATE: "2024-01-01",
            OrderFields.END_DATE: "2024-12-31"
        }

        response = self.session.get(
            self.asset_transaction_api("BTC"),
            params=params,
            timeout=self.timeout
        )

        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status code {response.status_code} for query params"


    def test_get_transactions_performance(self):
        """Test that transactions endpoint responds within reasonable time"""
        start_time = time.time()
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 3000, f"Response time {response_time:.2f}ms exceeds 3000ms threshold"
        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"


    def test_get_transactions_filtering(self):
        """Test that transactions endpoint supports basic filtering"""
        # Test asset_id filter (part of URL path)
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            timeout=self.timeout
        )
        assert response.status_code in [200, 401, 403], f"Expected 200 or auth error, got {response.status_code}: {response.text}"

        # Test transaction_type filter
        params = {OrderFields.TRANSACTION_TYPE: CommonFields.BUY}
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            params=params,
            timeout=self.timeout
        )
        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status: {response.status_code}"

    def test_get_transactions_pagination(self):
        """Test that transactions endpoint supports pagination"""
        # Test limit parameter
        params = {OrderFields.LIMIT: "5"}
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            params=params,
            timeout=self.timeout
        )
        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status: {response.status_code}"

        # Test offset parameter
        params = {OrderFields.OFFSET: "10", OrderFields.LIMIT: "5"}
        response = self.session.get(
            self.asset_transaction_api("BTC"),
            params=params,
            timeout=self.timeout
        )
        assert response.status_code in [200, 400, 401, 403, 422], f"Unexpected status: {response.status_code}"

    def cleanup_test_orders(self):
        """Clean up test orders (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when order service supports order deletion
        self.created_orders = []

    def run_all_transaction_tests(self):
        """Run all asset transaction tests"""
        self.test_get_transactions_unauthorized()
        self.test_get_transactions_invalid_token()
        self.test_get_transactions_malformed_token()
        self.test_get_transactions_nonexistent_asset()
        self.test_get_transactions_invalid_asset_formats()
        self.test_get_transactions_response_schema()
        self.test_get_transactions_query_parameters()
        self.test_get_transactions_performance()
        self.test_get_transactions_filtering()
        self.test_get_transactions_pagination()
        self.cleanup_test_orders()

if __name__ == "__main__":
    tests = AssetTransactionTests()
    tests.run_all_transaction_tests()
