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

## 🔌 **Port Configuration Design**

### **Port Architecture Decision: Different Ports for Container vs Service**

**Decision**: Use different ports at different layers for better production readiness and Kubernetes best practices.

**Port Configuration:**
```
Frontend Container: Port 3000 (development standard)
Kubernetes Service: Port 80 (production standard)
External Access: localhost:3000 via port forwarding
```

### **Why This Design?**

#### **✅ Benefits:**
1. **Production Standards**: Kubernetes services use standard ports (80, 443)
2. **Service Abstraction**: Service layer abstracts container port details
3. **Load Balancer Compatibility**: Standard ports work better with cloud infrastructure
4. **Kubernetes Best Practices**: Follows Kubernetes design patterns
5. **Development Workflow**: Frontend container runs on familiar port 3000
6. **Port Flexibility**: Can change container port without affecting service configuration

#### **❌ Alternative (Same Port) Issues:**
1. **Port Conflicts**: Port 3000 might conflict with other local services
2. **Production Mismatch**: Production environments expect services on standard ports
3. **Load Balancer Issues**: Some load balancers expect services on port 80/443
4. **Kubernetes Convention**: Services typically use standard ports

### **Current Port Configuration:**

| Service | Container Port | Service Port | Target Port | NodePort | External Access |
|---------|----------------|--------------|-------------|----------|-----------------|
| Frontend | 3000 | 80 | 3000 | 30004 | localhost:3000 (port-forward) |
| Gateway | 8000 | 8000 | 8000 | 30000 | localhost:30000 |
| User Service | 8000 | 8000 | 8000 | 30001 | localhost:30001 |
| Inventory Service | 8001 | 8001 | 8001 | 30002 | localhost:30002 |
| Order Service | 8002 | 8002 | 8002 | 30003 | localhost:30003 |

### **Port Forwarding for Frontend:**
```bash
# Access frontend on localhost:3000
kubectl port-forward -n order-processor service/frontend 3000:80

# Or use our management script
./kubernetes/scripts/k8s-manage.sh port-forward
```

### **Configuration Files:**
- **Deployment**: `containerPort: 3000`, health checks on port 3000
- **Service**: `port: 80`, `targetPort: 3000`
- **Health Probes**: All check port 3000 (container port)

---

## 🚀 **Quick Start**

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
   ```