"""
User Transaction History API Integration Tests
Tests GET /balance/transactions endpoint - validates transaction history retrieval
"""
import uuid
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestUserValues, CommonFields

class UserTransactionHistoryTests:
    """Integration tests for transaction history API - focus on data retrieval and filtering"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_empty_transaction_history(self):
        """Test new user has empty transaction history"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert UserFields.TRANSACTIONS in data
        assert isinstance(data[UserFields.TRANSACTIONS], list)
        assert len(data[UserFields.TRANSACTIONS]) == 0

    def test_transaction_history_after_deposit(self):
        """Test transaction history contains deposit record"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        # Make a deposit
        deposit_data = {UserFields.AMOUNT: 500}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Get transaction history
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert UserFields.TRANSACTIONS in data
        transactions = data[UserFields.TRANSACTIONS]
        assert len(transactions) >= 1

    def test_transaction_history_after_withdraw(self):
        """Test transaction history contains withdrawal record"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        # Deposit first
        deposit_data = {UserFields.AMOUNT: 500}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Withdraw
        withdraw_data = {UserFields.AMOUNT: 100}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            json=withdraw_data,
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code == 201

        # Get transaction history
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert UserFields.TRANSACTIONS in data
        transactions = data[UserFields.TRANSACTIONS]
        assert len(transactions) >= 2

    def test_transaction_history_pagination(self):
        """Test transaction history with pagination parameters"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)
        headers = self.user_manager.build_auth_headers(token)

        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS) + "?limit=10&offset=0",
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert UserFields.TRANSACTIONS in data

    def run_all_transaction_history_tests(self):
        """Run all transaction history tests"""
        self.test_empty_transaction_history()
        self.test_transaction_history_after_deposit()
        self.test_transaction_history_after_withdraw()
        self.test_transaction_history_pagination()

if __name__ == "__main__":
    tests = UserTransactionHistoryTests()
    tests.run_all_transaction_history_tests()
