# Build System Documentation

This project includes a universal build system that can be used to build, test, and deploy Python microservices. The build system is designed to be reusable across different services in the project.

## Quick Start

Make the build script executable:
```bash
chmod +x build.sh
```

Build and test the current service:
```bash
./build.sh
```

Or use the Makefile for convenience:
```bash
make build
```

## Build Script Features

The `build.sh` script provides the following features:

- **Universal**: Works with any Python service or package
- **Virtual Environment Management**: Automatically creates and manages virtual environments
- **Dependency Installation**: Handles both service-specific and shared dependencies
- **Testing**: Runs pytest with coverage reporting
- **Linting**: Optional code quality checks with flake8 and black
- **Building**: Creates Python packages (sdist and wheel)
- **Docker Support**: Can build Docker images
- **Clean Builds**: Removes build artifacts

## Usage Examples

### Basic Usage

```bash
# Build current service (auto-detected)
./build.sh

# Build specific service
./build.sh order-service

# Build common package
./build.sh common
```

### Advanced Options

```bash
# Clean build with verbose output
./build.sh --clean --verbose order-service

# Test only (skip building)
./build.sh --test-only

# Build only (skip tests)
./build.sh --build-only

# Install dependencies only
./build.sh --install-deps

# Build with Docker image
./build.sh --docker order-service

# Use specific Python version
./build.sh --python 3.11 order-service

# Set coverage threshold
./build.sh --coverage 90 order-service

# Skip coverage reporting
./build.sh --no-coverage order-service
```

### Using the Makefile

The Makefile provides convenient shortcuts:

```bash
# Show available targets
make help

# Build current service
make build

# Test current service
make test

# Build specific service
make build SERVICE=order-service

# Clean and build
make clean build

# Build all services
make build-all

# Test all services
make test-all

# Setup development environment
make dev-setup

# Run quality assurance
make qa

# CI/CD pipeline
make ci
```

## Project Structure Support

The build system works with the following project structure:

```
project/
├── build.sh                 # Universal build script
├── Makefile                 # Build automation
├── services/
│   ├── common/              # Shared package
│   │   ├── setup.py
│   │   ├── requirements.txt
│   │   └── ...
│   ├── order-service/       # Individual service
│   │   ├── src/
│   │   ├── requirements.txt
│   │   ├── Dockerfile (optional)
│   │   └── ...
│   └── other-services/
└── tests/                   # Global tests (optional)
```

## Configuration

### Environment Variables

You can set the following environment variables to customize the build:

```bash
export PYTHON_VERSION=3.11
export COVERAGE_THRESHOLD=80
export BUILD_DIR=build
export DIST_DIR=dist
```

### Service-Specific Configuration

Each service can have its own configuration files:

- `requirements.txt` - Service dependencies
- `test-requirements.txt` - Test-specific dependencies
- `setup.py` - Package configuration
- `Dockerfile` - Docker image configuration

## Virtual Environment Management

The build system automatically creates and manages virtual environments:

- Virtual environments are created in `.venv-{service-name}` directories
- Dependencies are automatically installed
- The common package is installed in development mode for services that depend on it

## Testing

The build system supports pytest with the following features:

- Automatic test discovery
- Coverage reporting (HTML and terminal)
- Configurable coverage thresholds
- Test-specific dependency installation

### Test Directory Detection

The system looks for tests in the following locations:
1. `tests/` directory
2. `test/` directory  
3. `../tests/` directory (for services)

## Dependency Management

The build system handles dependencies in the following order:

1. **Common package dependencies** (for services that depend on it)
2. **Service-specific dependencies** from `requirements.txt`
3. **Test dependencies** from `test-requirements.txt` or `tests/requirements.txt`
4. **Development installation** of the package itself

## Docker Support

If a `Dockerfile` exists in the service directory, the build system can build Docker images:

```bash
./build.sh --docker order-service
make docker SERVICE=order-service
```

## Code Quality

The build system includes optional code quality checks:

- **flake8**: Code linting and style checking
- **black**: Code formatting (check mode)

Install these tools to enable quality checks:
```bash
pip install flake8 black
```

## Continuous Integration

For CI/CD pipelines, use the `ci` target:

```bash
make ci                    # Run CI for current service
make ci-all               # Run CI for all services
```

This performs:
1. Clean build artifacts
2. Install dependencies
3. Run linting (if tools available)
4. Run tests with coverage
5. Build package

## Troubleshooting

### Common Issues

1. **Python version not found**
   ```bash
   # Install the required Python version
   sudo apt-get install python3.11  # Ubuntu/Debian
   brew install python@3.11         # macOS
   ```

2. **Permission denied**
   ```bash
   chmod +x build.sh
   ```

3. **Import errors in tests**
   - Ensure the common package is properly installed
   - Check that `PYTHONPATH` includes the correct directories
   - Use `--install-deps` to reinstall dependencies

4. **Coverage threshold not met**
   ```bash
   # Lower the threshold temporarily
   ./build.sh --coverage 60 order-service
   
   # Or skip coverage
   ./build.sh --no-coverage order-service
   ```

### Debug Mode

Enable verbose output for debugging:

```bash
./build.sh --verbose order-service
make verbose-build SERVICE=order-service
```

## Customization

### Adding New Services

To add a new service:

1. Create the service directory under `services/`
2. Add `requirements.txt` for dependencies
3. Add `setup.py` if it's a package
4. Add tests in a `tests/` directory
5. The build system will automatically detect and build it

### Extending the Build Script

The build script is modular and can be extended:

1. Add new command-line options in the argument parsing section
2. Create new functions for additional build steps
3. Update the main function to call your new functions

### Custom Make Targets

Add custom targets to the Makefile:

```makefile
my-custom-target: ## Description of custom target
	@./build.sh --