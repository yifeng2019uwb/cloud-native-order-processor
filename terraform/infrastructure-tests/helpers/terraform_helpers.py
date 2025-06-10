#!/usr/bin/env python3
# File: terraform/infrastructure-tests/helpers/terraform_helpers.py
# Terraform operation utilities
# TerraformManager class with comprehensive operations
# Plan analysis: JSON parsing, change summaries
# State operations: import, move, remove resources
# Apply/destroy with proper error handling

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import tempfile

class TerraformManager:
    """Advanced Terraform operations manager"""

    def __init__(self, terraform_dir: Path, workspace: str = "dev"):
        self.terraform_dir = terraform_dir
        self.workspace = workspace
        self.timeout = 1800  # 30 minutes default timeout

    def run_command(self, command: List[str], capture_output: bool = True,
                   timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Run terraform command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                cwd=self.terraform_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout or self.timeout,
                env=dict(os.environ)
            )
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Terraform command timed out: {' '.join(command)}")
        except Exception as e:
            raise RuntimeError(f"Failed to run terraform command: {e}")

    def init(self, backend_config: Optional[Dict[str, str]] = None) -> bool:
        """Initialize Terraform with optional backend configuration"""
        command = ["terraform", "init", "-input=false"]

        if backend_config:
            # Create temporary backend config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tfvars', delete=False) as f:
                for key, value in backend_config.items():
                    f.write(f'{key} = "{value}"\n')
                command.extend(["-backend-config", f.name])

        result = self.run_command(command, timeout=300)  # 5 minutes for init
        return result.returncode == 0

    def plan_with_output(self, var_file: Optional[str] = None,
                        target: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """Generate plan and return both text and JSON output"""
        # Generate plan file
        plan_file = self.terraform_dir / "tfplan"

        command = ["terraform", "plan", "-input=false", "-out", str(plan_file)]
        if var_file:
            command.extend(["-var-file", var_file])
        if target:
            command.extend(["-target", target])

        result = self.run_command(command)
        if result.returncode not in [0, 2]:  # 0=no changes, 2=changes
            return False, result.stderr, {}

        # Get JSON representation of plan
        json_result = self.run_command(["terraform", "show", "-json", str(plan_file)])
        plan_json = {}
        if json_result.returncode == 0:
            try:
                plan_json = json.loads(json_result.stdout)
            except json.JSONDecodeError:
                pass

        # Clean up plan file
        if plan_file.exists():
            plan_file.unlink()

        return True, result.stdout, plan_json

    def apply_with_auto_approve(self, var_file: Optional[str] = None) -> Tuple[bool, str]:
        """Apply Terraform configuration with auto-approve"""
        command = ["terraform", "apply", "-input=false", "-auto-approve"]
        if var_file:
            command.extend(["-var-file", var_file])

        result = self.run_command(command, timeout=self.timeout)
        return result.returncode == 0, result.stdout

    def destroy_with_auto_approve(self, var_file: Optional[str] = None) -> Tuple[bool, str]:
        """Destroy Terraform configuration with auto-approve"""
        command = ["terraform", "destroy", "-input=false", "-auto-approve"]
        if var_file:
            command.extend(["-var-file", var_file])

        result = self.run_command(command, timeout=self.timeout)
        return result.returncode == 0, result.stdout

    def import_resource(self, resource_address: str, resource_id: str) -> bool:
        """Import existing resource into Terraform state"""
        command = ["terraform", "import", resource_address, resource_id]
        result = self.run_command(command)
        return result.returncode == 0

    def state_mv(self, source: str, destination: str) -> bool:
        """Move resource in Terraform state"""
        command = ["terraform", "state", "mv", source, destination]
        result = self.run_command(command)
        return result.returncode == 0

    def state_rm(self, resource_address: str) -> bool:
        """Remove resource from Terraform state"""
        command = ["terraform", "state", "rm", resource_address]
        result = self.run_command(command)
        return result.returncode == 0

    def get_resource_from_state(self, resource_address: str) -> Optional[Dict]:
        """Get specific resource from Terraform state"""
        result = self.run_command(["terraform", "state", "show", "-json", resource_address])
        if result.returncode != 0:
            return None

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    def refresh_state(self) -> bool:
        """Refresh Terraform state"""
        result = self.run_command(["terraform", "refresh", "-input=false"])
        return result.returncode == 0

    def get_plan_summary(self, plan_json: Dict) -> Dict[str, int]:
        """Extract summary from plan JSON"""
        if not plan_json or 'resource_changes' not in plan_json:
            return {}

        summary = {
            'create': 0,
            'update': 0,
            'delete': 0,
            'replace': 0,
            'no_change': 0
        }

        for change in plan_json['resource_changes']:
            actions = change.get('change', {}).get('actions', [])

            if actions == ['create']:
                summary['create'] += 1
            elif actions == ['update']:
                summary['update'] += 1
            elif actions == ['delete']:
                summary['delete'] += 1
            elif actions == ['delete', 'create']:
                summary['replace'] += 1
            elif actions == ['no-op']:
                summary['no_change'] += 1

        return summary
