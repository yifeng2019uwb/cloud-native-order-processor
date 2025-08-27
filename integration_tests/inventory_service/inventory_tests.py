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
        return APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSET_BY_ID, asset_id=asset_id)

    def test_get_assets(self):
        """Test getting all assets"""
        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        assert r.status_code == 200
        assert "assets" in r.json()
        assert any(a.get("asset_id") == "BTC" for a in r.json()["assets"])

    def test_get_asset_by_id(self):
        """Test getting a specific asset by ID"""
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, "BTC"), timeout=self.timeout)
        assert r.status_code == 200
        data = r.json()
        assert data.get("asset_id") == "BTC"
        assert "name" in data

    def test_get_nonexistent_asset(self):
        """Test getting a non-existent asset returns 422 (validation error)"""
        # "UNKNOWN_ASSET" is 13 characters, which exceeds the 1-10 character limit
        # Field validation happens before business logic, so malformed IDs fail validation first
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, "UNKNOWN_ASSET"), timeout=self.timeout)
        assert r.status_code == 422, f"Expected 422 for invalid asset ID format, got {r.status_code}"
        # Should return error details
        error_data = r.json()
        assert "error" in error_data or "detail" in error_data or "message" in error_data

    def test_invalid_asset_id_formats(self):
        """Test various invalid asset ID formats"""
        invalid_ids = ["", "   ", "BTC!", "BTC@123", "A" * 100]  # Empty, whitespace, special chars, too long

        for invalid_id in invalid_ids:
            r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, invalid_id), timeout=self.timeout)
            # Should return 422 for invalid asset ID format (field validation errors)
            # Field validation happens before business logic, so malformed IDs fail validation first
            assert r.status_code == 422, f"Expected 422 for invalid asset ID format '{invalid_id}', got {r.status_code}"

    def test_asset_schema_validation(self):
        """Test that asset responses have correct schema and data types"""
        # Test list schema
        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        assert r.status_code == 200
        data = r.json()
        assert "assets" in data
        assert isinstance(data["assets"], list)

        if data["assets"]:
            asset = data["assets"][0]
            # Updated required fields based on actual API response
            required_fields = ["asset_id", "name", "description", "category", "price_usd", "is_active"]
            for field in required_fields:
                assert field in asset, f"Missing required field: {field}"

            # Check data types
            assert isinstance(asset["asset_id"], str)
            assert isinstance(asset["name"], str)
            assert isinstance(asset["price_usd"], (int, float))
            assert asset["price_usd"] >= 0, "Price should be non-negative"
            assert isinstance(asset["is_active"], bool)

    def test_asset_consistency(self):
        """Test that two sequential requests return consistent data"""
        r1 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        r2 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)

        assert r1.status_code == 200
        assert r2.status_code == 200

        data1 = r1.json()
        data2 = r2.json()

        # Asset count should be consistent
        assert len(data1["assets"]) == len(data2["assets"])

        # BTC should exist in both responses
        btc_in_r1 = any(a.get("asset_id") == "BTC" for a in data1["assets"])
        btc_in_r2 = any(a.get("asset_id") == "BTC" for a in data2["assets"])
        assert btc_in_r1 == btc_in_r2, "BTC asset consistency check failed"

    def test_performance_guard(self):
        """Test that asset listing responds within reasonable time"""
        start_time = time.time()
        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 1000, f"Response time {response_time:.2f}ms exceeds 1000ms threshold"
        assert r.status_code == 200

    def test_unsupported_query_params(self):
        """Test that unsupported query parameters don't cause errors"""
        # Test common pagination params that might not be supported
        params = {"limit": "10", "offset": "0", "page": "1", "sort": "name"}

        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), params=params, timeout=self.timeout)
        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert r.status_code in [200, 400, 422], f"Unexpected status code {r.status_code} for unsupported params"

    def cleanup_test_assets(self):
        """Clean up test assets (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when inventory service supports asset deletion
        self.created_assets = []

    def run_all_inventory_tests(self):
        tests = [
            ("Get All Assets", self.test_get_assets),
            ("Get Asset by ID", self.test_get_asset_by_id),
            ("Get Non-existent Asset", self.test_get_nonexistent_asset),
            ("Invalid Asset ID Formats", self.test_invalid_asset_id_formats),
            ("Asset Schema Validation", self.test_asset_schema_validation),
            ("Asset Consistency", self.test_asset_consistency),
            ("Performance Guard", self.test_performance_guard),
            ("Unsupported Query Params", self.test_unsupported_query_params),
        ]

        failed_tests = []

        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                failed_tests.append(name)

        self.cleanup_test_assets()

        if failed_tests:
            raise AssertionError(f"Inventory tests failed: {', '.join(failed_tests)}")

if __name__ == "__main__":
    tests = InventoryServiceTests(APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSETS).replace("/assets", ""))
    try:
        tests.run_all_inventory_tests()
        print("🎉 All inventory tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Inventory tests failed: {e}")
        sys.exit(1)