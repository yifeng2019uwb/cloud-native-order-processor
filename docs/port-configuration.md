# Port Configuration

## Port Assignment

| Service | Internal | NodePort | URL | Status |
|---------|----------|----------|-----|---------|
| **Frontend** | 80 | 30003 | http://localhost:30003 | ✅ Active |
| **Grafana** | 3000 | 30001 | http://localhost:30001 | 🔄 Monitoring Stack |
| **Gateway** | 8080 | 30002 | http://localhost:30002 | ✅ Active |
| **User Service** | 8000 | 30004 | http://localhost:30004 | ✅ Active |
| **Inventory Service** | 8001 | 30005 | http://localhost:30005 | ✅ Active |
| **Order Service** | 8002 | 30006 | http://localhost:30006 | ✅ Active |
| **Auth Service** | 8003 | 30007 | http://localhost:30007 | 🚧 Ready for Deployment |

## Monitoring & Logging Stack

| Service | Internal | NodePort | URL | Status |
|---------|----------|----------|-----|---------|
| **Prometheus** | 9090 | 30008 | http://localhost:30008 | 🔄 Monitoring Stack |
| **Loki** | 3100 | 30009 | http://localhost:30009 | 🔄 Logging Stack |
| **Promtail** | 9080 | 30010 | http://localhost:30010 | 🔄 Logging Stack |
| **Alertmanager** | 9093 | 30011 | http://localhost:30011 | 🔄 Monitoring Stack |

## Future Services

| Service | Internal | NodePort | URL | Purpose |
|---------|----------|----------|-----|---------|
| **Elasticsearch** | 9200 | 30012 | http://localhost:30012 | Alternative Logging |
| **Kibana** | 5601 | 30013 | http://localhost:30013 | Alternative Logging UI |

## Rules
- **Internal ports**: Use standard ports (80, 3000, 8080, 8000-8003)
- **NodePorts**: Use 30000+ range (30001, 30002, 30003...)
- **No conflicts**: Each service gets unique internal + NodePort
- **Service grouping**: Core services (8000-8003), Monitoring (3000, 9090, 3100, 9080, 9093)
- **Port allocation**: Reserve 30007 for Auth Service, 30008-30011 for monitoring stack

## Auth Service Architecture

### **Port Assignment:**
- **Internal Port**: 8003 (consistent with service naming convention)
- **NodePort**: 30007 (next available in sequence)
- **Service Type**: Internal-only (ClusterIP for production, NodePort for dev)

### **Communication Flow:**
```
Client → Gateway (30002) → Auth Service (8003) → JWT Validation
Client → Gateway (30002) → Backend Services (8000-8002)
```

### **Security Model:**
- **Auth Service**: Internal-only, validates JWT tokens
- **Gateway**: Public-facing, forwards auth requests to Auth Service
- **Backend Services**: Internal-only, validate Gateway headers

## Quick Commands
```bash
# Check services
kubectl get services -n order-processor

# Check port usage
netstat -tulpn | grep :3000

# Check Auth Service status
kubectl get pods -n order-processor -l component=auth-service

# Check Auth Service logs
kubectl logs -n order-processor -l component=auth-service

# Port forwarding for Auth Service (if needed)
kubectl port-forward -n order-processor svc/auth-service 8003:8003
```
