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
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_retry import simple_retry
from test_data import TestDataManager
from api_endpoints import APIEndpoints, InventoryAPI

class InventoryServiceTests:
    """Integration tests for inventory service"""

    def __init__(self, inventory_service_url: str, timeout: int = 10):
        self.inventory_service_url = inventory_service_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_assets = []

    def inventory_api(self, endpoint: str) -> str:
        """Helper method to build inventory service API URLs"""
        return APIEndpoints.get_inventory_endpoint(endpoint)

    def inventory_api_with_id(self, endpoint: str, asset_id: str) -> str:
        """Helper method to build inventory service API URLs with asset ID"""
        return APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSET_BY_ID, id=asset_id)

    def test_get_assets(self):
        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        assert r.status_code == 200
        assert "assets" in r.json()
        assert any(a.get("asset_id") == "BTC" for a in r.json()["assets"])

    def test_get_asset_by_id(self):
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, "BTC"), timeout=self.timeout)
        assert r.status_code == 200
        data = r.json()
        assert data.get("asset_id") == "BTC"
        assert "name" in data

    def cleanup_test_assets(self):
        """Clean up test assets (placeholder for future implementation)"""
        print(f"🧹 Cleanup: {len(self.created_assets)} test assets marked for cleanup")
        # TODO: Implement actual cleanup when inventory service supports asset deletion
        self.created_assets = []

    def run_all_inventory_tests(self):
        print("📦 Running inventory service tests...")
        tests = [
            ("Get All Assets", self.test_get_assets),
            ("Get Asset by ID", self.test_get_asset_by_id),
        ]
        passed = 0
        failed = 0
        for name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ PASS {name}")
                passed += 1
            except AssertionError as e:
                print(f"  ❌ FAIL {name}")
                print(f"    Error: {e}")
                failed += 1
            except Exception as e:
                print(f"  ❌ FAIL {name}")
                print(f"    Unexpected error: {e}")
                failed += 1
        self.cleanup_test_assets()
        print("\n==================================================")
        print(f"✅ Passed: {passed}/{len(tests)}")
        print(f"❌ Failed: {failed}/{len(tests)}")
        if failed == 0:
            print("🎉 All inventory tests passed!")
        else:
            print("⚠️  Some tests failed")

if __name__ == "__main__":
    tests = InventoryServiceTests(APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSETS).replace("/assets", ""))
    tests.test_get_assets()
    tests.test_get_asset_by_id()
    print("All direct assertions passed.")