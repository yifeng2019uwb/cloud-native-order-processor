# 🔧 Scripts & Automation

> Comprehensive automation scripts for building, testing, deploying, and managing the Cloud Native Order Processor system

## 🚀 Quick Start
- **Prerequisites**: Docker, Kubernetes (Kind), AWS CLI, Python 3.11+
- **Start Services**: `./manage-services.sh start all` for local development
- **Full Pipeline**: `./test-local.sh --environment dev --all` for CI/CD validation
- **Deploy**: `./deploy.sh --type k8s --environment dev` for Kubernetes deployment

## ✨ Key Features
- **Service Management**: Start, stop, and monitor all services locally
- **CI/CD Pipeline**: Full build, test, deploy, and destroy automation
- **Multi-Environment**: Support for dev, staging, and production deployments
- **Testing Automation**: Comprehensive testing and validation scripts
- **Infrastructure Management**: AWS and Kubernetes deployment automation

## 🔗 Quick Links
- [Service Management](usage/service-management.md)
- [Testing & Validation](usage/testing-validation.md)
- [Build & Deploy](usage/build-deploy.md)
- [Infrastructure](usage/infrastructure.md)
- [Component Scripts](usage/component-scripts.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All scripts tested and working
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Scripts Working**
- **Service Management**: Local service startup and monitoring
- **CI/CD Pipeline**: Full automation from build to deployment
- **Testing**: Comprehensive validation and smoke testing
- **Deployment**: Docker and Kubernetes deployment automation
- **Infrastructure**: AWS and local environment management

### 🚀 **Ready for Production**
- **Multi-Environment**: Dev, staging, and production support
- **Error Handling**: Comprehensive error handling and validation
- **Logging**: Detailed logging and debugging information
- **Documentation**: Complete usage guides and examples

---

## 📁 Project Structure

```
scripts/
├── README.md                    # This file - main overview
├── usage/                       # Detailed usage documentation
│   ├── service-management.md    # Service management scripts
│   ├── testing-validation.md    # Testing and validation
│   ├── build-deploy.md         # Build and deployment
│   ├── infrastructure.md       # Infrastructure management
│   └── component-scripts.md    # Component-level scripts
├── shared/                      # Shared utilities and functions
├── deploy.sh                    # Main deployment script
├── test-local.sh               # CI/CD pipeline mirror
├── manage-services.sh           # Service management
└── [other scripts]             # Additional automation scripts
```

## 🛠️ Core Scripts

### **Main Deployment Script**
```bash
# Deploy to Kubernetes
./deploy.sh --type k8s --environment dev

# Deploy to Docker
./deploy.sh --type docker --environment dev

# Production deployment
./deploy.sh --type k8s --environment prod
```

### **Service Management**
```bash
# Start all services
./manage-services.sh start all

# Check status
./manage-services.sh status

# View logs
./manage-services.sh logs user-service
```

### **Testing & Validation**
```bash
# Full CI/CD pipeline
./test-local.sh --environment dev --all

# Development cycle
./test-local.sh --environment dev --dev-cycle

# Component testing
./test-local.sh --frontend
```

## 🔧 Prerequisites

### **Required Tools**
- **Docker**: Container runtime
- **Kubernetes**: Kind cluster for local development
- **AWS CLI**: AWS service management
- **Python 3.11+**: Service development and testing
- **Node.js 18+**: Frontend development

### **Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup AWS credentials
./update-aws-credentials.sh

# Create Kind cluster
kind create cluster --name order-processor
```

## 📚 Usage Documentation

### **Service Management**
- [Service Management Guide](usage/service-management.md) - Start, stop, and monitor services
- [Component Scripts](usage/component-scripts.md) - Package-level build and test scripts

### **Testing & Deployment**
- [Testing & Validation](usage/testing-validation.md) - CI/CD pipeline and testing automation
- [Build & Deploy](usage/build-deploy.md) - Build and deployment automation

### **Infrastructure**
- [Infrastructure Management](usage/infrastructure.md) - AWS and Kubernetes management

---

**Note**: This is a focused README for quick start and essential information. For detailed usage information, see the individual usage guides in the `usage/` directory.