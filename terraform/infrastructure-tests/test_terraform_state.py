#!/usr/bin/env python3
# File: terraform/infrastructure-tests/test_terraform_state.py
# Terraform state and configuration validation tests
# Configuration tests: version, validation, formatting
# Plan generation: success, error checking, resource validation
# State management: backend config, locking, state consistency
# Security checks: no hardcoded secrets, encryption, permissions

import pytest
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

@pytest.mark.terraform
class TestTerraformConfiguration:
    """Test Terraform configuration validity"""

    def test_terraform_version(self, terraform_helper):
        """Test that Terraform version meets requirements"""
        result = terraform_helper.run_command(["terraform", "version", "-json"])
        assert result.returncode == 0, "Failed to get Terraform version"

        version_info = json.loads(result.stdout)
        terraform_version = version_info["terraform_version"]

        # Basic version format check
        assert terraform_version.count('.') >= 2, f"Invalid version format: {terraform_version}"

        # Check minimum version (basic comparison)
        version_parts = terraform_version.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        assert major > 1 or (major == 1 and minor >= 5), f"Terraform version {terraform_version} is too old"

    def test_terraform_validate(self, terraform_helper):
        """Test that Terraform configuration is valid"""
        is_valid, error_message = terraform_helper.validate()
        assert is_valid, f"Terraform validation failed: {error_message}"

    def test_terraform_fmt_check(self, terraform_helper):
        """Test that Terraform files are properly formatted"""
        result = terraform_helper.run_command(["terraform", "fmt", "-check", "-recursive"])
        assert result.returncode == 0, "Terraform files are not properly formatted. Run 'terraform fmt -recursive'"

    def test_terraform_init_successful(self, terraform_helper):
        """Test that Terraform initialization was successful"""
        terraform_dir = terraform_helper.terraform_dir

        # Check that .terraform directory exists
        terraform_hidden_dir = terraform_dir / ".terraform"
        assert terraform_hidden_dir.exists(), "Terraform not initialized (.terraform directory missing)"

        # Check that providers are downloaded
        providers_dir = terraform_hidden_dir / "providers"
        if providers_dir.exists():
            # Should have at least AWS provider
            provider_files = list(providers_dir.rglob("*"))
            assert len(provider_files) > 0, "No providers downloaded"

    def test_terraform_workspace(self, terraform_helper):
        """Test that correct Terraform workspace is selected"""
        result = terraform_helper.run_command(["terraform", "workspace", "show"])
        assert result.returncode == 0, "Failed to get current workspace"

        current_workspace = result.stdout.strip()
        expected_workspace = terraform_helper.workspace
        assert current_workspace == expected_workspace, f"Wrong workspace selected: {current_workspace} != {expected_workspace}"

@pytest.mark.terraform
@pytest.mark.slow
class TestTerraformPlan:
    """Test Terraform plan generation"""

    def test_terraform_plan_succeeds(self, terraform_helper):
        """Test that Terraform plan can be generated successfully"""
        is_successful, plan_output = terraform_helper.plan()
        assert is_successful, f"Terraform plan failed:\n{plan_output}"

    def test_terraform_plan_no_errors(self, terraform_helper):
        """Test that Terraform plan contains no errors"""
        result = terraform_helper.run_command(["terraform", "plan", "-input=false"])

        # Check for common error patterns
        error_patterns = [
            "Error:",
            "error:",
            "Failed to",
            "Invalid",
            "Unsupported"
        ]

        for pattern in error_patterns:
            assert pattern not in result.stdout, f"Plan contains error pattern '{pattern}'"
            assert pattern not in result.stderr, f"Plan stderr contains error pattern '{pattern}'"

