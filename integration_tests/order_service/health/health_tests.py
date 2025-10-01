"""
Order Service Integration Tests - Health
Tests GET /health endpoint for service health check
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from test_data import TestDataManager
from api_endpoints import APIEndpoints, OrderAPI
from test_constants import OrderFields, TestValues, CommonFields

class HealthTests:
    """Integration tests for health check API (GET /health)"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()

    def health_api(self) -> str:
        """Helper method to build health API URL"""
        return APIEndpoints.get_order_endpoint(OrderAPI.HEALTH)

    def test_health_endpoint_accessible(self):
        """Test that health endpoint is accessible without authentication"""

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        # Health endpoint should be accessible without auth
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_health_response_schema(self):
        """Test that health response has correct schema"""

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # Check expected fields
        assert CommonFields.STATUS in data, f"Missing status field: {data}"
        assert data[CommonFields.STATUS] in ["healthy", "ok", "up"], f"Unexpected status: {data[CommonFields.STATUS]}"

    def test_health_response_consistency(self):
        """Test that health endpoint returns consistent responses"""

        responses = []
        for i in range(3):
            response = self.session.get(
                self.health_api(),
                timeout=self.timeout
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            responses.append(response.json())
            time.sleep(0.1)  # Small delay between requests

        # All responses should have the same status
        statuses = [r.get(CommonFields.STATUS) for r in responses if CommonFields.STATUS in r]
        assert len(statuses) > 0, "No status fields found in responses"
        assert len(set(statuses)) == 1, f"Health status inconsistent: {statuses}"

        # All responses should have the same service name
        services = [r.get(CommonFields.SERVICE) for r in responses if CommonFields.SERVICE in r]
        assert len(services) > 0, "No service fields found in responses"
        assert len(set(services)) == 1, f"Service name inconsistent: {services}"

    def test_health_performance(self):
        """Test that health endpoint responds within reasonable time"""

        start_time = time.time()
        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )
        end_time = time.time()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 500, f"Response time {response_time:.2f}ms exceeds 500ms threshold"

    def test_health_with_query_parameters(self):
        """Test that health endpoint handles query parameters gracefully"""
        # Test common health check params
        params = {OrderFields.FORMAT: CommonFields.JSON, OrderFields.DETAILED: CommonFields.TRUE, OrderFields.INCLUDE_METRICS: CommonFields.TRUE}

        response = self.session.get(
            self.health_api(),
            params=params,
            timeout=self.timeout
        )

        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert response.status_code in [200, 400, 422], f"Unexpected status code {response.status_code} for query params"


    def test_health_methods(self):
        """Test that health endpoint only accepts GET method"""
        # Test POST method (should not be allowed)
        response = self.session.post(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for POST, got {response.status_code}"
        # Test PUT method (should not be allowed)
        response = self.session.put(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for PUT, got {response.status_code}"
        # Test DELETE method (should not be allowed)
        response = self.session.delete(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for DELETE, got {response.status_code}"

    def test_health_headers(self):
        """Test that health endpoint returns appropriate headers"""

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Check for common headers
        headers = response.headers

        # Content-Type header should be JSON
        assert "content-type" in headers, "Missing Content-Type header"
        content_type = headers["content-type"]
        assert "application/json" in content_type, f"Expected JSON content type, got {content_type}"

    def run_all_health_tests(self):
        """Run all health check tests"""
        self.test_health_endpoint_accessible()
        self.test_health_response_schema()
        self.test_health_response_consistency()
        self.test_health_performance()
        self.test_health_with_query_parameters()
        self.test_health_methods()
        self.test_health_headers()


if __name__ == "__main__":
    tests = HealthTests()
    tests.run_all_health_tests()
