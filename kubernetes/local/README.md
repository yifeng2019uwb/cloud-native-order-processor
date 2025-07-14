# Local Kubernetes Deployment

This directory contains the local Kubernetes configurations for deploying the Order Processor application to a Kind cluster.

## Prerequisites

1. **Kind cluster running**:
   ```bash
   kind create cluster --name order-processor
   ```

2. **Docker images built**:
   ```bash
   # Build images for local deployment
   docker-compose -f ../docker/docker-compose.dev.yml build
   ```

3. **AWS infrastructure deployed** (for DynamoDB access):
   - Run `terraform apply` in the terraform directory
   - This creates the IAM role and DynamoDB tables
   - Uses your existing AWS credentials (local/GitHub) for role assumption

## Deployment

### 1. Deploy using the automated script (Recommended):
```bash
./scripts/deploy-local-k8s.sh
```

This script will:
- Get the role ARN from Terraform outputs
- Update Kubernetes deployment files
- Apply all configurations
- Wait for pods to be ready

### 2. Manual deployment (Alternative):
```bash
# Apply base configuration
kubectl apply -k ../base

# Deploy to local cluster
kubectl apply -k .
```

### 4. Verify deployment:
```bash
kubectl get all -n order-processor
```

## Access Points

After deployment, the services will be available at:

- **Frontend**: http://localhost:30000
- **User Service**: http://localhost:30001
- **Inventory Service**: http://localhost:30002

## Configuration

### Environment Variables
- `ENVIRONMENT`: development
- `AWS_REGION`: us-east-1
- `AWS_ROLE_ARN`: Automatically set from Terraform outputs
- `JWT_SECRET`: local-dev-secret-key

### Resources
- **User Service**: 128Mi-256Mi memory, 100m-200m CPU
- **Inventory Service**: 128Mi-256Mi memory, 100m-200m CPU
- **Frontend**: 64Mi-128Mi memory, 50m-100m CPU

### Health Checks
- Liveness probes on `/health` endpoints
- Readiness probes for service availability
- 30s initial delay, 10s period for liveness
- 5s initial delay, 5s period for readiness

## Troubleshooting

### Check pod status:
```bash
kubectl get pods -n order-processor
kubectl describe pod <pod-name> -n order-processor
```

### Check logs:
```bash
kubectl logs <pod-name> -n order-processor
kubectl logs -f <pod-name> -n order-processor
```

### Check services:
```bash
kubectl get svc -n order-processor
kubectl describe svc <service-name> -n order-processor
```

## Cleanup

To remove the deployment:
```bash
kubectl delete -k .
```

## Notes

- Uses `imagePullPolicy: Never` to use local Docker images
- NodePort services for external access
- Minimal resource allocation for local development
- Uses STS role assumption with existing AWS credentials
- Role ARN automatically retrieved from Terraform outputs