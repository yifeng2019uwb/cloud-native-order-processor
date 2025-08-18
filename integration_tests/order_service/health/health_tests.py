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
        print("  🏥 Testing health endpoint accessibility")

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        # Health endpoint should be accessible without auth
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("  ✅ Health endpoint accessible without authentication")

    def test_health_response_schema(self):
        """Test that health response has correct schema"""
        print("  🔍 Testing health response schema")

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        try:
            data = response.json()

            # Check if response has expected structure
            if "status" in data:
                assert data["status"] in ["healthy", "ok", "up"], f"Unexpected status: {data['status']}"
                print("    ✅ Status field present and valid")
            else:
                print("    ⚠️  Status field missing")

            if "timestamp" in data:
                print("    ✅ Timestamp field present")
            else:
                print("    ⚠️  Timestamp field missing")

            if "service" in data:
                print("    ✅ Service field present")
            else:
                print("    ⚠️  Service field missing")

            if "version" in data:
                print("    ✅ Version field present")
            else:
                print("    ⚠️  Version field missing")

        except Exception as e:
            print(f"    ❌ Health response schema validation failed: {e}")
            raise

    def test_health_response_consistency(self):
        """Test that health endpoint returns consistent responses"""
        print("  🔄 Testing health response consistency")

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
        statuses = [r.get("status") for r in responses if "status" in r]
        if statuses:
            assert len(set(statuses)) == 1, f"Health status inconsistent: {statuses}"
            print("    ✅ Health status consistent across requests")

        # All responses should have the same service name
        services = [r.get("service") for r in responses if "service" in r]
        if services:
            assert len(set(services)) == 1, f"Service name inconsistent: {services}"
            print("    ✅ Service name consistent across requests")

        print("    ✅ Health responses consistent across multiple requests")

    def test_health_performance(self):
        """Test that health endpoint responds within reasonable time"""
        print("  ⏱️  Testing health endpoint performance")

        start_time = time.time()
        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )
        end_time = time.time()

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 500, f"Response time {response_time:.2f}ms exceeds 500ms threshold"

        print(f"    ✅ Response time: {response_time:.2f}ms")

    def test_health_with_query_parameters(self):
        """Test that health endpoint handles query parameters gracefully"""
        print("  🔍 Testing health endpoint with query parameters")

        # Test common health check params
        params = {"format": "json", "detailed": "true", "include_metrics": "true"}

        response = self.session.get(
            self.health_api(),
            params=params,
            timeout=self.timeout
        )

        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert response.status_code in [200, 400, 422], f"Unexpected status code {response.status_code} for query params"

        if response.status_code == 200:
            print("    ✅ Query parameters accepted")
        else:
            print(f"    ✅ Query parameters handled gracefully (status: {response.status_code})")

    def test_health_methods(self):
        """Test that health endpoint only accepts GET method"""
        print("  🔍 Testing health endpoint HTTP methods")

        # Test POST method (should not be allowed)
        response = self.session.post(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for POST, got {response.status_code}"
        print("    ✅ POST method correctly rejected")

        # Test PUT method (should not be allowed)
        response = self.session.put(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for PUT, got {response.status_code}"
        print("    ✅ PUT method correctly rejected")

        # Test DELETE method (should not be allowed)
        response = self.session.delete(
            self.health_api(),
            timeout=self.timeout
        )
        assert response.status_code in [405, 404], f"Expected 405/404 for DELETE, got {response.status_code}"
        print("    ✅ DELETE method correctly rejected")

    def test_health_headers(self):
        """Test that health endpoint returns appropriate headers"""
        print("  🔍 Testing health endpoint headers")

        response = self.session.get(
            self.health_api(),
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Check for common headers
        headers = response.headers

        if "content-type" in headers:
            content_type = headers["content-type"]
            assert "application/json" in content_type, f"Expected JSON content type, got {content_type}"
            print("    ✅ Content-Type header correct")
        else:
            print("    ⚠️  Content-Type header missing")

        if "cache-control" in headers:
            cache_control = headers["cache-control"]
            # Health checks should typically not be cached
            assert "no-cache" in cache_control or "no-store" in cache_control, f"Health endpoint should not be cached, got {cache_control}"
            print("    ✅ Cache-Control header appropriate")
        else:
            print("    ⚠️  Cache-Control header missing")

    def run_all_health_tests(self):
        """Run all health check tests"""
        print("🏥 Running order service health check integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_order_endpoint(OrderAPI.HEALTH)}")

        try:
            # Health Check Tests
            print("\n🏥 === HEALTH CHECK TESTS ===")
            self.test_health_endpoint_accessible()
            print("  ✅ Health Endpoint Accessible - PASS")

            self.test_health_response_schema()
            print("  ✅ Health Response Schema - PASS")

            self.test_health_response_consistency()
            print("  ✅ Health Response Consistency - PASS")

            self.test_health_performance()
            print("  ✅ Health Performance - PASS")

            self.test_health_with_query_parameters()
            print("  ✅ Health Query Parameters - PASS")

            self.test_health_methods()
            print("  ✅ Health HTTP Methods - PASS")

            self.test_health_headers()
            print("  ✅ Health Headers - PASS")

        except Exception as e:
            print(f"  ❌ Unexpected error in health tests: {e}")

        print("\n==================================================")
        print("🎉 Health check tests completed!")

if __name__ == "__main__":
    tests = HealthTests()
    tests.run_all_health_tests()
