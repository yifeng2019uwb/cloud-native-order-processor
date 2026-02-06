#!/usr/bin/env python3
"""
Create Load Test Users
Pre-creates test users for k6 load tests
Reuses integration test user_manager.py pattern
"""

import sys
import os
import json
import requests

# Add integration_tests paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../config'))

from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestUserValues

def create_load_test_user(username: str = "load_test_user_1"):
    """
    Create or get existing load test user and save token to JSON file
    Reuses integration_tests/utils/user_manager.py pattern
    
    Since database doesn't allow deletion, checks if user exists first:
    - If user exists: Login to get token
    - If user doesn't exist: Create new user
    """
    session = requests.Session()
    user_manager = TestUserManager()
    
    try:
        # Check if user already exists by trying to login first
        login_data = {
            UserFields.USERNAME: username,
            UserFields.PASSWORD: TestUserValues.DEFAULT_PASSWORD
        }
        
        login_url = APIEndpoints.get_user_endpoint(UserAPI.LOGIN)
        login_response = session.post(login_url, json=login_data, timeout=user_manager.timeout)
        
        if login_response.status_code == 200:
            # User exists - use existing token
            # Handle response structure (token may be in 'data' field or root)
            response_data = login_response.json()
            token_data = response_data.get(UserFields.DATA, response_data)
            token = token_data[UserFields.ACCESS_TOKEN]
            print(f"✅ User already exists: {username}")
            print(f"   Logged in and retrieved token")
        else:
            # User doesn't exist - create new user
            print(f"📝 User doesn't exist, creating: {username}")
            token = user_manager.create_test_user(session, username)
            print(f"✅ Created new load test user: {username}")
        
        # Save token to JSON file for k6 scripts (in k6 directory)
        k6_dir = os.path.join(os.path.dirname(__file__), '../k6')
        os.makedirs(k6_dir, exist_ok=True)
        output_file = os.path.join(k6_dir, 'test_user.json')
        user_data = {
            "username": username,
            "token": token
        }
        
        with open(output_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        print(f"   Token saved to: {output_file}")
        return token
        
    except Exception as e:
        print(f"❌ Failed to create/get load test user: {e}")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Create load test user')
    parser.add_argument('--username', default='load_test_user_1', help='Username for load test user')
    args = parser.parse_args()
    
    create_load_test_user(args.username)