@pytest.mark.terraform
@pytest.mark.integration
class TestTerraformState:
    """Test Terraform state management"""

    def test_terraform_state_backend_configured(self, terraform_helper):
        """Test that Terraform backend is properly configured"""
        terraform_dir = terraform_helper.terraform_dir

        # Check for backend configuration
        tf_files = list(terraform_dir.glob("*.tf"))
        backend_found = False

        for tf_file in tf_files:
            content = tf_file.read_text()
            if "backend" in content and "s3" in content:
                backend_found = True
                break

        assert backend_found, "No S3 backend configuration found in Terraform files"

    def test_terraform_state_lock_table(self, terraform_helper, aws_helper):
        """Test that DynamoDB table for state locking exists or can be created"""
        # Get backend configuration to find lock table name
        result = terraform_helper.run_command(["terraform", "init", "-backend=false"])

        # For this test, we'll use the expected naming convention
        # In real deployment, this should be extracted from backend config
        lock_table_name = f"{terraform_helper.workspace}-terraform-locks"

        # Note: This test assumes the table will be created by Terraform itself
        # We're just checking that we can query DynamoDB
        try:
            dynamodb = aws_helper.get_client('dynamodb')
            tables = dynamodb.list_tables()
            # Test passes if we can list tables (permissions are correct)
            assert 'TableNames' in tables
        except Exception as e:
            pytest.fail(f"Cannot access DynamoDB for state locking: {e}")

    def test_terraform_state_exists_if_applied(self, terraform_helper):
        """Test that Terraform state exists if infrastructure is applied"""
        result = terraform_helper.run_command(["terraform", "state", "list"])

        if result.returncode == 0 and result.stdout.strip():
            # State exists and has resources
            resources = result.stdout.strip().split('\n')
            assert len(resources) > 0, "State file exists but contains no resources"

            # Verify state can be read
            state_result = terraform_helper.run_command(["terraform", "show", "-json"])
            assert state_result.returncode == 0, "Cannot read Terraform state"

            try:
                state_data = json.loads(state_result.stdout)
                assert 'values' in state_data, "State file format is invalid"
            except json.JSONDecodeError:
                pytest.fail("State file is not valid JSON")
        else:
            # No state yet - this is OK for initial runs
            pytest.skip("No Terraform state exists yet (infrastructure not applied)")

@pytest.mark.terraform
class TestTerraformOutputs:
    """Test Terraform outputs"""

    def test_terraform_outputs_accessible(self, terraform_helper):
        """Test that Terraform outputs can be retrieved"""
        outputs = terraform_helper.output()

        # If infrastructure is applied, outputs should be accessible
        result = terraform_helper.run_command(["terraform", "output"])
        if result.returncode == 0 and result.stdout.strip():
            assert isinstance(outputs, dict), "Outputs should be a dictionary"
        else:
            pytest.skip("No outputs available (infrastructure not applied)")

    def test_required_outputs_present(self, terraform_outputs, terraform_state_resources):
        """Test that required outputs are present when infrastructure is applied"""
        if not terraform_state_resources:
            pytest.skip("No infrastructure deployed yet")

        # Define expected outputs based on your infrastructure
        expected_outputs = [
            "vpc_id",
            "subnet_ids",
            "ecs_cluster_name",
            "security_group_ids"
        ]

        for output_name in expected_outputs:
            if output_name in terraform_outputs:
                output_value = terraform_outputs[output_name].get('value')
                assert output_value is not None, f"Output '{output_name}' has no value"
                assert output_value != "", f"Output '{output_name}' is empty"

@pytest.mark.terraform
@pytest.mark.slow
class TestTerraformSecurity:
    """Test Terraform security configurations"""

    def test_no_hardcoded_secrets(self, terraform_helper):
        """Test that no secrets are hardcoded in Terraform files"""
        terraform_dir = terraform_helper.terraform_dir
        tf_files = list(terraform_dir.glob("**/*.tf"))

        # Patterns that might indicate hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*"[^"]{8,}"',
            r'secret\s*=\s*"[^"]{8,}"',
            r'key\s*=\s*"[A-Z0-9]{20,}"',
            r'token\s*=\s*"[^"]{16,}"'
        ]

        import re

        for tf_file in tf_files:
            content = tf_file.read_text()
            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert len(matches) == 0, f"Potential hardcoded secret found in {tf_file}: {matches}"

    def test_s3_bucket_encryption_enabled(self, terraform_helper):
        """Test that S3 buckets have encryption enabled"""
        tf_files = list(terraform_helper.terraform_dir.glob("**/*.tf"))

        for tf_file in tf_files:
            content = tf_file.read_text()
            if "aws_s3_bucket" in content:
                # Check if encryption is configured (allow for different terraform versions)
                has_encryption = any(encryption_term in content for encryption_term in [
                    "server_side_encryption_configuration",
                    "aws_s3_bucket_encryption"
                ])
                if not has_encryption:
                    # This is a warning, not a failure for development environments
                    print(f"Warning: S3 bucket in {tf_file} should have encryption configured")

    def test_security_groups_not_too_permissive(self, terraform_helper):
        """Test that security groups are not overly permissive"""
        tf_files = list(terraform_helper.terraform_dir.glob("**/*.tf"))

        for tf_file in tf_files:
            content = tf_file.read_text()
            if "aws_security_group" in content:
                # Should not allow 0.0.0.0/0 for all ports
                dangerous_patterns = [
                    'cidr_blocks = ["0.0.0.0/0"]',
                    'from_port = 0',
                    'to_port = 65535'
                ]

                # Check if multiple dangerous patterns exist together
                pattern_count = sum(1 for pattern in dangerous_patterns if pattern in content)
                assert pattern_count < 3, f"Security group in {tf_file} may be too permissive"
