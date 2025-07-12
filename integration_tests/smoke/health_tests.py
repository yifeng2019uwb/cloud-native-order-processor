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
from simple_retry import simple_retry

class HealthTests:
    """Smoke tests for service connectivity"""

    def __init__(self, api_gateway_url: str, timeout: int = 10):
        self.api_gateway_url = api_gateway_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def test_api_gateway_health(self) -> Dict[str, Any]:
        """Test API Gateway health endpoint"""
        start_time = time.time()

        def health_check():
            return self.session.get(f"{self.api_gateway_url}/health", timeout=self.timeout)

        try:
            response = simple_retry(health_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'API Gateway Health Check',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'api-gateway'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'API Gateway Health Check',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'api-gateway'
            }

    def test_api_gateway_root(self) -> Dict[str, Any]:
        """Test API Gateway root endpoint"""
        start_time = time.time()

        def root_check():
            return self.session.get(f"{self.api_gateway_url}/", timeout=self.timeout)

        try:
            response = simple_retry(root_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'API Gateway Root Endpoint',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'api-gateway'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'API Gateway Root Endpoint',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'api-gateway'
            }

    def test_api_gateway_info(self) -> Dict[str, Any]:
        """Test API Gateway info endpoint"""
        start_time = time.time()

        def info_check():
            return self.session.get(f"{self.api_gateway_url}/info", timeout=self.timeout)

        try:
            response = simple_retry(info_check)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'API Gateway Info Endpoint',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'api-gateway'
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'API Gateway Info Endpoint',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'api-gateway'
            }

    def run_all_health_tests(self) -> list:
        """Run all health tests"""
        print("🏥 Running smoke tests (health checks)...")

        tests = [
            self.test_api_gateway_health(),
            self.test_api_gateway_root(),
            self.test_api_gateway_info()
        ]

        # Print results
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']*1000:.2f}ms")
            if test['error']:
                print(f"    Error: {test['error']}")

        return tests