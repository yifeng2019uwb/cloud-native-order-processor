#!/usr/bin/env python3
# File: terraform/infrastructure-tests/conftest.py
# Test configuration and fixtures for infrastructure tests
# TerraformHelper class for all Terraform operations
# AWSHelper class for AWS resource validation
# Session-scoped fixtures for shared resources
# Auto-setup for Terraform init and workspace management

import os
import sys
import json
import boto3
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    "terraform_dir": Path(__file__).parent.parent,
    "timeout": {
        "terraform_init": 300,  # 5 minutes
        "terraform_plan": 600,  # 10 minutes
        "terraform_apply": 1800,  # 30 minutes
        "aws_resource_check": 60  # 1 minute
    },
    "required_terraform_version": "1.5.0",
    "aws_regions": ["us-west-2", "us-east-1"],  # Supported regions
}

class TerraformHelper:
    """Helper class for Terraform operations"""

    def __init__(self, terraform_dir: Path):
        self.terraform_dir = terraform_dir
        self.workspace = os.getenv("TERRAFORM_WORKSPACE", "dev")

    def run_command(self, command: list, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run terraform command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                cwd=self.terraform_dir,
                capture_output=capture_output,
                text=True,
                timeout=TEST_CONFIG["timeout"]["terraform_plan"]
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Terraform command timed out: {' '.join(command)}")
        except Exception as e:
            pytest.fail(f"Failed to run terraform command: {e}")

    def init(self) -> bool:
        """Initialize Terraform"""
        result = self.run_command(["terraform", "init", "-input=false"])
        return result.returncode == 0

    def workspace_select_or_create(self) -> bool:
        """Select or create terraform workspace"""
        # Try to select workspace
        result = self.run_command(["terraform", "workspace", "select", self.workspace])
        if result.returncode == 0:
            return True

        # If select fails, try to create
        result = self.run_command(["terraform", "workspace", "new", self.workspace])
        return result.returncode == 0

    def validate(self) -> tuple[bool, str]:
        """Validate Terraform configuration"""
        result = self.run_command(["terraform", "validate", "-json"])
        if result.returncode == 0:
            return True, ""
        return False, result.stderr

    def plan(self, var_file: Optional[str] = None) -> tuple[bool, str]:
        """Generate Terraform plan"""
        command = ["terraform", "plan", "-input=false", "-detailed-exitcode"]
        if var_file:
            command.extend(["-var-file", var_file])

        result = self.run_command(command)
        return result.returncode in [0, 2], result.stdout  # 0=no changes, 2=changes

    def output(self, output_name: Optional[str] = None) -> Dict[str, Any]:
        """Get Terraform outputs"""
        command = ["terraform", "output", "-json"]
        if output_name:
            command.append(output_name)

        result = self.run_command(command)
        if result.returncode != 0:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}

    def state_list(self) -> list[str]:
        """List resources in Terraform state"""
        result = self.run_command(["terraform", "state", "list"])
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.split('\n') if line.strip()]

class AWSHelper:
    """Helper class for AWS operations"""

    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        self.session = boto3.Session(region_name=self.region)

    def get_client(self, service_name: str):
        """Get AWS service client"""
        return self.session.client(service_name)

    def get_resource(self, service_name: str):
        """Get AWS service resource"""
        return self.session.resource(service_name)

    def get_account_id(self) -> str:
        """Get current AWS account ID"""
        sts = self.get_client('sts')
        return sts.get_caller_identity()['Account']

    def check_s3_bucket_exists(self, bucket_name: str) -> bool:
        """Check if S3 bucket exists"""
        try:
            s3 = self.get_client('s3')
            s3.head_bucket(Bucket=bucket_name)
            return True
        except Exception:
            return False

    def check_dynamodb_table_exists(self, table_name: str) -> bool:
        """Check if DynamoDB table exists"""
        try:
            dynamodb = self.get_client('dynamodb')
            dynamodb.describe_table(TableName=table_name)
            return True
        except Exception:
            return False

    def get_vpc_by_tag(self, tag_key: str, tag_value: str) -> Optional[Dict]:
        """Find VPC by tag"""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_vpcs(
                Filters=[
                    {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
                ]
            )
            vpcs = response.get('Vpcs', [])
            return vpcs[0] if vpcs else None
        except Exception:
            return None

@pytest.fixture(scope="session")
def environment_config():
    """Load environment configuration"""
    return {
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "aws_region": os.getenv("AWS_DEFAULT_REGION", "us-west-2"),
        "resource_prefix": os.getenv("RESOURCE_PREFIX", "order-processor-dev"),
        "project_name": os.getenv("PROJECT_NAME", "cloud-native-order-processor"),
    }

@pytest.fixture(scope="session")
def terraform_helper():
    """Terraform helper fixture"""
    terraform_dir = TEST_CONFIG["terraform_dir"]
    helper = TerraformHelper(terraform_dir)

    # Ensure terraform is initialized
    if not helper.init():
        pytest.fail("Failed to initialize Terraform")

    # Ensure workspace is selected
    if not helper.workspace_select_or_create():
        pytest.fail(f"Failed to select/create workspace: {helper.workspace}")

    return helper

@pytest.fixture(scope="session")
def aws_helper():
    """AWS helper fixture"""
    return AWSHelper()

@pytest.fixture(scope="session")
def terraform_outputs(terraform_helper):
    """Get all Terraform outputs"""
    return terraform_helper.output()

@pytest.fixture(scope="session")
def terraform_state_resources(terraform_helper):
    """Get all resources from Terraform state"""
    return terraform_helper.state_list()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "aws: marks tests that require AWS access"
    )
    config.addinivalue_line(
        "markers", "terraform: marks tests that require Terraform"
    )

def pytest_runtest_setup(item):
    """Setup for each test"""
    # Skip AWS tests if credentials not available
    if "aws" in item.keywords:
        try:
            boto3.Session().get_credentials()
        except Exception:
            pytest.skip("AWS credentials not available")

    # Skip Terraform tests if terraform not available
    if "terraform" in item.keywords:
        try:
            subprocess.run(["terraform", "version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Terraform not available")
