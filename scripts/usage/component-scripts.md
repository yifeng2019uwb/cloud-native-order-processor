# 🔧 Component Scripts

> Package-level build and test scripts

## 🚀 Quick Start
```bash
# Frontend
./frontend/build.sh --test-only

# Gateway
./gateway/build.sh --build-only

# Services
./services/build.sh user_service
```

## 🎨 Frontend Package

```bash
# Build and test (default)
./frontend/build.sh

# Build only, skip tests
./frontend/build.sh --build-only

# Run tests only, skip building
./frontend/build.sh --test-only

# Clean build
./frontend/build.sh --clean
```

## 🚪 Gateway Package

```bash
# Build and test (default)
./gateway/build.sh

# Build only, skip tests
./gateway/build.sh --build-only

# Run tests only, skip building
./gateway/build.sh --test-only

# Development workflow
./gateway/dev.sh run
./gateway/dev.sh test
./gateway/dev.sh stop
```

## 🐍 Services Package

```bash
# Build and test all services
./services/build.sh

# Build and test specific service
./services/build.sh user_service
./services/build.sh inventory_service
./services/build.sh order_service

# Build only, skip tests
./services/build.sh --build-only user_service
```

## 🔧 Common Features

All scripts support:
```bash
--help              # Show help
--build-only        # Build only, skip tests
--test-only         # Test only, skip building
--verbose           # Verbose output
--clean             # Clean build artifacts
```

## 🔍 Troubleshooting

```bash
# Frontend build failures
node --version
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Gateway build failures
go version
go clean -cache
go mod tidy

# Services build failures
python --version
source venv/bin/activate
pip install -r requirements.txt
```

---

**Note**: For system-wide automation, see other usage guides.
