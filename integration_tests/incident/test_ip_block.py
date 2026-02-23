"""
Incident response integration test: IP block (SEC-011).
Same style as user/auth/login: TestUserManager, APIEndpoints, UserAPI, UserFields, TestUserValues.

Steps:
  1. Init: create a new user (register + login).
  2. Login with correct password (no issue), then logout.
  3. Login with same user + wrong password 5 times; 6th request should get 403 if IP block is on.
  4. Wait 5 minutes, then login again with correct password to verify block expired.

Run: cd integration_tests && python3 incident/test_ip_block.py
Or: ./run_all_tests.sh incident
"""
import sys
import os
import time
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "config"))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestUserValues

import requests


class IPBlockTests:
    """IP block (SEC-011) – same way as user/auth/login. No extra constants."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager(timeout=timeout)
        self.username = None  # set by init_suite(), used by all tests

    def user_api(self, api: UserAPI) -> str:
        return APIEndpoints.get_user_endpoint(api)

    def init_suite(self):
        """Shared init for incident tests: create user, login, logout. Run once; all tests use self.username."""
        if self.username is not None:
            return
        username = f"incident_testuser_{uuid.uuid4().hex[:8]}"
        token = self.user_manager.create_test_user(self.session, username)
        assert token, "Init: create test user should return token"
        login_ok = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.USERNAME: username, UserFields.PASSWORD: TestUserValues.DEFAULT_PASSWORD},
            timeout=self.timeout,
        )
        assert login_ok.status_code == 200, f"Init: login expected 200, got {login_ok.status_code}"
        data = login_ok.json()
        token_data = data.get(UserFields.DATA, data)
        token = token_data.get(UserFields.ACCESS_TOKEN)
        assert token, "Init: login response should include access token"
        logout_ok = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=self.user_manager.build_auth_headers(token),
            json={UserFields.ACCESS_TOKEN: token},
            timeout=self.timeout,
        )
        assert logout_ok.status_code == 200, f"Init: logout expected 200, got {logout_ok.status_code}"
        self.username = username
        print("  OK: Init – user created, login OK, logout OK")

    def test_brute_force_triggers_ip_block(self):
        """Step 1 & 2 from init_suite (run once in run_all_ip_block_tests). Step 3: 5 wrong logins then 6th => 403."""
        username = self.username
        assert username, "run_all_ip_block_tests() must call init_suite() first"

        # Step 3: same user, wrong password 5 times; 6th request should get 403 (IP blocked)
        wrong_password = "WrongPassword123!"  # valid format, wrong
        payload = {UserFields.USERNAME: username, UserFields.PASSWORD: wrong_password}
        for _ in range(5):
            self.session.post(self.user_api(UserAPI.LOGIN), json=payload, timeout=self.timeout)

        r = self.session.post(self.user_api(UserAPI.LOGIN), json=payload, timeout=self.timeout)
        assert r.status_code == 403, (
            f"Step 3: expected 403 (IP blocked) after 5 failed logins, got {r.status_code}. "
            "Check gateway/Redis: IP block (SEC-011) may not be applied correctly."
        )
        print("  OK: Step 3 – 6th request got 403 (IP blocked)")

    def test_ip_block_expires(self):
        """Step 4: wait 5 minutes then login again with correct password to verify block expired."""
        username = self.username  # set by init_suite(); brute_force must run first so IP is blocked
        assert username, "run_all_ip_block_tests() must call init_suite() first"
        print("  Step 4: Waiting 5 minutes for block to expire...")
        time.sleep(300)
        login_after = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.USERNAME: username, UserFields.PASSWORD: TestUserValues.DEFAULT_PASSWORD},
            timeout=self.timeout,
        )
        assert login_after.status_code == 200, (
            f"Step 4: after block expiry expected 200, got {login_after.status_code}"
        )
        print("  OK: Step 4 – block expired, login works again")

    def run_all_ip_block_tests(self):
        print("=== Incident: IP block (SEC-011) ===")
        self.init_suite()
        self.test_brute_force_triggers_ip_block()
        self.test_ip_block_expires()
        print("=== Incident IP block tests passed ===\n")


if __name__ == "__main__":
    tests = IPBlockTests()
    tests.run_all_ip_block_tests()
