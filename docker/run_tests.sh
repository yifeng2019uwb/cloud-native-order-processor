#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PYTHON_VERSION="3.11" # Specify your desired Python version (e.g., 3.11, 3.12)
# The virtual environment will still be created in the project root (one level up)
PROJECT_ROOT=$(dirname "$(dirname "$0")") # Go up two levels from script location (from docker/ to project_root/)
VENV_DIR="$PROJECT_ROOT/.venv"
# All other paths (requirements.txt, requirements-dev.txt, pytest.ini, api/, tests/)
# are now relative to the script's current directory (cloud-native-order-processor/docker/)

# --- 1. Create and Activate Virtual Environment ---
echo "--- Creating/Updating Virtual Environment ---"
# Check if a specific Python version executable exists
if command -v python${PYTHON_VERSION} &> /dev/null; then
    python_cmd="python${PYTHON_VERSION}"
elif command -v python3 &> /dev/null; then
    python_cmd="python3"
else
    echo "Error: Python 3.x or python${PYTHON_VERSION} not found. Please install Python."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    "$python_cmd" -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo "Virtual environment activated."

# --- 2. Install Project Dependencies ---
echo "--- Installing Dependencies ---"
"$python_cmd" -m pip install --upgrade pip

# Install core dependencies (from requirements.txt, which is now a sibling to this script)
if [ -f "requirements.txt" ]; then
    echo "Installing core dependencies from requirements.txt"
    pip install -r "requirements.txt"
else
    echo "Error: requirements.txt not found in $(pwd). Please check your path and file."
    exit 1 # Exit if core requirements are not found
fi

# Install development and testing dependencies (from requirements-dev.txt, also a sibling)
if [ -f "requirements-dev.txt" ]; then
    echo "Installing dev/test dependencies from requirements-dev.txt"
    pip install -r "requirements-dev.txt"
else
    echo "Error: requirements-dev.txt not found in $(pwd). Please check your path and file."
    exit 1 # Exit if dev requirements are not found (as tests won't run)
fi

echo "Dependencies installation complete."

# --- NEW STEP: Run Code Formatter (Black) ---
echo "--- Running Code Formatter (Black) ---"
if command -v black &> /dev/null; then
    echo "Attempting to format code with Black on api/ and tests/ directories..."
    
    BLACK_OUTPUT=$(black api tests 2>&1 || true)
    
    echo "$BLACK_OUTPUT"
    
    if echo "$BLACK_OUTPUT" | grep -q "reformatted"; then
        echo "Black reported reformatting files. Code formatting complete. ✅"
    elif echo "$BLACK_OUTPUT" | grep -q "files left unchanged"; then
        echo "Black reported no files needed reformatting. Code is already formatted. ✨"
    else
        echo "Black ran, but its output was unexpected. Please review the output above for any errors. ⚠️"
    fi
else
    echo "Black not found. Skipping code formatting."
    echo "Please ensure 'black' is in requirements-dev.txt and installed (you can run 'pip install -r requirements-dev.txt' manually if needed)."
fi

# --- NEW STEP: Create/Update .flake8 configuration for Linting ---
echo "--- Ensuring .flake8 configuration is in place ---"
FLAKE8_CONFIG_FILE="./.flake8" # Relative to the script's current directory (docker/)

# This creates or overwrites the .flake8 file with the desired ignored warnings.
# IMPORTANT: No comments are allowed on the 'ignore' line itself, only on separate lines.
cat << EOF > "$FLAKE8_CONFIG_FILE"
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,venv,.venv
ignore = E203,W503,E501,W291,W293
per-file-ignores =
    __init__.py:F401
EOF
echo "Created/Updated $FLAKE8_CONFIG_FILE with W291 and W293 warnings ignored for flake8. ✨"


# --- 3. Run Linting (Optional, if flake8 is in requirements-dev.txt) ---
echo "--- Running Linting ---"
# Ensure flake8 is installed before trying to run it
if pip show flake8 > /dev/null 2>&1; then
    echo "Running flake8..."
    # 'api' and 'tests' are now relative to the current directory (docker/)
    # flake8 will now pick up the .flake8 config created above
    flake8 api tests --max-line-length=100 --exclude=__pycache__,venv,.venv
    echo "Linting complete."
else
    echo "flake8 not found. Skipping linting (likely due to missing requirements-dev.txt)."
fi

# --- 4. Run Tests with Coverage ---
echo "--- Running Tests ---"
# We are already in the 'docker' directory where pytest.ini, tests/, and api/ are located.
pytest -v # Use the simplified command as addopts is in pytest.ini
echo "Tests complete."

# --- Optional: Upload coverage reports (Local run only) ---
echo "Coverage report generated at coverage.xml (in the current directory: $(pwd))"

# --- 5. Deactivate Virtual Environment ---
deactivate
echo "Virtual environment deactivated."

echo "All tasks completed successfully!"