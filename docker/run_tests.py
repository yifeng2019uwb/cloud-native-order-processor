#!/usr/bin/env python3
"""
Test Runner Script for Order Processor API
Runs all tests in the docker/tests directory with various options
"""

import os
import sys
import subprocess
import argparse
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
    
    def __init__(self, test_path: str = "docker/tests", api_path: str = "docker/api"):
        self.test_path = Path(test_path)
        self.api_path = Path(api_path)
        self.python_cmd = sys.executable
        
    def print_colored(self, message: str, color: str = NC) -> None:
        """Print colored message"""
        print(f"{color}{message}{NC}")
        
    def run_command(self, cmd: List[str], check: bool = True) -> Optional[subprocess.CompletedProcess]:
        """Run a command and return the result"""
        try:
            self.print_colored(f"Running: {' '.join(cmd)}", BLUE)
            result = subprocess.run(cmd, check=check, text=True, capture_output=False)
            return result
        except subprocess.CalledProcessError as e:
            self.print_colored(f"Command failed with exit code {e.returncode}", RED)
            return None
            
    def install_dependencies(self) -> bool:
        """Install required test dependencies"""
        self.print_colored("Installing test dependencies...", GREEN)
        
        deps = [
            "pytest>=7.4.0",
            "pytest-mock>=3.11.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-watch>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0"
        ]
        
        cmd = [self.python_cmd, "-m", "pip", "install"] + deps
        result = self.run_command(cmd)
        return result is not None
        
    def check_dependencies(self) -> bool:
        """Check if pytest is installed"""
        try:
            subprocess.run([self.python_cmd, "-m", "pytest", "--version"], 
                         check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def format_code(self) -> None:
        """Format code with black"""
        self.print_colored("Formatting code with black...", GREEN)
        cmd = [self.python_cmd, "-m", "black", str(self.api_path), str(self.test_path)]
        self.run_command(cmd, check=False)
        
    def run_linting(self) -> None:
        """Run flake8 linting"""
        self.print_colored("Running flake8 linting...", GREEN)
        cmd = [
            self.python_cmd, "-m", "flake8", 
            str(self.api_path), str(self.test_path),
            "--max-line-length=100",
            "--exclude=__pycache__"
        ]
        self.run_command(cmd, check=False)
        
    def run_type_checking(self) -> None:
        """Run mypy type checking"""
        self.print_colored("Running mypy type checking...", GREEN)
        cmd = [
            self.python_cmd, "-m", "mypy", 
            str(self.api_path),
            "--ignore-missing-imports"
        ]
        self.run_command(cmd, check=False)
        
    def run_tests(self, 
                  coverage: bool = False,
                  verbose: bool = True,
                  markers: Optional[str] = None,
                  specific_file: Optional[str] = None,
                  failed_only: bool = False,
                  watch: bool = False) -> None:
        """Run pytest with various options"""
        
        if not self.test_path.exists():
            self.print_colored(f"Test directory {self.test_path} does not exist!", RED)
            return
            
        # Build pytest command
        cmd = [self.python_cmd, "-m"]
        
        if watch:
            cmd.append("pytest_watch")
        else:
            cmd.append("pytest")
            
        # Add test path or specific file
        if specific_file:
            cmd.append(specific_file)
        else:
            cmd.append(str(self.test_path))
            
        # Add options
        if verbose:
            cmd.append("-v")
            
        cmd.append("--color=yes")
        
        if coverage:
            cmd.extend([
                f"--cov={self.api_path}",
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
        result = self.run_command(cmd)
        
        if result and result.returncode == 0:
            self.print_colored("All tests passed! ✅", GREEN)
        else:
            self.print_colored("Some tests failed! ❌", RED)
            
        if coverage:
            self.print_colored("Coverage report generated in htmlcov/index.html", YELLOW)
            
    def run_all_checks(self) -> None:
        """Run all checks: format, lint, type-check, and test"""
        self.print_colored("Running full build pipeline...", GREEN)
        
        # Format
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
        
        patterns = [
            "**/__pycache__",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/htmlcov",
            "**/*.pyc",
            "**/.coverage"
        ]
        
        for pattern in patterns:
            for path in Path(".").glob(pattern):
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                    
        self.print_colored("Cleanup completed!", GREEN)
        
    def init_project_structure(self) -> None:
        """Initialize project structure with necessary files"""
        self.print_colored("Initializing project structure...", GREEN)
        
        # Create directories
        self.test_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = self.test_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            
        # Create pytest.ini
        pytest_ini = Path("pytest.ini")
        if not pytest_ini.exists():
            pytest_ini.write_text("""[pytest]
testpaths = docker/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra -q --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
""")
            
        # Create .flake8
        flake8_config = Path(".flake8")
        if not flake8_config.exists():
            flake8_config.write_text("""[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,.venv,build,dist
ignore = E203,W503
""")
            
        # Create requirements-dev.txt
        req_dev = Path("requirements-dev.txt")
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
""")
            
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
    test_parser.add_argument("-f", "--file", help="Run specific test file")
    test_parser.add_argument("--failed", action="store_true", help="Run only failed tests")
    test_parser.add_argument("-w", "--watch", action="store_true", help="Run in watch mode")
    
    # Other commands
    subparsers.add_parser("install", help="Install test dependencies")
    subparsers.add_parser("format", help="Format code with black")
    subparsers.add_parser("lint", help="Run linting")
    subparsers.add_parser("type-check", help="Run type checking")
    subparsers.add_parser("build", help="Run full build pipeline")
    subparsers.add_parser("clean", help="Clean temporary files")
    subparsers.add_parser("init", help="Initialize project structure")
    
    args = parser.parse_args()
    
    # Create runner
    runner = TestRunner()
    
    # Execute command
    if args.command == "test":
        if not runner.check_dependencies():
            runner.print_colored("pytest not found. Installing dependencies...", YELLOW)
            runner.install_dependencies()
            
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