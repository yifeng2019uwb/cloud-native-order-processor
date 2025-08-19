# Scripts Directory

This directory contains comprehensive scripts for building, testing, deploying, and managing the Cloud Native Order Processor system.

## 📑 Table of Contents

- [📋 Quick Start](#-quick-start)
- [📦 Package-Level Scripts](#-package-level-scripts)
- [🚀 Service Management](#-service-management)
- [🧪 Testing & Validation](#-testing--validation)
- [🏗️ Build & Deploy](#️-build--deploy)
- [🧹 Cleanup & Maintenance](#-cleanup--maintenance)
- [🔧 Infrastructure & Configuration](#-infrastructure--configuration)
- [📚 Shared Utilities](#-shared-utilities)
- [📖 Documentation](#-documentation)
- [💰 Cost Management](#-cost-management)
- [🔧 Prerequisites](#-prerequisites)

## 📋 Quick Start

```bash
# Start all services locally
./scripts/manage-services.sh start all

# Run full CI/CD pipeline locally
./scripts/test-local.sh --environment dev --all

# Quick build and deploy
./scripts/deploy.sh --type k8s --environment dev
```

## 📦 Package-Level Scripts

Each package has its own professional build and development scripts:

```bash
# Frontend Development
./frontend/build.sh --test-only          # Test frontend
./frontend/build.sh --build-only         # Build frontend

# Gateway Development
./gateway/build.sh --test-only           # Test gateway
./gateway/dev.sh run --port 9090        # Run gateway on custom port

# Python Services
./services/build.sh user_service         # Build user service
./services/build.sh --test-only common  # Test common package
```

**See [Component Build Scripts](#component-build-scripts--comprehensive) section for complete details.**

## 🚀 Service Management

### manage-services.sh

A comprehensive script to start, stop, restart, and monitor all services locally.

```bash
# Start all services
./scripts/manage-services.sh start all

# Check status
./scripts/manage-services.sh status

# Stop all services
./scripts/manage-services.sh stop all

# View logs
./scripts/manage-services.sh logs inventory-service
```

**Features:**
- ✅ **Frontend** (React/Vite) - Port 3000
- ✅ **User Service** (FastAPI) - Port 8000
- ✅ **Inventory Service** (FastAPI) - Port 8001
- Automatic dependency installation
- Virtual environment detection
- Process management with PID tracking
- Comprehensive logging
- Colored output for better readability

## 🧪 Testing & Validation

### test-local.sh ✅ **NEW - MIRRORS CI/CD**

Mirrors the CI/CD pipeline locally for pre-push validation.

```bash
# Full pipeline (build → deploy → test → destroy)
./scripts/test-local.sh --environment dev --all

# Development cycle (keeps infrastructure running)
./scripts/test-local.sh --environment dev --dev-cycle

# App-only deployment (assumes infra exists)
./scripts/test-local.sh --environment dev --app-only

# Component-level testing
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services
```

**Environments:**
- **`dev`** - Local FastAPI services (development)
- **`prod`** - EKS + Kubernetes (full infrastructure)

**Component Testing:**
- **`--frontend`** - Build and test frontend only
- **`--gateway`** - Build and test gateway only
- **`--services`** - Build and test all Python services
- **`--component <name>`** - Test specific component

### test-integration.sh

Run integration tests against deployed infrastructure.

```bash
./scripts/test-integration.sh --environment dev
```

### build-test-frontend.sh

Build and test the frontend application.

```bash
./scripts/build-test-frontend.sh
```

## 🏗️ Build & Deploy

### deploy.sh ✅ **UPDATED**

Universal deployment script for services, infrastructure, and Kubernetes.

```bash
# Deploy to Kubernetes (development)
./scripts/deploy.sh --type k8s --environment dev

# Deploy infrastructure only
./scripts/deploy.sh --type infra --environment dev

# Deploy specific service
./scripts/deploy.sh --type service --service user
```

**What it does:**
- **k8s**: Builds Docker images, loads to Kind, deploys to Kubernetes
- **infra**: Deploys AWS infrastructure with Terraform
- **service**: Deploys specific service (user/inventory)

### Component Build Scripts ✅ **COMPREHENSIVE**

Each component has its own dedicated build script with professional-grade features:

#### **Frontend Package (`frontend/build.sh`)**
```bash
# Build and test frontend (default)
./frontend/build.sh

# Build only, skip tests
./frontend/build.sh --build-only

# Run tests only, skip building
./frontend/build.sh --test-only

# Verbose output
./frontend/build.sh --verbose
```

**Features:**
- ✅ **Node.js version validation** (requires 18+)
- ✅ **Dependency installation** with npm
- ✅ **Build optimization** with Vite
- ✅ **Testing** with comprehensive test suite
- ✅ **Error handling** with colored output
- ✅ **Prerequisites checking** for Node.js and npm

#### **Gateway Package (`gateway/build.sh`)**
```bash
# Build and test gateway (default)
./gateway/build.sh

# Build only, skip tests
./gateway/build.sh --build-only

# Run tests only, skip building
./gateway/build.sh --test-only

# Verbose output
./gateway/build.sh --verbose
```

**Features:**
- ✅ **Go version validation** (requires 1.24+)
- ✅ **Cross-platform builds** (Linux, macOS, Windows)
- ✅ **Dependency management** with go mod
- ✅ **Testing** with coverage reporting
- ✅ **Binary optimization** for production
- ✅ **Clean build artifacts** management

#### **Gateway Development (`gateway/dev.sh`)**
```bash
# Install dependencies
./gateway/dev.sh install

# Build binary
./gateway/dev.sh build

# Run development server
./gateway/dev.sh run

# Run tests with coverage
./gateway/dev.sh test

# Stop running gateway
./gateway/dev.sh stop

# Custom port
./gateway/dev.sh --port 9090 run
```

**Features:**
- ✅ **Development workflow** management
- ✅ **Hot reload** capabilities
- ✅ **Port configuration** (default: 8080)
- ✅ **Redis integration** setup
- ✅ **Environment variable** support
- ✅ **Process management** with PID tracking

#### **Services Package (`services/build.sh`)**
```bash
# Build and test all services (default)
./services/build.sh

# Build and test specific service
./services/build.sh user_service
./services/build.sh inventory_service
./services/build.sh order_service
./services/build.sh common
./services/build.sh exception

# Build only, skip tests
./services/build.sh --build-only user_service

# Run tests only, skip building
./services/build.sh --test-only inventory_service

# Verbose output
./services/build.sh --verbose order_service
```

**Features:**
- ✅ **Python version validation** (requires 3.11+)
- ✅ **Virtual environment** management
- ✅ **Dependency installation** with pip
- ✅ **Testing** with pytest and coverage
- ✅ **Service-specific builds** or all services
- ✅ **Build artifact** management
- ✅ **Error handling** and validation

#### **Individual Service Scripts**
Each service can also be built independently:
```bash
# User Service
cd services/user_service && python -m pip install -e .
cd services/user_service && python -m pytest

# Inventory Service
cd services/inventory_service && python -m pip install -e .
cd services/inventory_service && python -m pytest

# Order Service
cd services/order_service && python -m pip install -e .
cd services/order_service && python -m pytest
```

#### **Common Script Features**
All package-level scripts share consistent interfaces:
- ✅ **Help/Usage**: `-h, --help` with detailed examples
- ✅ **Color-coded output**: Green (success), Red (error), Yellow (warning), Blue (info)
- ✅ **Verbose mode**: `-v, --verbose` for detailed logging
- ✅ **Build/Test separation**: `--build-only`, `--test-only` options
- ✅ **Prerequisites checking**: Validate required tools before execution
- ✅ **Error handling**: `set -e` with clear error messages
- ✅ **Cross-platform**: Works on Linux, macOS, and Windows

**💡 Pro Tip**: All scripts follow the same pattern - use `-h` or `--help` to see usage for any script!

### quick_build.sh

Quick ECR build and push for immediate deployment.

```bash
./scripts/quick_build.sh
```

**What it does:**
- Creates ECR repository if needed
- Builds Docker image
- Pushes to ECR with timestamped and latest tags

### deploy-app.sh

Deploy application to infrastructure.

```bash
./scripts/deploy-app.sh --environment dev
./scripts/deploy-app.sh --environment prod --skip-build
```

**What it does:**
- **dev**: Runs/Builds local FastAPI services
- **prod**: Builds Docker image, pushes to ECR, deploys to EKS

### deploy-docker.sh

Deploy using Docker Compose for local/development environments.

**Purpose**: Simple, consistent Docker deployment for development environment

**Usage**:
```bash
# Build + Deploy all services
./scripts/deploy-docker.sh -bd all

# Build + Deploy specific service
./scripts/deploy-docker.sh -bd frontend-dev
./scripts/deploy-docker.sh -bd user_service
./scripts/deploy-docker.sh -bd inventory_service
./scripts/deploy-docker.sh -bd order_service
./scripts/deploy-docker.sh -bd gateway

# Build only
./scripts/deploy-docker.sh -b frontend-dev

# Deploy only (uses existing images)
./scripts/deploy-docker.sh -d frontend-dev
```

**Features**:
- ✅ **Simple interface**: `-b` (build), `-d` (deploy), `-bd` (both)
- ✅ **Service selection**: Individual services or `all`
- ✅ **Development focused**: Uses `docker-compose.dev.yml`
- ✅ **Health checks**: Waits for services to be healthy
- ✅ **Clear logging**: Colored output with progress indicators
- ✅ **Error handling**: Validates arguments and prerequisites

**Service Names**:
- `frontend-dev` - React frontend application
- `user_service` - User authentication and management
- `inventory_service` - Asset inventory management
- `order_service` - Order processing and portfolio management
- `gateway` - API Gateway with authentication and routing
- `all` - All services

**Testing Status**: ✅ **FULLY TESTED** - All scenarios verified working correctly

### ecr_build_push.sh

Build and push Docker images to ECR.

```bash
./scripts/ecr_build_push.sh
```

## 🧹 Cleanup & Maintenance

### destroy.sh

Destroy all AWS resources created by Terraform.

```bash
./scripts/destroy.sh --environment dev --force
./scripts/destroy.sh --environment prod --force
```

**Important:** Always run with `--force` to avoid ongoing AWS charges!

### workspace-cleanup.sh

Emergency cleanup script for workspace.

```bash
./scripts/workspace-cleanup.sh
```

## 🔧 Infrastructure & Configuration

### validate-environment.sh

Validate environment setup and prerequisites.

```bash
./scripts/validate-environment.sh
```

### generate-k8s-config.sh

Generate Kubernetes configuration files.

```bash
./scripts/generate-k8s-config.sh
```

### full-cycle-local.sh

Complete local development cycle script.

```bash
./scripts/full-cycle-local.sh
```

## 📚 Shared Utilities

### shared/prerequisites-checker.sh

Check and validate system prerequisites.

```bash
./scripts/shared/prerequisites-checker.sh
```

## 📖 Documentation

### build-test-deploy.md

Complete guide for the full build → deploy → test → destroy cycle.

**Key workflows:**
- **Daily Development**: Deploy once, iterate on app
- **Pre-Push Validation**: Full pipeline testing
- **Production Simulation**: EKS-based testing

## 💰 Cost Management

### Cost Estimates:
- **dev environment**: ~$1-5/day when running
- **prod environment**: ~$10-30/day when running

### Cost Control:
```bash
# Always clean up when done
./scripts/destroy.sh --environment dev --force

# Emergency cleanup
./scripts/workspace-cleanup.sh
```

## 🔧 Prerequisites

### Required Tools:
- Terraform (>= 1.5.0)
- AWS CLI (>= 2.0.0)
- Docker (running daemon)
- Node.js and npm
- Python 3.11+
- Go 1.24+
- jq (for JSON parsing)

### AWS Setup:
```bash
# Configure credentials
aws configure

# Verify access
aws sts get-caller-identity
```

## 🎯 Common Workflows

### Daily Development
```bash
# Start services locally
./scripts/manage-services.sh start all

# Or use Docker
./scripts/deploy-docker.sh

# Or use Kubernetes
./scripts/deploy.sh --type k8s --environment dev
```

### Pre-Push Validation
```bash
# Full validation
./scripts/test-local.sh --environment dev --all

# Production simulation
./scripts/test-local.sh --environment prod --all

# Component testing
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services
```

### Infrastructure Deployment
```bash
# Deploy infrastructure
./scripts/deploy.sh --type infra --environment dev

# Deploy application
./scripts/deploy.sh --type k8s --environment dev

# Clean up when done
./scripts/destroy.sh --environment dev --force
```

### Quick Iteration
```bash
# Component-level development
./frontend/build.sh --test-only
./gateway/build.sh --test-only
./services/build.sh --test-only

# Or use development cycle
./scripts/test-local.sh --environment dev --dev-cycle
```

## 🐛 Troubleshooting

### Common Issues:

**Infrastructure conflicts:**
```bash
./scripts/destroy.sh --environment dev --force
```

**Terraform state issues:**
```bash
cd terraform
terraform destroy -auto-approve
```

**Docker build failures:**
```bash
./scripts/deploy.sh --type k8s --environment dev --no-cache
```

**AWS credential issues:**
```bash
aws configure
aws sts get-caller-identity
```

**Service startup issues:**
```bash
./scripts/manage-services.sh status
./scripts/manage-services.sh logs [service-name]
```

**Component build issues:**
```bash
# Check individual component builds
./frontend/build.sh -v
./gateway/build.sh -v
./services/build.sh -v
```

## 📋 Script Summary

| Script | Purpose | Use Case |
|--------|---------|----------|
| `manage-services.sh` | Local service management | Daily development |
| `test-local.sh` | CI/CD pipeline mirror | Pre-push validation |
| `deploy.sh` | Universal deployment | Infrastructure & app deployment |
| `destroy.sh` | Resource cleanup | Cost control |
| `quick_build.sh` | Fast ECR build | Quick iteration |
| `validate-environment.sh` | Environment validation | Setup verification |
| `workspace-cleanup.sh` | Emergency cleanup | Troubleshooting |

### Component Build Scripts ✅ **NEW**

| Script | Purpose | Use Case |
|--------|---------|----------|
| `frontend/build.sh` | Frontend build & test | Frontend development |
| `gateway/build.sh` | Gateway build & test | Gateway development |
| `services/build.sh` | Services build & test | Backend development |

## 🚀 Makefile Integration ✅ **NEW**

The Makefile provides convenient shortcuts for common operations:

```bash
# Quick development cycle
make dev-cycle

# Build all components
make build

# Test all components
make test

# Deploy to Kubernetes
make deploy-k8s

# Port forwarding
make port-forward

# Cleanup
make cleanup-dev
```

### Makefile Targets:

**Development:**
- `make dev-cycle` - Complete development cycle
- `make quick-cycle` - Quick build and test cycle

**Build & Test:**
- `make build` - Build all components
- `make test` - Test all components
- `make test-local` - Run local tests

**Deployment:**
- `make deploy-k8s` - Deploy to Kubernetes
- `make port-forward` - Set up port forwarding

**Cleanup:**
- `make cleanup-dev` - Clean up development environment

---

**Remember:** Always run `destroy.sh --force` when done to avoid unexpected AWS charges!

### Quick Start

```bash
# Make the script executable (if not already done)
chmod +x scripts/manage-services.sh

# Start all services
./scripts/manage-services.sh start all

# Check status
./scripts/manage-services.sh status

# Stop all services
./scripts/manage-services.sh stop all
```

### Usage

```bash
./scripts/manage-services.sh [COMMAND] [SERVICE]
```

### Commands

- `start` - Start a service or all services
- `stop` - Stop a service or all services
- `restart` - Restart a service or all services
- `status` - Show status of all services
- `logs` - Show logs for a specific service
- `help` - Show help message

### Services

- `all` - All services (frontend, user-service, inventory-service)
- `frontend` - React frontend application
- `user-service` - FastAPI user authentication service
- `inventory-service` - FastAPI inventory management service

### Examples

```bash
# Start all services
./scripts/manage-services.sh start all

# Start only frontend
./scripts/manage-services.sh start frontend

# Stop only user service
./scripts/manage-services.sh stop user-service

# Restart inventory service
./scripts/manage-services.sh restart inventory-service

# Check status of all services
./scripts/manage-services.sh status

# View frontend logs
./scripts/manage-services.sh logs frontend

# View inventory service logs
./scripts/manage-services.sh logs inventory-service
```

### Features

- **Automatic dependency installation** - Installs npm dependencies if missing
- **Virtual environment detection** - Automatically finds and activates Python virtual environments
- **Process management** - Tracks PIDs and ensures clean shutdown
- **Logging** - Captures all service logs in `logs/` directory
- **Status monitoring** - Shows running status with colored output
- **Port management** - Handles port conflicts automatically
- **Error handling** - Graceful error handling and recovery

### Log Files

All service logs are stored in the `logs/` directory:
- `logs/frontend.log` - Frontend development server logs
- `logs/user-service.log` - User service logs
- `logs/inventory-service.log` - Inventory service logs

### Ports

- **Frontend**: 3000 (or next available port)
- **User Service**: 8000
- **Inventory Service**: 8001

## 📋 Complete Scripts Reference

### **Root-Level Scripts** (in `scripts/` directory)
| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy-docker.sh` | Docker Compose deployment | `./scripts/deploy-docker.sh -bd all` |
| `deploy.sh` | Universal deployment (K8s/infra) | `./scripts/deploy.sh --type k8s --environment dev` |
| `test-local.sh` | Local CI/CD pipeline | `./scripts/test-local.sh --environment dev --all` |
| `smoke-test.sh` | Health checks | `./scripts/smoke-test.sh` |
| `cli-client.sh` | API testing client | `./scripts/cli-client.sh` |
| `destroy.sh` | Infrastructure cleanup | `./scripts/destroy.sh --environment dev --force` |
| `validate-environment.sh` | Environment validation | `./scripts/validate-environment.sh` |

### **Package-Level Scripts** (in each package directory)
| Package | Script | Purpose | Usage |
|---------|--------|---------|-------|
| **Frontend** | `build.sh` | Build & test | `./frontend/build.sh --test-only` |
| **Gateway** | `build.sh` | Build & test | `./gateway/build.sh --build-only` |
| **Gateway** | `dev.sh` | Development workflow | `./gateway/dev.sh run --port 9090` |
| **Services** | `build.sh` | All Python services | `./services/build.sh user_service` |
| **User Service** | `setup.py` | Individual build | `cd services/user_service && python -m pip install -e .` |
| **Inventory Service** | `setup.py` | Individual build | `cd services/inventory_service && python -m pytest` |
| **Order Service** | `setup.py` | Individual build | `cd services/order_service && python -m pytest` |

### **Quick Reference Commands**
```bash
# 🚀 Start everything
./scripts/deploy-docker.sh -bd all

# 🧪 Test everything
./scripts/test-local.sh --environment dev --all

# 🏗️ Build specific component
./frontend/build.sh --test-only
./gateway/build.sh --build-only
./services/build.sh user_service

# 🧹 Clean up everything
./scripts/destroy.sh --environment dev --force
```

### Prerequisites

- Node.js and npm installed
- Python 3.11+ installed
- Virtual environments set up for Python services
- AWS credentials configured (for backend services)