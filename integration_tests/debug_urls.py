#!/usr/bin/env python3
"""
Debug script to check what URLs are being used
"""
import os
import yaml
import sys

def load_config(config_file: str = "config/services.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Loaded configuration from {config_file}")
        return config
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return {}

def get_api_gateway_url(config):
    """Get API Gateway URL from config or environment"""
    # Try environment variable first
    api_url = os.getenv('API_GATEWAY_URL')
    if api_url:
        print(f"API Gateway URL from env: {api_url}")
        return api_url

    # Try config file
    if config and 'api_gateway' in config:
        env = os.getenv('ENVIRONMENT', 'dev')
        if env in config['api_gateway']:
            url = config['api_gateway'][env]['base_url']
            print(f"API Gateway URL from config: {url}")
            return url

    # Fallback to known URL
    fallback = "https://gsgy1f1cmi.execute-api.us-west-2.amazonaws.com/dev"
    print(f"API Gateway URL fallback: {fallback}")
    return fallback

def get_user_service_url(config):
    """Get user service URL from config or environment"""
    # Try environment variable first
    user_url = os.getenv('USER_SERVICE_URL')
    if user_url:
        print(f"User service URL from env: {user_url}")
        return user_url

    # Try config file
    if config and 'local_services' in config:
        if 'user_service' in config['local_services']:
            url = config['local_services']['user_service']['base_url']
            print(f"User service URL from config: {url}")
            return url

    print("User service URL: None (not configured)")
    return None

def get_inventory_service_url(config):
    """Get inventory service URL from config or environment"""
    # Try environment variable first
    inventory_url = os.getenv('INVENTORY_SERVICE_URL')
    if inventory_url:
        print(f"Inventory service URL from env: {inventory_url}")
        return inventory_url

    # Try config file
    if config and 'local_services' in config:
        if 'inventory_service' in config['local_services']:
            url = config['local_services']['inventory_service']['base_url']
            print(f"Inventory service URL from config: {url}")
            return url

    print("Inventory service URL: None (not configured)")
    return None

def main():
    print("🔍 DEBUG: URL Configuration")
    print("="*50)

    config = load_config()

    print("\n📋 Environment Variables:")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")
    print(f"API_GATEWAY_URL: {os.getenv('API_GATEWAY_URL', 'not set')}")
    print(f"USER_SERVICE_URL: {os.getenv('USER_SERVICE_URL', 'not set')}")
    print(f"INVENTORY_SERVICE_URL: {os.getenv('INVENTORY_SERVICE_URL', 'not set')}")

    print("\n🌐 Service URLs:")
    api_url = get_api_gateway_url(config)
    user_url = get_user_service_url(config)
    inventory_url = get_inventory_service_url(config)

    print(f"\n📊 Summary:")
    print(f"API Gateway: {api_url}")
    print(f"User Service: {user_url}")
    print(f"Inventory Service: {inventory_url}")

    if user_url is None and inventory_url is None:
        print("\n⚠️  Both user and inventory service URLs are None!")
        print("   This means functional tests should be skipped.")
        print("   But if they're running, there might be a bug in the test runner.")

if __name__ == "__main__":
    main()