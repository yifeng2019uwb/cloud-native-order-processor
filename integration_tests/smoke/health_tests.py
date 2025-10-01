"""
Smoke tests for basic connectivity
Tests service health endpoints
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from api_endpoints import APIEndpoints, UserAPI, InventoryAPI, OrderAPI

class HealthTests:
    """Smoke tests for service connectivity"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def test_user_service_health(self):
        """Test User Service health endpoint"""
        response = self.session.get(
            APIEndpoints.get_user_endpoint(UserAPI.HEALTH),
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data

    def test_inventory_service_health(self):
        """Test Inventory Service health endpoint"""
        response = self.session.get(
            APIEndpoints.get_inventory_endpoint(InventoryAPI.HEALTH),
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data

    def test_order_service_health(self):
        """Test Order Service health endpoint"""
        response = self.session.get(
            APIEndpoints.get_order_endpoint(OrderAPI.HEALTH),
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data

    def run_all_health_tests(self):
        """Run all smoke tests"""
        self.test_user_service_health()
        self.test_inventory_service_health()
        self.test_order_service_health()

if __name__ == "__main__":
    tests = HealthTests()
    tests.run_all_health_tests()
