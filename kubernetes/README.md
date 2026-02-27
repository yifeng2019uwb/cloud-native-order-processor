# ☸️ Kubernetes

> Production-ready Kubernetes deployment with Kustomize-based multi-environment configurations for local development and AWS EKS production

## 🚀 Quick Start
- **Prerequisites**: Docker, Kind, kubectl, AWS CLI
- **Local Dev**: `kind create cluster --name order-processor` then `./scripts/deploy.sh --type k8s --environment dev`
- **Production**: Set AWS credentials then `./scripts/deploy.sh --type k8s --environment prod`
- **Access**: Frontend on localhost:30004, Gateway on localhost:30000

## ✨ Key Features
- Multi-environment deployment (dev/prod)
- Kustomize-based configuration management
- Intelligent port configuration
- Secure secrets management
- Production-ready EKS deployment

## 📁 Project Structure
```
kubernetes/
├── base/                      # Base Kubernetes manifests
│   ├── frontend/             # Frontend deployment
│   ├── gateway/              # Gateway deployment
│   ├── services/             # Backend services
│   └── monitoring/           # Monitoring stack
├── overlays/                 # Environment-specific overlays
│   ├── dev/                 # Development configuration
│   └── prod/                # Production configuration
├── scripts/                  # Deployment scripts
│   └── deploy.sh            # Main deployment script
└── README.md                # This file
```

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/kubernetes-design.md)
- [Terraform Documentation](../terraform/README.md)
- [Docker Documentation](../docker/README.md)
- [Services Overview](../services/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All environments configured and working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.