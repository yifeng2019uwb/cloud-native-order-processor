#!/usr/bin/env python3
"""
Test Runner Script for Order Processor API
Runs all tests in the docker/tests directory with various options
"""

import os
import sys
import subprocess
import argparse
import shutil # Added for rmtree
from pathlib import Path
from typing import List, Optional

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class TestRunner:
    """Test runner for the Order Processor API"""
    
    def __init__(self, test_path: str = "tests", api_path: str = "api"): # Corrected default paths
        # Paths are relative to the directory where this script is run (docker/)
        self.script_dir = Path(__file__).parent # This will be the 'docker' directory
        self.project_root = self.script_dir.parent # This will be 'cloud-native-order-processor'
        
        self.test_path = self.script_dir / test_path # e.g., docker/tests
        self.api_path = self.script_dir / api_path   # e.g., docker/api
        
        # Determine Python command based on activated virtual environment
        # sys.executable points to the interpreter currently running this script.
        # This assumes the user has activated the virtual environment before running the script.
        self.python_cmd = sys.executable 
        
    def print_colored(self, message: str, color: str = NC) -> None:
        """Print colored message"""
        print(f"{color}{message}{NC}")
        
    def run_command(self, cmd: List[str], check: bool = True) -> Optional[subprocess.CompletedProcess]:
        """Run a command and return the result"""
        try:
            self.print_colored(f"Running: {' '.join(cmd)}", BLUE)
            # Use 'capture_output=True' if you want to inspect stdout/stderr programmatically
            # Otherwise, 'capture_output=False' allows subprocess output to print directly.
            result = subprocess.run(cmd, check=check, text=True, capture_output=False) 
            return result
        except subprocess.CalledProcessError as e:
            self.print_colored(f"Command failed with exit code {e.returncode}", RED)
            # You can print error details if needed
            # self.print_colored(f"STDOUT:\n{e.stdout}", RED)
            # self.print_colored(f"STDERR:\n{e.stderr}", RED)
            return None
            
    def install_dependencies(self) -> bool:
        """Install required test dependencies from requirements files"""
        self.print_colored("Installing dependencies...", GREEN)
        
        # Define paths to requirements files relative to the script's directory (docker/)
        core_req_path = self.script_dir / "requirements.txt"
        dev_req_path = self.script_dir / "requirements-dev.txt"
        
        # Upgrade pip first
        cmd = [self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"]
        if self.run_command(cmd) is None:
            return False

        # Install core dependencies
        if core_req_path.exists():
            cmd = [self.python_cmd, "-m", "pip", "install", "-r", str(core_req_path)]
            if self.run_command(cmd) is None:
                self.print_colored(f"Failed to install core dependencies from {core_req_path}", RED)
                return False
        else:
            self.print_colored(f"Warning: {core_req_path} not found. Skipping core dependency installation.", YELLOW)
            
        # Install development dependencies
        if dev_req_path.exists():
            cmd = [self.python_cmd, "-m", "pip", "install", "-r", str(dev_req_path)]
            if self.run_command(cmd) is None:
                self.print_colored(f"Failed to install dev dependencies from {dev_req_path}", RED)
                return False
        else:
            self.print_colored(f"Warning: {dev_req_path} not found. Skipping dev dependency installation.", YELLOW)
            
        self.print_colored("Dependencies installed successfully.", GREEN)
        return True
        
    def check_dependencies(self) -> bool:
        """Check if pytest is installed by attempting to run pytest --version"""
        try:
            # We don't need capture_output for a simple check, just ensure it runs
            subprocess.run([self.python_cmd, "-m", "pytest", "--version"], 
                         check=True, capture_output=True, text=True) # Capture output to keep terminal clean
            return True
        except subprocess.CalledProcessError:
            self.print_colored("pytest not found in the current environment.", YELLOW)
            return False
            
    def format_code(self) -> None:
        """Format code with black"""
        self.print_colored("Formatting code with black...", GREEN)
        # Black should be run from the current directory (docker/)
        # and given the paths to the directories it needs to format.
        cmd = [self.python_cmd, "-m", "black", str(self.api_path), str(self.test_path)]
        self.run_command(cmd, check=False) # Black usually exits with 0 even if it formats files
        
    def run_linting(self) -> None:
        """Run flake8 linting"""
        self.print_colored("Running flake8 linting...", GREEN)
        # Flake8 also runs from the current directory (docker/)
        cmd = [
            self.python_cmd, "-m", "flake8", 
            str(self.api_path), str(self.test_path),
            "--max-line-length=100",
            # Exclude paths relative to the current working directory (docker/)
            # Venv is typically outside docker/, so direct exclude isn't needed here.
            "--exclude=__pycache__,venv,.venv,build,dist" 
            # You might need to adjust exclude if your venv is somewhere else relative to docker/
        ]
        self.run_command(cmd, check=False) # Flake8 exits with non-zero on lint errors, so check=False for just reporting
        
    def run_type_checking(self) -> None:
        """Run mypy type checking"""
        self.print_colored("Running mypy type checking...", GREEN)
        # Mypy should be run from the current directory (docker/)
        cmd = [
            self.python_cmd, "-m", "mypy", 
            str(self.api_path), # Only type-check your API code
            "--ignore-missing-imports", # Often needed for third-party libraries without stubs
            "--allow-untyped-globals" # Add this if you get many errors from untyped global vars
        ]
        self.run_command(cmd, check=False) # Mypy exits non-zero on type errors
        
    def run_tests(self, 
                  coverage: bool = False,
                  verbose: bool = True, # Pytest is verbose by default with -v
                  markers: Optional[str] = None,
                  specific_file: Optional[str] = None,
                  failed_only: bool = False,
                  watch: bool = False) -> None:
        """Run pytest with various options"""
        
        # Pytest will be run from the current working directory (docker/)
        # so test_path and api_path should be 'tests' and 'api'
        
        if not self.test_path.exists():
            self.print_colored(f"Test directory {self.test_path} does not exist! Please check path.", RED)
            return
            
        # Build pytest command
        cmd = [self.python_cmd, "-m"]
        
        if watch:
            cmd.append("pytest_watch")
        else:
            cmd.append("pytest")
            
        # Add test path or specific file (relative to current working directory)
        if specific_file:
            # Ensure specific_file is relative to the current directory (docker/)
            specific_file_path = self.script_dir / specific_file
            if not specific_file_path.exists():
                self.print_colored(f"Specific test file {specific_file_path} does not exist!", RED)
                return
            cmd.append(str(specific_file_path))
        else:
            cmd.append(str(self.test_path)) # Path to 'tests' directory
            
        # Add options
        if verbose:
            cmd.append("-v")
            
        cmd.append("--color=yes")
        
        if coverage:
            # --cov path should be relative to pytest's rootdir, which is 'docker/' here
            cmd.extend([
                "--cov=api", # Changed from f"--cov={self.api_path}" to "api"
                "--cov-report=html",
                "--cov-report=term"
            ])
            
        if markers:
            cmd.extend(["-m", markers])
            
        if failed_only:
            cmd.append("--lf")
            
        if watch:
            cmd.append("--clear")
            
        # Run tests
        self.print_colored("Running tests...", GREEN)
        result = self.run_command(cmd) # check=True by default now, will exit on failure
        
        if result and result.returncode == 0:
            self.print_colored("All tests passed! ✅", GREEN)
        else:
            self.print_colored("Some tests failed! ❌", RED)
            
        if coverage:
            # htmlcov will be created in the current directory (docker/)
            self.print_colored("Coverage report generated in htmlcov/index.html", YELLOW)
            
    def run_all_checks(self) -> None:
        """Run all checks: format, lint, type-check, and test"""
        self.print_colored("Running full build pipeline...", GREEN)
        
        # Ensure dependencies are installed before running checks
        if not self.install_dependencies():
            self.print_colored("Failed to install dependencies. Aborting build pipeline.", RED)
            return
            
        # Format (fixes issues before linting)
        self.format_code()
        
        # Lint
        self.run_linting()
        
        # Type check
        self.run_type_checking()
        
        # Test with coverage
        self.run_tests(coverage=True)
        
        self.print_colored("Build pipeline completed!", GREEN)
        
    def clean(self) -> None:
        """Clean up cache and temporary files"""
        self.print_colored("Cleaning up temporary files...", GREEN)
        
        # Patterns relative to the directory where the script is run (docker/)
        # or relative to the project root for .venv
        patterns = [
            "**/__pycache__",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/htmlcov",
            "**/*.pyc",
            "**/.coverage"
        ]
        
        # Clean within the 'docker' directory
        for pattern in patterns:
            # Use self.script_dir for globbing relative to the script's location
            for path in self.script_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        # Also clean the virtual environment if it's in the project root
        venv_path = self.project_root / ".venv"
        if venv_path.exists() and venv_path.is_dir():
            self.print_colored(f"Removing virtual environment at {venv_path}", YELLOW)
            shutil.rmtree(venv_path)
        
        self.print_colored("Cleanup completed!", GREEN)
        
    def init_project_structure(self) -> None:
        """Initialize project structure with necessary files"""
        self.print_colored("Initializing project structure...", GREEN)
        
        # Create directories relative to the script's location (docker/)
        self.test_path.mkdir(parents=True, exist_ok=True) # docker/tests
        self.api_path.mkdir(parents=True, exist_ok=True) # docker/api
            
        # Create __init__.py in tests (relative to script_dir)
        init_file = self.test_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            self.print_colored(f"Created {init_file}", YELLOW)
            
        # Create pytest.ini (relative to script_dir)
        pytest_ini = self.script_dir / "pytest.ini"
        if not pytest_ini.exists():
            pytest_ini.write_text("""[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra -q --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
""")
            self.print_colored(f"Created {pytest_ini}", YELLOW)
            
        # Create .flake8 (relative to script_dir)
        flake8_config = self.script_dir / ".flake8"
        if not flake8_config.exists():
            flake8_config.write_text("""[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist # Removed venv/.venv as they are typically in project root
ignore = E203,W503,E501
per-file-ignores =
    __init__.py:F401
""")
            self.print_colored(f"Created {flake8_config}", YELLOW)
            
        # Create requirements-dev.txt (relative to script_dir)
        req_dev = self.script_dir / "requirements-dev.txt"
        if not req_dev.exists():
            req_dev.write_text("""# Development dependencies
pytest>=7.4.0
pytest-mock>=3.11.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-watch>=4.2.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
httpx>=0.25.0
""") # Added httpx, as it's common in FastAPI dev/test
            self.print_colored(f"Created {req_dev}", YELLOW)
            
        # Create requirements.txt (relative to script_dir)
        req_core = self.script_dir / "requirements.txt"
        if not req_core.exists():
            req_core.write_text("""# Core dependencies (example from your previous messages)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
aiokafka==0.10.0
confluent-kafka==2.3.0
boto3==1.29.7
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
httpx==0.25.2
""")
            self.print_colored(f"Created {req_core}", YELLOW)
            
        self.print_colored("Project structure initialized!", GREEN)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test runner for Order Processor API")
    
    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("-m", "--markers", help="Run tests with specific markers")
    test_parser.add_argument("-f", "--file", help="Run specific test file (e.g., tests/test_my_feature.py)")
    test_parser.add_argument("--failed", action="store_true", help="Run only failed tests")
    test_parser.add_argument("-w", "--watch", action="store_true", help="Run in watch mode (requires pytest-watch)")
    
    # Other commands
    subparsers.add_parser("install", help="Install test dependencies")
    subparsers.add_parser("format", help="Format code with black")
    subparsers.add_parser("lint", help="Run linting (flake8)")
    subparsers.add_parser("type-check", help="Run type checking (mypy)")
    subparsers.add_parser("build", help="Run full build pipeline (format, lint, type-check, test)")
    subparsers.add_parser("clean", help="Clean temporary files and virtual environment")
    subparsers.add_parser("init", help="Initialize project structure with necessary config files")
    
    args = parser.parse_args()
    
    # Create runner
    runner = TestRunner()
    
    # Execute command
    if args.command == "test":
        # The script assumes a virtual environment is ALREADY activated.
        # It checks if pytest is available in the current environment.
        if not runner.check_dependencies():
            runner.print_colored("pytest not found. Please activate your virtual environment and install dependencies.", RED)
            runner.print_colored("You can run 'python run_tests.py install' first.", YELLOW)
            sys.exit(1) # Exit if essential dependencies aren't found
            
        runner.run_tests(
            coverage=args.coverage,
            markers=args.markers,
            specific_file=args.file,
            failed_only=args.failed,
            watch=args.watch
        )
    elif args.command == "install":
        runner.install_dependencies()
    elif args.command == "format":
        runner.format_code()
    elif args.command == "lint":
        runner.run_linting()
    elif args.command == "type-check":
        runner.run_type_checking()
    elif args.command == "build":
        runner.run_all_checks()
    elif args.command == "clean":
        runner.clean()
    elif args.command == "init":
        runner.init_project_structure()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()