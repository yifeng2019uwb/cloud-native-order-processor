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
from test_constants import InventoryFields, TestValues, CommonFields

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
        assert InventoryFields.ASSETS in r.json()
        assert any(a.get(InventoryFields.ASSET_ID) == TestValues.BTC_ASSET_ID for a in r.json()[InventoryFields.ASSETS])

    def test_get_asset_by_id(self):
        """Test getting a specific asset by ID"""
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, TestValues.BTC_ASSET_ID), timeout=self.timeout)
        assert r.status_code == 200
        data = r.json()
        assert data.get(InventoryFields.ASSET_ID) == TestValues.BTC_ASSET_ID
        assert InventoryFields.NAME in data

    def test_get_nonexistent_asset(self):
        """Test getting a non-existent asset returns 422 (validation error)"""
        # "UNKNOWN_ASSET" is 13 characters, which exceeds the 1-10 character limit
        # Field validation happens before business logic, so malformed IDs fail validation first
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, "UNKNOWN_ASSET"), timeout=self.timeout)
        assert r.status_code == 422, f"Expected 422 for invalid asset ID format, got {r.status_code}"

    def test_invalid_asset_id_formats(self):
        """Test various invalid asset ID formats"""
        invalid_ids = ["   ", "BTC!", "BTC@123", "A" * 100]  # Whitespace, special chars, too long

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
        assert InventoryFields.ASSETS in data
        assert isinstance(data[InventoryFields.ASSETS], list)
        assert len(data[InventoryFields.ASSETS]) > 0, "Assets list should not be empty"

        asset = data[InventoryFields.ASSETS][0]
        # Check required fields exist
        assert asset.get(InventoryFields.ASSET_ID) is not None, f"Missing {InventoryFields.ASSET_ID}"
        assert asset.get(InventoryFields.NAME) is not None, f"Missing {InventoryFields.NAME}"
        assert asset.get(InventoryFields.CATEGORY) is not None, f"Missing {InventoryFields.CATEGORY}"
        assert asset.get(InventoryFields.PRICE_USD) is not None, f"Missing {InventoryFields.PRICE_USD}"
        assert asset.get(InventoryFields.IS_ACTIVE) is not None, f"Missing {InventoryFields.IS_ACTIVE}"

        # Check data types
        assert isinstance(asset[InventoryFields.ASSET_ID], str)
        assert isinstance(asset[InventoryFields.NAME], str)
        assert isinstance(asset[InventoryFields.PRICE_USD], (int, float))
        assert asset[InventoryFields.PRICE_USD] >= 0, "Price should be non-negative"
        assert isinstance(asset[InventoryFields.IS_ACTIVE], bool)

    def test_asset_consistency(self):
        """Test that two sequential requests return consistent data"""
        r1 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        r2 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)

        assert r1.status_code == 200
        assert r2.status_code == 200

        data1 = r1.json()
        data2 = r2.json()

        # Asset count should be consistent
        assert len(data1[InventoryFields.ASSETS]) == len(data2[InventoryFields.ASSETS])

        # BTC should exist in both responses
        btc_in_r1 = any(a.get(InventoryFields.ASSET_ID) == TestValues.BTC_ASSET_ID for a in data1[InventoryFields.ASSETS])
        btc_in_r2 = any(a.get(InventoryFields.ASSET_ID) == TestValues.BTC_ASSET_ID for a in data2[InventoryFields.ASSETS])
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
        params = {CommonFields.LIMIT: "10", CommonFields.OFFSET: "0", CommonFields.PAGE: "1", CommonFields.SORT: "name"}

        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), params=params, timeout=self.timeout)
        # Should either accept params (200) or reject them gracefully (400/422), but not crash (500)
        assert r.status_code in [200, 400, 422], f"Unexpected status code {r.status_code} for unsupported params"

    def cleanup_test_assets(self):
        """Clean up test assets (placeholder for future implementation)"""
        # TODO: Implement actual cleanup when inventory service supports asset deletion
        self.created_assets = []

    def run_all_inventory_tests(self):
        """Run all inventory tests"""
        self.test_get_assets()
        self.test_get_asset_by_id()
        self.test_get_nonexistent_asset()
        self.test_invalid_asset_id_formats()
        self.test_asset_schema_validation()
        self.test_asset_consistency()
        self.test_performance_guard()
        self.test_unsupported_query_params()
        self.cleanup_test_assets()

if __name__ == "__main__":
    tests = InventoryServiceTests(APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSETS).replace("/assets", ""))
    tests.run_all_inventory_tests()