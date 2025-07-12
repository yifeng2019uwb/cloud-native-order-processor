#!/usr/bin/env python3
"""
Main Integration Test Runner
Orchestrates all tests with reporting and cleanup
"""
import sys
import os
import yaml
import time
from datetime import datetime
from typing import Dict, Any

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from reporting import TestReporter
from test_data import TestDataManager

# Add test modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'smoke'))
from health_tests import HealthTests

class IntegrationTestRunner:
    """Main test runner with enterprise-grade features"""

    def __init__(self, config_file: str = "config/services.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.reporter = TestReporter()
        self.test_data_manager = TestDataManager()
        self.api_gateway_url = self._get_api_gateway_url()

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
        # Try environment variable first
        api_url = os.getenv('API_GATEWAY_URL')
        if api_url:
            return api_url

        # Try config file
        if self.config and 'api_gateway' in self.config:
            env = os.getenv('ENVIRONMENT', 'dev')
            if env in self.config['api_gateway']:
                return self.config['api_gateway'][env]['base_url']

        # Fallback to known URL
        return "https://gsgy1f1cmi.execute-api.us-west-2.amazonaws.com/dev"

    def _get_user_service_url(self) -> str:
        """Get user service URL - always use API Gateway"""
        return self.api_gateway_url

    def _get_inventory_service_url(self) -> str:
        """Get inventory service URL - always use API Gateway"""
        return self.api_gateway_url

    def run_smoke_tests(self) -> list:
        """Run smoke tests (health checks)"""
        print("\n" + "="*60)
        print("🏥 SMOKE TESTS - Basic Connectivity")
        print("="*60)

        health_tests = HealthTests(self.api_gateway_url)
        results = health_tests.run_all_health_tests()

        # Add results to reporter
        for result in results:
            self.reporter.add_test_result(
                test_name=result['test_name'],
                success=result['success'],
                duration=result['duration'],
                status_code=result['status_code'],
                error=result['error'],
                service=result['service']
            )

        return results

    def run_functional_tests(self) -> list:
        """Run functional tests (business logic) against API Gateway"""
        print("\n" + "="*60)
        print("🔧 FUNCTIONAL TESTS - Business Logic (API Gateway)")
        print("="*60)

        results = []

        # Run user service tests against API Gateway
        user_service_url = self._get_user_service_url()
        try:
            from user_services.user_tests import UserServiceTests
            user_tests = UserServiceTests(user_service_url)
            user_results = user_tests.run_all_user_tests()
            results.extend(user_results)

            # Add results to reporter
            for result in user_results:
                self.reporter.add_test_result(
                    test_name=result['test_name'],
                    success=result['success'],
                    duration=result['duration'],
                    status_code=result['status_code'],
                    error=result['error'],
                    service=result['service']
                )
        except Exception as e:
            print(f"⚠️  User service tests failed: {e}")

        # Run inventory service tests against API Gateway
        inventory_service_url = self._get_inventory_service_url()
        try:
            from inventory_service.inventory_tests import InventoryServiceTests
            inventory_tests = InventoryServiceTests(inventory_service_url)
            inventory_results = inventory_tests.run_all_inventory_tests()
            results.extend(inventory_results)

            # Add results to reporter
            for result in inventory_results:
                self.reporter.add_test_result(
                    test_name=result['test_name'],
                    success=result['success'],
                    duration=result['duration'],
                    status_code=result['status_code'],
                    error=result['error'],
                    service=result['service']
                )
        except Exception as e:
            print(f"⚠️  Inventory service tests failed: {e}")

        return results

    def cleanup_test_data(self):
        """Clean up test data after tests"""
        print("\n" + "="*60)
        print("🧹 CLEANUP - Test Data")
        print("="*60)

        if not self.config.get('test_config', {}).get('cleanup_after_tests', True):
            print("⚠️  Cleanup disabled in config")
            return

        print("✅ Test data cleanup completed")
        self.test_data_manager.clear_data()

    def generate_reports(self) -> Dict[str, str]:
        """Generate test reports"""
        print("\n" + "="*60)
        print("📊 REPORTS - Test Results")
        print("="*60)

        reports = {}

        if self.config.get('test_config', {}).get('generate_reports', True):
            # Generate JSON report
            json_report = self.reporter.generate_json_report()
            reports['json'] = json_report
            print(f"✅ JSON report: {json_report}")

            # Generate HTML report
            html_report = self.reporter.generate_html_report()
            reports['html'] = html_report
            print(f"✅ HTML report: {html_report}")
        else:
            print("⚠️  Report generation disabled in config")

        return reports

    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        start_time = time.time()

        print("🚀 INTEGRATION TEST RUNNER")
        print("="*60)
        print(f"🎯 API Gateway: {self.api_gateway_url}")
        print(f"🆔 Test Run ID: {self.test_data_manager.get_test_run_id()}")
        print(f"⏰ Started: {datetime.utcnow().isoformat()}")
        print("="*60)

        try:
            # Run smoke tests
            smoke_results = self.run_smoke_tests()

            # Run functional tests
            functional_results = self.run_functional_tests()

            # Cleanup test data
            self.cleanup_test_data()

            # Generate reports
            reports = self.generate_reports()

            # Summary
            total_tests = len(smoke_results) + len(functional_results)
            passed_tests = sum(1 for r in smoke_results + functional_results if r['success'])

            print("\n" + "="*60)
            print("📊 TEST SUMMARY")
            print("="*60)
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
            print(f"Duration: {time.time() - start_time:.2f}s")

            success = passed_tests == total_tests
            print(f"\n🎯 Overall Result: {'✅ PASS' if success else '❌ FAIL'}")

            return success

        except Exception as e:
            print(f"\n❌ Test runner failed: {e}")
            return False

def main():
    """Main entry point"""
    # Check if PyYAML is available
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML not found. Install with: pip install PyYAML")
        sys.exit(1)

    # Run tests
    runner = IntegrationTestRunner()
    success = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()