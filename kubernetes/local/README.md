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

3. **AWS credentials configured** (for DynamoDB access):
   - Update `secrets.yaml` with your AWS credentials
   - Base64 encode your credentials:
     ```bash
     echo -n "your-access-key" | base64
     echo -n "your-secret-key" | base64
     ```

## Deployment

### 1. Apply base configuration:
```bash
kubectl apply -k ../base
```

### 2. Update secrets with your credentials:
Edit `secrets.yaml` and replace the placeholder values with your actual base64-encoded AWS credentials.

### 3. Deploy to local cluster:
```bash
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
- AWS credentials required for DynamoDB access