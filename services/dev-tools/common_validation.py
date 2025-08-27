#!/usr/bin/env python3
"""
Common validation functions for development scripts
Provides shared validation utilities across all service dev.sh scripts
"""

import os
import sys
from pathlib import Path

def check_python_syntax(directory="src"):
    """
    Check Python syntax for all .py files in a directory

    Args:
        directory: Directory to check (default: 'src')

    Returns:
        tuple: (success: bool, file_count: int, error_count: int)
    """
    syntax_errors = 0
    file_count = 0

    if not os.path.exists(directory):
        return False, 0, 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_count += 1

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    print(f"Syntax error in: {file_path}")
                    print(f"  Line {e.lineno}: {e.text}")
                    print(f"  Error: {e.msg}")
                    syntax_errors += 1
                except Exception as e:
                    print(f"Error checking {file_path}: {e}")
                    syntax_errors += 1

    return syntax_errors == 0, file_count, syntax_errors



def validate_service_imports(service_name, service_dir="."):
    """
    Validate critical imports for a service

    Args:
        service_name: Name of the service being validated
        service_dir: Directory containing the service (default: current directory)

    Returns:
        tuple: (success: bool, issues: list)
    """
    import sys
    from pathlib import Path

    issues = []
    original_path = list(sys.path)

    try:
        # Add service src and dev-tools to Python path
        service_src = Path(service_dir) / "src"
        dev_tools = Path(service_dir) / ".." / "dev-tools"

        if service_src.exists():
            sys.path.insert(0, str(service_src))
        if dev_tools.exists():
            sys.path.insert(0, str(dev_tools))

        # Import validation functions
        from mock_env import setup_mock_environment, validate_import

        # Setup mock environment
        setup_mock_environment()

        # Generic import tests that work for all services
        import_tests = [
            ("main", "Main application")
        ]

        # Only test common.auth.security for services that actually need it
        if service_name == "auth_service":
            import_tests.append(("common.auth.security", "Common package auth"))

        # Add service-specific exceptions if they exist
        try:
            if service_name == "user_service":
                import_tests.append(("user_exceptions", "Service exceptions"))
            elif service_name == "inventory_service":
                import_tests.append(("inventory_exceptions", "Service exceptions"))
            elif service_name == "order_service":
                import_tests.append(("order_exceptions", "Service exceptions"))
            elif service_name == "auth_service":
                import_tests.append(("auth_exceptions", "Service exceptions"))
        except:
            pass  # Skip if service exceptions don't exist

        # Run import tests
        for module_path, description in import_tests:
            try:
                if not validate_import(module_path, description):
                    issues.append(f"Import validation failed for {description}")
            except Exception as e:
                issues.append(f"Import validation error for {description}: {e}")

        if not issues:
            print(f"✓ All {service_name} imports validated successfully")
        else:
            print(f"✗ {len(issues)} import validation issues found in {service_name}")

    except Exception as e:
        issues.append(f"Import validation setup failed: {e}")
    finally:
        # Restore original Python path
        sys.path = original_path

    return len(issues) == 0, issues

if __name__ == "__main__":
    # When run directly, test the validation functions
    print("Testing common validation functions...")

    # Test syntax checking
    success, file_count, errors = check_python_syntax()
    print(f"Syntax check: {file_count} files, {errors} errors")

    # Test import validation
    try:
        success, issues = validate_service_imports("test_service")
        print(f"Import validation: {'OK' if success else 'Issues found'}")
        for issue in issues:
            print(f"  - {issue}")
    except Exception as e:
        print(f"Import validation failed: {e}")
