"""
Test data management utility
Handles UUID generation and cleanup for test isolation
"""
import uuid
import time
from typing import Dict, List, Any
from datetime import datetime, timezone

class TestDataManager:
    """Manages test data with UUID-based isolation and cleanup"""

    def __init__(self, user_prefix: str = "test_user", asset_prefix: str = "test_asset"):
        self.user_prefix = user_prefix
        self.asset_prefix = asset_prefix
        self.created_data = {
            'users': [],
            'assets': []
        }
        self.test_run_id = str(uuid.uuid4())[:8]

    def generate_user_data(self, email_domain: str = "test.example.com") -> Dict[str, str]:
        """Generate unique user test data"""
        user_id = f"{self.user_prefix}_{self.test_run_id}_{str(uuid.uuid4())[:8]}"
        user_data = {
            'username': user_id,
            'email': f"{user_id}@{email_domain}",
            'password': f"testpass_{str(uuid.uuid4())[:8]}",
            'test_id': user_id
        }
        self.created_data['users'].append(user_data)
        return user_data

    def generate_asset_data(self, category: str = "test_category") -> Dict[str, Any]:
        """Generate unique asset test data"""
        asset_id = f"{self.asset_prefix}_{self.test_run_id}_{str(uuid.uuid4())[:8]}"
        asset_data = {
            'name': f"Test Asset {asset_id}",
            'description': f"Test asset created at {datetime.now(timezone.utc).isoformat()}",
            'category': category,
            'value': 100.0,
            'test_id': asset_id
        }
        self.created_data['assets'].append(asset_data)
        return asset_data

    def get_created_users(self) -> List[Dict[str, str]]:
        """Get list of created users for cleanup"""
        return self.created_data['users']

    def get_created_assets(self) -> List[Dict[str, Any]]:
        """Get list of created assets for cleanup"""
        return self.created_data['assets']

    def mark_for_cleanup(self, data_type: str, data: Dict[str, Any]):
        """Mark data for cleanup after tests"""
        if data_type in self.created_data:
            self.created_data[data_type].append(data)

    def get_test_run_id(self) -> str:
        """Get unique test run identifier"""
        return self.test_run_id

    def clear_data(self):
        """Clear all test data (for cleanup)"""
        self.created_data = {
            'users': [],
            'assets': []
        }