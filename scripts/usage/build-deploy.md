# 🏗️ Build & Deploy

> Build and deploy to different environments

## 🚀 Quick Start
```bash
# Kubernetes deployment
./deploy.sh --type k8s --environment dev

# Docker deployment
./deploy.sh --type docker --environment dev

# Infrastructure deployment
./deploy.sh --type infra --environment dev
```

## 🐳 Docker Deployment

```bash
# Build and deploy all services
./deploy-docker.sh -bd all

# Build and deploy specific service
./deploy-docker.sh -bd frontend-dev
./deploy-docker.sh -bd user_service
./deploy-docker.sh -bd gateway
```

## ☸️ Kubernetes Deployment

```bash
# Create Kind cluster
kind create cluster --name order-processor

# Deploy to Kind
./deploy.sh --type k8s --environment dev

# Port forward for access
kubectl port-forward svc/frontend 30004:80 -n order-processor
kubectl port-forward svc/gateway 30000:8080 -n order-processor
```

## 🔧 Component Deployment

```bash
# Frontend
./frontend/build.sh --build-only
./deploy.sh --type k8s --environment dev --service frontend

# Gateway
./gateway/build.sh --build-only
./deploy.sh --type k8s --environment dev --service gateway

# Services
./services/build.sh --build-only
./deploy.sh --type k8s --environment dev --service user_service
```

## 🔍 Validation

```bash
# Health checks
./smoke-test.sh
curl http://localhost:3000/health
curl http://localhost:8080/health

# Kubernetes status
kubectl get pods -n order-processor
```

---

**Note**: For local development, see Service Management guide.
