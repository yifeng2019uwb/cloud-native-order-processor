"""
User Deposit API Integration Tests
Tests POST /balance/deposit endpoint - validates deposit business logic
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields

class UserDepositTests:
    """Integration tests for user deposit API - focus on validation and business logic"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_deposit_success(self):
        """Test successful deposit"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}
        deposit_data = {UserFields.AMOUNT: 100.00}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json=deposit_data,
            timeout=self.timeout
        )

        assert response.status_code == 201

    def test_deposit_negative_amount(self):
        """Test deposit with negative amount is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: -50.00},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_deposit_zero_amount(self):
        """Test deposit with zero amount is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: 0},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_deposit_missing_amount(self):
        """Test deposit with missing amount field is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_deposit_exceeds_max_amount(self):
        """Test deposit exceeding max amount limit is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: 999999999.99},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def run_all_deposit_tests(self):
        """Run all deposit validation tests"""
        self.test_deposit_success()
        self.test_deposit_negative_amount()
        self.test_deposit_zero_amount()
        self.test_deposit_missing_amount()
        self.test_deposit_exceeds_max_amount()

if __name__ == "__main__":
    tests = UserDepositTests()
    tests.run_all_deposit_tests()
