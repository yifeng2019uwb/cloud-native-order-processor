#!/usr/bin/env python3
"""
API Gateway Integration Test Runner
Tests the production-like API Gateway + Lambda setup
"""
import sys
import os
import yaml
import time
import requests
from datetime import datetime
from typing import Dict, Any

class APIGatewayTestRunner:
    """Test runner for API Gateway + Lambda setup"""

    def __init__(self, config_file: str = "config/services.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.api_gateway_url = self._get_api_gateway_url()
        self.session = requests.Session()
        self.test_results = []

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded configuration from {self.config_file}")
            return config
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return {}

    def _get_api_gateway_url(self) -> str:
        """Get API Gateway URL from config or environment"""
        api_url = os.getenv('API_GATEWAY_URL')
        if api_url:
            return api_url

        if self.config and 'api_gateway' in self.config:
            env = os.getenv('ENVIRONMENT', 'dev')
            if env in self.config['api_gateway']:
                return self.config['api_gateway'][env]['base_url']

        return "https://gsgy1f1cmi.execute-api.us-west-2.amazonaws.com/dev"

    def run_smoke_tests(self) -> list:
        """Run smoke tests (health checks)"""
        print("\n" + "="*60)
        print("🏥 SMOKE TESTS - Basic Connectivity")
        print("="*60)

        tests = [
            self._test_endpoint("/health", "GET", "API Gateway Health Check"),
            self._test_endpoint("/", "GET", "API Gateway Root Endpoint"),
            self._test_endpoint("/info", "GET", "API Gateway Info Endpoint"),
            self._test_endpoint("/test", "GET", "API Gateway Test Endpoint")
        ]

        for test in tests:
            self.test_results.append(test)
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']:.2f}ms")
            if not test['success']:
                print(f"    Error: {test['error']}")

        return tests

    def run_user_service_tests(self) -> list:
        """Run user service tests against API Gateway"""
        print("\n" + "="*60)
        print("👤 USER SERVICE TESTS - API Gateway")
        print("="*60)

        tests = [
            self._test_endpoint("/auth/register", "POST", "User Registration",
                              json_data={"username": "test_user", "password": "test_pass", "email": "test@example.com"}),
            self._test_endpoint("/auth/login", "POST", "User Login",
                              json_data={"username": "test_user", "password": "test_pass"}),
            self._test_endpoint("/auth/profile", "GET", "User Profile")
        ]

        for test in tests:
            self.test_results.append(test)
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']:.2f}ms")
            if not test['success']:
                print(f"    Error: {test['error']}")

        return tests

    def run_inventory_service_tests(self) -> list:
        """Run inventory service tests against API Gateway"""
        print("\n" + "="*60)
        print("📦 INVENTORY SERVICE TESTS - API Gateway")
        print("="*60)

        tests = [
            self._test_endpoint("/assets", "GET", "Get All Assets"),
            self._test_endpoint("/assets?category=electronics", "GET", "Get Assets by Category"),
            self._test_endpoint("/assets/asset-1", "GET", "Get Asset by ID"),
            self._test_endpoint("/categories", "GET", "Get All Categories"),
            self._test_endpoint("/assets", "POST", "Create Asset",
                              json_data={"name": "Test Asset", "category": "electronics"})
        ]

        for test in tests:
            self.test_results.append(test)
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']:.2f}ms")
            if not test['success']:
                print(f"    Error: {test['error']}")

        return tests

    def _test_endpoint(self, path: str, method: str, test_name: str, json_data: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        start_time = time.time()
        url = f"{self.api_gateway_url}{path}"

        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=json_data, timeout=10)
            else:
                return {
                    'test_name': test_name,
                    'success': False,
                    'duration': time.time() - start_time,
                    'status_code': None,
                    'error': f"Unsupported method: {method}"
                }

            duration = time.time() - start_time
            success = response.status_code in [200, 201]

            return {
                'test_name': test_name,
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200/201, got {response.status_code}",
                'url': url,
                'method': method
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': test_name,
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'url': url,
                'method': method
            }

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "="*60)
        print("📊 API GATEWAY TEST SUMMARY")
        print("="*60)
        print(f"🎯 API Gateway: {self.api_gateway_url}")
        print(f"⏰ Test Time: {datetime.utcnow().isoformat()}")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")

        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  - {test['test_name']}: {test['error']}")

        overall_result = "✅ PASS" if passed_tests == total_tests else "❌ FAIL"
        print(f"\n🎯 Overall Result: {overall_result}")

        return passed_tests == total_tests

    def run_all_tests(self) -> bool:
        """Run all API Gateway tests"""
        start_time = time.time()

        print("🚀 API GATEWAY INTEGRATION TEST RUNNER")
        print("="*60)
        print(f"🎯 API Gateway: {self.api_gateway_url}")
        print(f"⏰ Started: {datetime.utcnow().isoformat()}")
        print("="*60)

        try:
            # Run all test suites
            self.run_smoke_tests()
            self.run_user_service_tests()
            self.run_inventory_service_tests()

            # Generate summary
            success = self.generate_summary()
            print(f"\n⏱️  Total Duration: {time.time() - start_time:.2f}s")

            return success

        except Exception as e:
            print(f"\n❌ Test runner failed: {e}")
            return False

def main():
    """Main entry point"""
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML not found. Install with: pip install PyYAML")
        sys.exit(1)

    runner = APIGatewayTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()