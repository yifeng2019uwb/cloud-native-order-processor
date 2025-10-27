"""
Inventory Service Integration Tests
Tests asset management, categories, and inventory operations
"""
import requests
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_retry import simple_retry
from api_endpoints import APIEndpoints, InventoryAPI
from test_constants import InventoryFields, TestValues, CommonFields

# Import service models directly from files to avoid __init__.py dependency chain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'inventory_service', 'src'))

# Import directly from files to bypass __init__.py that triggers dependency imports
import importlib.util
spec = importlib.util.spec_from_file_location(
    "data_models",
    os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'inventory_service', 'src', 'api_models', 'shared', 'data_models.py')
)
data_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_models)

AssetData = data_models.AssetData
AssetDetailData = data_models.AssetDetailData

# Create response wrappers using service data models
from pydantic import BaseModel
from typing import List

class ListAssetsResponse(BaseModel):
    """Response wrapper using service AssetData model"""
    data: List[AssetData]
    total_count: int
    active_count: int

class GetAssetResponse(BaseModel):
    """Response wrapper using service AssetDetailData model"""
    data: AssetDetailData

class InventoryServiceTests:
    """Integration tests for inventory service"""

    def __init__(self, inventory_service_url: str, timeout: int = 10):
        self.inventory_service_url = inventory_service_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.created_assets = []

    def inventory_api(self, endpoint: str) -> str:
        """Helper method to build inventory service API URLs"""
        return APIEndpoints.get_inventory_endpoint(endpoint)

    def inventory_api_with_id(self, endpoint: str, asset_id: str) -> str:
        """Helper method to build inventory service API URLs with asset ID"""
        return APIEndpoints.get_inventory_endpoint(InventoryAPI.ASSET_BY_ID, asset_id=asset_id)

    def test_get_assets(self):
        """Test getting all assets"""
        # Request 200 assets to get a more complete list
        r = self.session.get(self.inventory_api(InventoryAPI.ASSETS), params={"limit": 200}, timeout=self.timeout)
        assert r.status_code == 200

        # Parse as ListAssetsResponse object
        response = ListAssetsResponse(**r.json())

        # Assert using object attributes
        assert response.data is not None
        assert response.total_count is not None
        assert response.active_count is not None
        assert len(response.data) > 0, "Assets list should not be empty"

        # Check that at least one asset exists with proper structure
        first_asset = response.data[0]
        assert first_asset.asset_id is not None
        assert first_asset.asset_id is not TestValues.BTC_ASSET_ID
        assert first_asset.name is not None


    def test_get_asset_by_id(self):
        """Test getting a specific asset by ID"""
        r = self.session.get(self.inventory_api_with_id(InventoryAPI.ASSET_BY_ID, TestValues.BTC_ASSET_ID), timeout=self.timeout)
        assert r.status_code == 200

        # Parse as GetAssetResponse object
        response = GetAssetResponse(**r.json())

        # Assert using object attributes
        assert response.data.asset_id == TestValues.BTC_ASSET_ID
        assert response.data.name is not None

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

        # Parse as ListAssetsResponse object
        response = ListAssetsResponse(**r.json())

        assert response.data is not None
        assert len(response.data) > 0, "Assets list should not be empty"

        # Get first asset
        asset = response.data[0]

        # Check required fields exist using object attributes
        assert asset.asset_id is not None, "Missing asset_id"
        assert asset.name is not None, "Missing name"
        assert asset.category is not None, "Missing category"
        assert asset.price_usd is not None, "Missing price_usd"
        assert asset.is_active is not None, "Missing is_active"

        # Check data types
        assert isinstance(asset.asset_id, str)
        assert isinstance(asset.name, str)
        assert isinstance(asset.price_usd, (int, float))
        assert asset.price_usd >= 0, "Price should be non-negative"
        assert isinstance(asset.is_active, bool)

    def test_asset_consistency(self):
        """Test that two sequential requests return consistent data"""
        r1 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)
        r2 = self.session.get(self.inventory_api(InventoryAPI.ASSETS), timeout=self.timeout)

        assert r1.status_code == 200
        assert r2.status_code == 200

        # Parse as objects
        response1 = ListAssetsResponse(**r1.json())
        response2 = ListAssetsResponse(**r2.json())

        # Asset count should be consistent
        assert len(response1.data) == len(response2.data)

        # Both responses should have same structure and fields
        assert len(response1.data) > 0
        assert len(response2.data) > 0

        # Verify they have matching asset IDs in same order (for consistency)
        ids1 = [asset.asset_id for asset in response1.data]
        ids2 = [asset.asset_id for asset in response2.data]
        assert ids1 == ids2, "Asset lists should be consistent across requests"

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