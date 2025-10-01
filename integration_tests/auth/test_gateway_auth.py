"""
Gateway Authentication Integration Tests
Tests that protected endpoints require authentication through the API gateway.
This centralizes auth requirement testing - individual endpoint tests focus on business logic.

Individual API tests will:
- Use valid authentication (setup tokens)
- Test business logic, validation, edge cases
- Implicitly verify auth works (tests fail if auth broken)
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from api_endpoints import APIEndpoints, UserAPI, OrderAPI, InventoryAPI

class GatewayAuthTests:
    """Test that protected endpoints require authentication (return 401 without auth)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def test_user_service_no_token(self):
        """Test user service endpoints reject requests without token"""
        endpoints = [
            (APIEndpoints.get_user_endpoint(UserAPI.PROFILE), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_TRANSACTIONS), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT), 'POST'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_WITHDRAW), 'POST'),
            (APIEndpoints.get_user_endpoint(UserAPI.LOGOUT), 'POST'),
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = self.session.get(endpoint, timeout=self.timeout)
            else:
                response = self.session.post(endpoint, json={}, timeout=self.timeout)
            assert response.status_code == 401, f"Expected 401 for {method} {endpoint}, got {response.status_code}"

    def test_user_service_invalid_token(self):
        """Test user service endpoints reject requests with invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        endpoints = [
            (APIEndpoints.get_user_endpoint(UserAPI.PROFILE), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_TRANSACTIONS), 'GET'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_DEPOSIT), 'POST'),
            (APIEndpoints.get_user_endpoint(UserAPI.BALANCE_WITHDRAW), 'POST'),
            (APIEndpoints.get_user_endpoint(UserAPI.LOGOUT), 'POST'),
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = self.session.get(endpoint, headers=headers, timeout=self.timeout)
            else:
                response = self.session.post(endpoint, json={}, headers=headers, timeout=self.timeout)
            assert response.status_code == 401, f"Expected 401 for invalid token at {method} {endpoint}, got {response.status_code}"

    def test_order_service_no_token(self):
        """Test order service endpoints reject requests without token"""
        endpoints = [
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDERS), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDERS), 'POST'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDER_BY_ID).replace('{id}', '123'), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.PORTFOLIO).replace('{username}', 'testuser'), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ASSET_BALANCES), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ASSET_TRANSACTIONS).replace('{asset_id}', 'BTC'), 'GET'),
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = self.session.get(endpoint, timeout=self.timeout)
            else:
                response = self.session.post(endpoint, json={}, timeout=self.timeout)
            assert response.status_code == 401, f"Expected 401 for {method} {endpoint}, got {response.status_code}"

    def test_order_service_invalid_token(self):
        """Test order service endpoints reject requests with invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        endpoints = [
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDERS), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDERS), 'POST'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ORDER_BY_ID).replace('{id}', '123'), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.PORTFOLIO).replace('{username}', 'testuser'), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ASSET_BALANCES), 'GET'),
            (APIEndpoints.get_order_endpoint(OrderAPI.ASSET_TRANSACTIONS).replace('{asset_id}', 'BTC'), 'GET'),
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = self.session.get(endpoint, headers=headers, timeout=self.timeout)
            else:
                response = self.session.post(endpoint, json={}, headers=headers, timeout=self.timeout)
            assert response.status_code == 401, f"Expected 401 for invalid token at {method} {endpoint}, got {response.status_code}"

    def test_malformed_auth_header(self):
        """Test malformed authorization headers return 401"""
        malformed_headers = [
            {'Authorization': 'InvalidScheme token123'},
            {'Authorization': 'Bearer'},
            {'Authorization': 'token_without_bearer'},
            {'Authorization': ''},
        ]

        endpoint = APIEndpoints.get_user_endpoint(UserAPI.PROFILE)

        for headers in malformed_headers:
            response = self.session.get(endpoint, headers=headers, timeout=self.timeout)
            assert response.status_code == 401, f"Expected 401 for malformed header {headers}, got {response.status_code}"

    def test_public_endpoints_accessible(self):
        """Test public endpoints are accessible without auth"""
        endpoints = [
            (APIEndpoints.get_user_endpoint(UserAPI.LOGIN), 'POST'),
            (APIEndpoints.get_user_endpoint(UserAPI.REGISTER), 'POST'),
        ]

        for endpoint, method in endpoints:
            response = self.session.post(endpoint, json={}, timeout=self.timeout)
            # Should NOT return 401 - public endpoints should accept requests
            assert response.status_code != 401, f"Public endpoint {endpoint} should not require auth but got 401"

    def test_inventory_service_is_public(self):
        """Test inventory service endpoints are publicly accessible (no auth required)"""
        endpoints = [
            APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSETS),
            APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSET_BY_ID, asset_id='BTC')
        ]

        for endpoint in endpoints:
            response = self.session.get(endpoint, timeout=self.timeout)
            # Inventory should be public - expect 200 or 404 (not found), NOT 401
            assert response.status_code != 401, f"Inventory should be public but got 401 for {endpoint}"

    def run_all_auth_tests(self):
        """Run all centralized authentication requirement tests"""
        self.test_user_service_no_token()
        self.test_user_service_invalid_token()
        self.test_order_service_no_token()
        self.test_order_service_invalid_token()
        self.test_malformed_auth_header()
        self.test_public_endpoints_accessible()
        self.test_inventory_service_is_public()

if __name__ == "__main__":
    tests = GatewayAuthTests()
    tests.run_all_auth_tests()
