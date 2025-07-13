#!/usr/bin/env python3
import sys
import traceback

# Add paths to Python path
sys.path.insert(0, 'src')
sys.path.insert(0, '../common/src')
sys.path.insert(0, '../common')

print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nTesting imports...")

try:
    print("1. Testing common.entities.user import...")
    from common.entities.user import UserCreate, User
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()

try:
    print("2. Testing api_models.auth.registration import...")
    from api_models.auth.registration import UserRegistrationRequest
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()

try:
    print("3. Testing controllers.auth.register import...")
    from controllers.auth.register import router
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()