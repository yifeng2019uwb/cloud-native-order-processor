# Kubernetes Deployment Package

This directory contains Kubernetes configurations for deploying the Order Processor application to different environments.

## Structure

```
kubernetes/
├── base/                    # Shared base configurations
│   ├── namespace.yaml       # Common namespace
│   ├── service-account.yaml # Service account + RBAC
│   ├── redis.yaml          # Redis deployment and service
│   ├── kustomization.yaml   # Base kustomize config
│   └── README.md           # Base documentation
├── dev/                     # Local development overlay
│   ├── deployment.yaml     # Local deployments
│   ├── service.yaml        # NodePort services
│   ├── values.yaml         # Local configuration
│   ├── kustomization.yaml  # Local kustomize config
│   └── README.md           # Local deployment guide
├── secrets/                 # Sensitive manifests (hidden, .gitignored)
│   ├── deployment_dev.yaml # Dev deployments with secrets
│   ├── credentials-secret.yaml # Example secret manifest
│   └── kustomization.yaml  # Kustomize config for secrets
├── prod/                    # Production (AWS EKS)
│   ├── deployment.yaml     # Production deployments
│   ├── service.yaml        # ClusterIP services
│   ├── ingress.yaml        # AWS ALB ingress
│   ├── secrets.yaml        # Production secrets
│   ├── values.yaml         # Production configuration
│   ├── kustomization.yaml  # Production kustomize config
│   └── README.md           # Production deployment guide
├── scripts/                 # Deployment automation
│   ├── deploy-local.sh     # Deploy to local cluster
│   ├── deploy-prod.sh      # Deploy to production
│   ├── cleanup.sh          # Cleanup deployments
│   └── port-forward.sh     # Port forwarding utilities
└── README.md               # This file
```

## Quick Start

### Local Development (Kind) ✅ **WORKING**

1. **Create Kind cluster**:
   ```bash
   kind create cluster --name order-processor
   ```

2. **Deploy to local**:
   ```bash
   ./scripts/deploy.sh --type k8s --environment dev
   ```

3. **Access services**:
   - Frontend: http://localhost:30004
   - Gateway: http://localhost:30000
   - User Service: http://localhost:8000 (via port-forward)
   - Inventory Service: http://localhost:8001 (via port-forward)

### Production (AWS EKS)

1. **Set environment variables**:
   ```bash
   export AWS_ACCOUNT_ID="your-account-id"
   export AWS_REGION="us-east-1"
   ```

2. **Deploy to production**:
   ```bash
   ./scripts/deploy.sh --type k8s --environment prod
   ```

3. **Access services**:
   - Frontend: https://order-processor.yourdomain.com
   - API: https://api.order-processor.yourdomain.com

## Prerequisites

### Local Development
- [Docker](https://docs.docker.com/get-docker/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### Production
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- AWS EKS cluster
- AWS ECR repositories
- SSL certificate in AWS Certificate Manager

## Configuration

### Environment-Specific Settings

| Setting | Local | Production |
|---------|-------|------------|
| Replicas | 1 | 2 |
| Resources | 128Mi-256Mi | 512Mi-1Gi |
| Service Type | NodePort | ClusterIP |
| Load Balancer | None | AWS ALB |
| SSL | No | Yes |
| Image Source | Local Docker | AWS ECR |

### Port Mappings ✅ **UPDATED**

| Service | Container Port | Service Port | NodePort | External Access |
|---------|----------------|--------------|----------|-----------------|
| Frontend | 80 | 80 | 30004 | http://localhost:30004 |
| Gateway | 8080 | 8080 | 30000 | http://localhost:30000 |
| User Service | 8000 | 8000 | - | Port-forward: 8000:8000 |
| Inventory Service | 8001 | 8001 | - | Port-forward: 8001:8001 |
| Redis | 6379 | 6379 | - | Internal only |

### Secrets Management ✅ **WORKING**

Both environments require AWS credentials for DynamoDB access:

```bash
# AWS Credentials (Fresh) ✅ **WORKING**
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_ROLE_ARN=<your-role-arn>
```

**Note**: These credentials are automatically deployed via the deployment script and are fresh (not expired).

## Deployment Scripts

### `deploy.sh` ✅ **WORKING**
- Builds Docker images
- Loads images into Kind cluster
- Deploys to local environment
- Shows access URLs

### `deploy-prod.sh`
- Builds and tags Docker images
- Pushes to AWS ECR
- Deploys to production environment
- Shows ingress status

### `cleanup.sh`
- Removes deployments
- Usage: `./cleanup.sh [local|prod|all]`

## Troubleshooting

### Common Issues

1. **Images not found**:
   ```bash
   # Rebuild and reload images
   ./scripts/deploy.sh --type k8s --environment dev
   ```

2. **Secrets not configured**:
   ```bash
   # Check secrets
   kubectl get secrets -n order-processor
   kubectl describe secret aws-credentials -n order-processor
   ```

3. **Services not accessible**:
   ```bash
   # Check service status
   kubectl get svc -n order-processor
   kubectl describe svc user-service -n order-processor
   ```

4. **AWS credential issues** ✅ **RESOLVED**:
   ```bash
   # Fresh credentials are automatically deployed
   # Check service logs for any issues
   kubectl logs deployment/user-service -n order-processor
   kubectl logs deployment/inventory-service -n order-processor
   ```

### Useful Commands

```bash
# Check deployment status
kubectl get all -n order-processor

# View logs
kubectl logs <pod-name> -n order-processor

# Describe resources
kubectl describe pod <pod-name> -n order-processor
kubectl describe svc <service-name> -n order-processor

# Port forward (if needed)
kubectl port-forward svc/user-service 8000:8000 -n order-processor
kubectl port-forward svc/inventory-service 8001:8001 -n order-processor
```

## Development Workflow

1. **Local Development**:
   - Use Docker for rapid development
   - Use Kind for Kubernetes testing
   - Test integration with local deployment

2. **Production Deployment**:
   - Build and test locally first
   - Deploy to production when ready
   - Monitor deployment status

## Security Notes

- dev/ and secrets/ directories are excluded from version control (.gitignore) to prevent accidental exposure of sensitive or local-only configuration.
- Production uses non-root containers
- Secrets are stored in Kubernetes secrets
- SSL/TLS enabled in production
- Network policies can be added for additional security

## Cost Optimization

- Local development is free (Kind)
- Production uses appropriate resource limits
- Consider spot instances for cost savings
- Monitor usage with CloudWatch

## Current Status ✅ **WORKING**

### **✅ All Services Deployed Successfully**
- **Frontend**: React application with Nginx ✅
- **Gateway**: Go API Gateway with authentication ✅
- **User Service**: FastAPI authentication service ✅
- **Inventory Service**: FastAPI inventory service ✅
- **Redis**: In-memory cache and session store ✅

### **✅ AWS Integration Working**
- **Fresh AWS Credentials**: Deployed and working ✅
- **DynamoDB Access**: All services can access database ✅
- **No Expired Token Errors**: Credentials are current ✅

### **✅ Port Configuration Correct**
- **External Access**: Frontend and Gateway accessible via NodePorts ✅
- **Internal Communication**: Services communicate via ClusterIP ✅
- **Port Forwarding**: Available for direct service access ✅

### **✅ Deployment Process Stable**
- **Automated Deployment**: Single command deployment ✅
- **Image Building**: Docker images built and loaded ✅
- **Service Discovery**: All services can find each other ✅

---

**The Kubernetes deployment is now working perfectly with fresh AWS credentials and proper service configuration!** 🚀