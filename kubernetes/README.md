# ☸️ Kubernetes Deployment

> Production-ready Kubernetes deployment with Kustomize-based multi-environment configurations for local development and AWS EKS production

## 🚀 Quick Start
- **Prerequisites**: Docker, Kind, kubectl
- **Local Development**: `kind create cluster --name order-processor` then `./scripts/deploy.sh --type k8s --environment dev`
- **Production**: Set AWS credentials then `./scripts/deploy.sh --type k8s --environment prod`
- **Access**: Frontend on localhost:30004, Gateway on localhost:30000

## ✨ Key Features
- **Multi-Environment**: Local development and production configurations
- **Kustomize-Based**: DRY principle with environment-specific overlays
- **Port Management**: Intelligent port configuration for dev/prod
- **Secrets Management**: Secure AWS credentials and configuration
- **Production Ready**: EKS deployment with ingress and load balancing

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/kubernetes-design.md)
- [Port Configuration](#port-configuration)
- [Environment Setup](#environment-setup)
- [Deployment Scripts](#deployment-scripts)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All environments configured and working
- **Last Updated**: August 20, 2025

## ⚠️ Common Issues

### Issue 1: Images not found
**Symptoms**: Pods fail to start with "ImagePullBackOff" errors
**Solution**: Rebuild and reload images with `./scripts/deploy.sh --type k8s --environment dev`

### Issue 2: Secrets not configured
**Symptoms**: Services fail to start due to missing AWS credentials
**Solution**: Check secrets with `kubectl get secrets -n order-processor` and verify AWS credentials

### Issue 3: Port conflicts
**Symptoms**: Can't access services on expected ports
**Solution**: Check port usage with `netstat -tulpn | grep :3000` and use port forwarding

---

## 📁 Project Structure

```
kubernetes/
├── base/                    # Shared base configurations
├── dev/                     # Local development overlay
├── prod/                    # Production (AWS EKS)
└── scripts/                 # Deployment automation
```

## 🔌 Port Configuration

| Service | Container Port | Service Port | NodePort | External Access |
|---------|----------------|--------------|----------|-----------------|
| Frontend | 3000 | 80 | 30004 | http://localhost:30004 |
| Gateway | 8080 | 8080 | 30000 | http://localhost:30000 |
| User Service | 8000 | 8000 | - | Port-forward: 8000:8000 |
| Inventory Service | 8001 | 8001 | - | Port-forward: 8001:8001 |

## 🌍 Environment Setup

### **Local Development**
- **Cluster**: Kind cluster for local testing
- **Services**: NodePort for external access
- **Resources**: Minimal (128Mi-256Mi)
- **Replicas**: 1 for each service

### **Production Environment**
- **Cluster**: AWS EKS
- **Services**: ClusterIP with ingress
- **Resources**: Production (512Mi-1Gi)
- **Replicas**: 2+ for high availability

## 🔐 Secrets Management

```bash
# AWS Credentials required for DynamoDB access
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_ROLE_ARN=<your-role-arn>
```

## 🚀 Deployment Scripts

```bash
# Deploy to local environment
./scripts/deploy.sh --type k8s --environment dev

# Deploy to production
./scripts/deploy.sh --type k8s --environment prod

# Cleanup deployments
./cleanup.sh [local|prod|all]
```

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.