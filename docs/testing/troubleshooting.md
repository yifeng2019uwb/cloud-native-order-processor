# Troubleshooting

## Quick Commands

### Service Health
```bash
docker ps -a
kubectl get pods -A
curl http://localhost:8000/health
```

### Logs
```bash
docker-compose logs [service-name]
kubectl logs [pod-name] -n order-processor
```

### Common Issues
```bash
# Port conflicts
lsof -i :[port]

# AWS credentials
aws sts get-caller-identity

# Kubernetes events
kubectl describe pod [pod-name] -n order-processor
```

### Restart Services
```bash
docker-compose restart
kubectl rollout restart deployment -n order-processor
```
