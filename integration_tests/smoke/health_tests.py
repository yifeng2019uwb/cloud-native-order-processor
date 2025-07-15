"""
Smoke tests for basic connectivity
Tests service health endpoints
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_retry import simple_retry
from api_endpoints import APIEndpoints, UserAPI, InventoryAPI

class HealthTests:
    """Smoke tests for service connectivity"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def test_user_service_health(self) -> Dict[str, Any]:
        """Test User Service health endpoint"""
        start_time = time.time()

        def health_check():
            return self.session.get(APIEndpoints.get_user_endpoint(UserAPI.HEALTH), timeout=self.timeout)

        try:
            response = simple_retry(health_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'User Service Health Check',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'user-service',
                'data': data
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'User Service Health Check',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'user-service',
                'data': {}
            }

    def test_inventory_service_health(self) -> Dict[str, Any]:
        """Test Inventory Service health endpoint"""
        start_time = time.time()

        def health_check():
            return self.session.get(APIEndpoints.get_inventory_endpoint(InventoryAPI.HEALTH), timeout=self.timeout)

        try:
            response = simple_retry(health_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Inventory Service Health Check',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'inventory-service',
                'data': data
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'Inventory Service Health Check',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'data': {}
            }

    def test_user_service_root(self) -> Dict[str, Any]:
        """Test User Service root endpoint"""
        start_time = time.time()

        def root_check():
            return self.session.get(APIEndpoints.get_user_endpoint(UserAPI.ROOT), timeout=self.timeout)

        try:
            response = simple_retry(root_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'User Service Root Endpoint',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'user-service',
                'data': data
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'User Service Root Endpoint',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'user-service',
                'data': {}
            }

    def test_inventory_service_root(self) -> Dict[str, Any]:
        """Test Inventory Service root endpoint"""
        start_time = time.time()

        def root_check():
            return self.session.get(APIEndpoints.get_inventory_endpoint(InventoryAPI.ROOT), timeout=self.timeout)

        try:
            response = simple_retry(root_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Inventory Service Root Endpoint',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'inventory-service',
                'data': data
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'Inventory Service Root Endpoint',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'data': {}
            }

    def run_all_health_tests(self) -> list:
        """Run all health tests"""
        print("🏥 Running smoke tests (health checks)...")

        tests = [
            self.test_user_service_health(),
            self.test_inventory_service_health(),
            self.test_user_service_root(),
            self.test_inventory_service_root()
        ]

        # Print results
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']*1000:.2f}ms")
            if test['error']:
                print(f"    Error: {test['error']}")
            if test['success'] and test['data']:
                print(f"    Service: {test['data'].get('service', 'Unknown')}")

        return tests

if __name__ == "__main__":
    # Run smoke tests
    health_tests = HealthTests()
    results = health_tests.run_all_health_tests()

    # Summary
    passed = sum(1 for test in results if test['success'])
    total = len(results)
    print(f"\n📊 Smoke Test Summary: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All smoke tests passed!")
    else:
        print("⚠️  Some smoke tests failed. Check service connectivity.")