"""
User Balance API Integration Tests
Tests GET /balance endpoint - validates balance calculation after deposits and withdrawals
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, CommonFields

class UserBalanceTests:
    """Integration tests for user balance API - focus on balance calculation correctness"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_initial_balance_is_zero(self):
        """Test new user has zero balance"""
        user, token = self.user_manager.create_test_user(self.session)

        headers = {'Authorization': f'Bearer {token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        balance = float(data.get(UserFields.CURRENT_BALANCE, data.get(UserFields.BALANCE)))
        assert balance == 0

    def test_balance_after_deposit(self):
        """Test balance correctly reflects deposit"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit 1000
        deposit_data = {UserFields.AMOUNT: 1000}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Check balance
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 200
        data = response.json()
        balance = float(data.get(UserFields.CURRENT_BALANCE, data.get(UserFields.BALANCE)))
        assert balance == 1000

    def test_balance_after_multiple_deposits(self):
        """Test balance correctly accumulates multiple deposits"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit 500, then 300
        for amount in [500, 300]:
            deposit_data = {UserFields.AMOUNT: amount}
            response = self.session.post(
                self.user_api(UserAPI.BALANCE_DEPOSIT),
                json=deposit_data,
                headers=headers,
                timeout=self.timeout
            )
            assert response.status_code == 201

        # Check balance
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 200
        data = response.json()
        balance = float(data.get(UserFields.CURRENT_BALANCE, data.get(UserFields.BALANCE)))
        assert balance == 800

    def test_balance_after_deposit_and_withdrawal(self):
        """Test balance correctly reflects both deposits and withdrawals"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        # Deposit 1000
        deposit_data = {UserFields.AMOUNT: 1000}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Withdraw 300
        withdraw_data = {UserFields.AMOUNT: 300}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            json=withdraw_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Check balance
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 200
        data = response.json()
        balance = float(data.get(UserFields.CURRENT_BALANCE, data.get(UserFields.BALANCE)))
        assert balance == 700

    def test_balance_response_schema(self):
        """Test balance response has correct schema"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        # Verify required fields exist
        has_balance = UserFields.CURRENT_BALANCE in data or UserFields.BALANCE in data
        has_timestamp = UserFields.UPDATED_AT in data or CommonFields.TIMESTAMP in data
        assert has_balance
        assert has_timestamp

    def run_all_balance_tests(self):
        """Run all balance calculation tests"""
        self.test_initial_balance_is_zero()
        self.test_balance_after_deposit()
        self.test_balance_after_multiple_deposits()
        self.test_balance_after_deposit_and_withdrawal()
        self.test_balance_response_schema()

if __name__ == "__main__":
    tests = UserBalanceTests()
    tests.run_all_balance_tests()
