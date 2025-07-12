"""
Inventory Service Integration Tests
Tests asset management, categories, and inventory operations
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from simple_retry import simple_retry
from test_data import TestDataManager

class InventoryServiceTests:
    """Integration tests for inventory service"""

    def __init__(self, inventory_service_url: str, timeout: int = 10):
        self.inventory_service_url = inventory_service_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_assets = []

    def test_get_assets(self) -> Dict[str, Any]:
        """Test getting all assets"""
        start_time = time.time()

        def get_assets():
            return self.session.get(
                f"{self.inventory_service_url}/assets",
                timeout=self.timeout
            )

        try:
            response = simple_retry(get_assets)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Get All Assets',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'inventory-service',
                'test_data': None
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'Get All Assets',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'test_data': None
            }

    def test_get_assets_by_category(self) -> Dict[str, Any]:
        """Test getting assets filtered by category"""
        start_time = time.time()

        # Test with a common category
        category = "electronics"

        def get_assets_by_category():
            return self.session.get(
                f"{self.inventory_service_url}/assets?category={category}",
                timeout=self.timeout
            )

        try:
            response = simple_retry(get_assets_by_category)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': f'Get Assets by Category ({category})',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'inventory-service',
                'test_data': category
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': f'Get Assets by Category ({category})',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'test_data': category
            }

    def test_get_asset_by_id(self) -> Dict[str, Any]:
        """Test getting a specific asset by ID"""
        start_time = time.time()

        # First get all assets to find an ID to test with
        try:
            response = self.session.get(f"{self.inventory_service_url}/assets", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                if assets:
                    asset_id = assets[0].get('id')
                    if asset_id:
                        def get_asset_by_id():
                            return self.session.get(
                                f"{self.inventory_service_url}/assets/{asset_id}",
                                timeout=self.timeout
                            )

                        response = simple_retry(get_asset_by_id)
                        duration = time.time() - start_time

                        success = response.status_code == 200
                        data = response.json() if success else {}

                        return {
                            'test_name': f'Get Asset by ID ({asset_id})',
                            'success': success,
                            'duration': duration,
                            'status_code': response.status_code,
                            'error': None if success else f"Expected 200, got {response.status_code}",
                            'service': 'inventory-service',
                            'test_data': asset_id
                        }
        except Exception as e:
            pass

        # If no assets found or error occurred
        duration = time.time() - start_time
        return {
            'test_name': 'Get Asset by ID',
            'success': False,
            'duration': duration,
            'status_code': None,
            'error': 'No assets available for testing',
            'service': 'inventory-service',
            'test_data': None
        }

    def test_get_categories(self) -> Dict[str, Any]:
        """Test getting all categories"""
        start_time = time.time()

        def get_categories():
            return self.session.get(
                f"{self.inventory_service_url}/categories",
                timeout=self.timeout
            )

        try:
            response = simple_retry(get_categories)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'Get All Categories',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'inventory-service',
                'test_data': None
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'Get All Categories',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'test_data': None
            }

    def test_create_asset(self) -> Dict[str, Any]:
        """Test creating a new asset with UUID-based data"""
        start_time = time.time()

        # Generate unique test asset data
        asset_data = self.test_data_manager.generate_asset_data()
        self.created_assets.append(asset_data)

        def create_asset():
            return self.session.post(
                f"{self.inventory_service_url}/assets",
                json=asset_data,
                timeout=self.timeout
            )

        try:
            response = simple_retry(create_asset)
            duration = time.time() - start_time

            success = response.status_code == 201
            data = response.json() if success else {}

            return {
                'test_name': 'Create Asset',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 201, got {response.status_code}",
                'service': 'inventory-service',
                'test_data': asset_data['test_id']
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'Create Asset',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'inventory-service',
                'test_data': asset_data['test_id']
            }

    def cleanup_test_assets(self):
        """Clean up test assets (placeholder for future implementation)"""
        print(f"🧹 Cleanup: {len(self.created_assets)} test assets marked for cleanup")
        # TODO: Implement actual cleanup when inventory service supports asset deletion
        self.created_assets = []

    def run_all_inventory_tests(self) -> list:
        """Run all inventory service tests"""
        print("📦 Running inventory service tests...")

        tests = [
            self.test_get_assets(),
            self.test_get_assets_by_category(),
            self.test_get_asset_by_id(),
            self.test_get_categories(),
            self.test_create_asset()
        ]

        # Print results
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']*1000:.2f}ms")
            if test['error']:
                print(f"    Error: {test['error']}")

        # Cleanup test data
        self.cleanup_test_assets()

        return tests