"""
Order Service Integration Tests - Health Check
Tests GET /health endpoint - validates service health
"""
import requests
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from api_endpoints import APIEndpoints, OrderAPI

class OrderHealthTests:
    """Integration tests for order service health endpoint"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def health_api(self) -> str:
        """Helper method to build health API URL"""
        return APIEndpoints.get_order_endpoint(OrderAPI.HEALTH)

    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data

    def test_health_performance(self):
        """Test health endpoint responds quickly"""
        start_time = time.time()
        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        assert response_time < 1000
        assert response.status_code == 200

    def run_all_health_tests(self):
        """Run all health tests"""
        self.test_health_check()
        self.test_health_performance()

if __name__ == "__main__":
    tests = OrderHealthTests()
    tests.run_all_health_tests()
