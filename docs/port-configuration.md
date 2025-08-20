# Port Configuration

## Port Assignment

| Service | Internal | NodePort | URL |
|---------|----------|----------|-----|
| **Frontend** | 80 | 30003 | http://localhost:30003 |
| **Grafana** | 3000 | 30001 | http://localhost:30001 |
| **Gateway** | 8080 | 30002 | http://localhost:30002 |
| **User Service** | 8000 | 30004 | http://localhost:30004 |
| **Inventory Service** | 8001 | 30005 | http://localhost:30005 |
| **Order Service** | 8002 | 30006 | http://localhost:30006 |

## Future Services

| Service | Internal | NodePort | URL |
|---------|----------|----------|-----|
| **Prometheus** | 9090 | 30007 | http://localhost:30007 |
| **Elasticsearch** | 9200 | 30008 | http://localhost:30008 |
| **Kibana** | 5601 | 30009 | http://localhost:30009 |

## Rules
- **Internal ports**: Use standard ports (80, 3000, 8080, 8000-8002)
- **NodePorts**: Use 30000+ range (30001, 30002, 30003...)
- **No conflicts**: Each service gets unique internal + NodePort

## Quick Commands
```bash
# Check services
kubectl get services -n order-processor

# Check port usage
netstat -tulpn | grep :3000
```
