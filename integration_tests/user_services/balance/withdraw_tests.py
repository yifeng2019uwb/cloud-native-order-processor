"""
User Withdraw API Integration Tests
Tests POST /balance/withdraw endpoint - validates withdrawal business logic
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

class UserWithdrawTests:
    """Integration tests for user withdraw API - focus on validation and business logic"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_withdraw_success(self):
        """Test successful withdrawal"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit first to have funds
        deposit_data = {UserFields.AMOUNT: 1000}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Withdraw
        withdraw_data = {UserFields.AMOUNT: 300}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )
        assert response.status_code == 201

    def test_withdraw_negative_amount(self):
        """Test withdrawal with negative amount is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={UserFields.AMOUNT: -50.00},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_withdraw_zero_amount(self):
        """Test withdrawal with zero amount is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={UserFields.AMOUNT: 0},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Try to withdraw without any deposits
        withdraw_data = {UserFields.AMOUNT: 100}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_withdraw_more_than_balance(self):
        """Test withdrawal exceeding balance is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit 100
        deposit_data = {UserFields.AMOUNT: 100}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Try to withdraw 200 (more than balance)
        withdraw_data = {UserFields.AMOUNT: 200}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )
        assert response.status_code == 422

    def test_withdraw_missing_amount(self):
        """Test withdrawal with missing amount field is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={},
            timeout=self.timeout
        )
        assert response.status_code == 422

    def run_all_withdraw_tests(self):
        """Run all withdrawal validation tests"""
        self.test_withdraw_success()
        self.test_withdraw_negative_amount()
        self.test_withdraw_zero_amount()
        self.test_withdraw_insufficient_funds()
        self.test_withdraw_more_than_balance()
        self.test_withdraw_missing_amount()

if __name__ == "__main__":
    tests = UserWithdrawTests()
    tests.run_all_withdraw_tests()
