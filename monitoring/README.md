# 📊 Monitoring & Observability

> Comprehensive monitoring stack with Prometheus, Grafana, and Loki for system health, performance metrics, and business intelligence

## 🚀 Quick Start
- **Prerequisites**: Kubernetes cluster, Helm, kubectl
- **Deploy Stack**: `kubectl create namespace monitoring` then `helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring`
- **Access Grafana**: Port forward with `kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80`
- **Get Credentials**: `kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`

## ✨ Key Features
- **Metrics Collection**: Prometheus-based time-series data collection
- **Visualization**: Rich Grafana dashboards for system and business metrics
- **Log Aggregation**: Loki-based centralized logging with correlation
- **Alerting**: Comprehensive alerting with AlertManager
- **Infrastructure Monitoring**: Kubernetes and AWS service metrics

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/monitoring-design.md)
- [Application Metrics (plan + PromQL)](../docs/METRICS.md)
- [Prometheus Configuration](#prometheus-configuration)
- [Grafana Dashboards](#grafana-dashboards)
- [Alerting Rules](#alerting-rules)

## 📊 Status
- **Current Status**: 🔄 **READY FOR DEPLOYMENT** - All components configured and ready
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **Ready for Implementation**
- **Infrastructure**: Complete Prometheus stack configuration ready
- **Service Integration**: Metrics collection from all microservices configured
- **Dashboard Templates**: Pre-configured Grafana dashboards prepared
- **Alerting Rules**: Comprehensive alerting configuration defined

### 🔄 **Next Steps (MONITOR-001)**
- **Phase 1**: Deploy Prometheus stack to Kubernetes
- **Phase 2**: Implement request ID middleware and structured logging
- **Phase 3**: Create business metrics collection and dashboards

---

## 📁 Project Structure

```
monitoring/
├── prometheus/           # Prometheus configuration
├── grafana/             # Grafana dashboards and configuration
├── alertmanager/        # Alert routing and notification
├── kube-state-metrics/  # Kubernetes resource metrics
└── node-exporter/       # Infrastructure metrics
```

## 🔧 Prometheus Configuration

### **Scrape Intervals**
- **Infrastructure**: 15s (Node Exporter, Kube State Metrics)
- **Applications**: 30s (Service metrics endpoints)
- **Custom Metrics**: 60s (Business metrics)

### **Retention & Storage**
- **Metrics**: 15 days retention
- **Logs**: 7 days retention
- **Storage**: Local storage with persistent volume options

### **Service Discovery**
```yaml
# Kubernetes service discovery
kubernetes_sd_configs:
  - role: pod
    namespaces:
      names: ["order-processor"]
```

## 📊 Grafana Dashboards

### **System Health Dashboard**
- Service status and health indicators
- Response time percentiles (P50, P95, P99)
- Error rate trends and alerts
- Resource utilization graphs

### **Business Operations Dashboard**
- Trading volume and order statistics
- User registration and activity metrics
- Portfolio performance indicators
- Asset price and balance trends

### **Infrastructure Dashboard**
- Kubernetes cluster health
- AWS service metrics and costs
- Network performance and latency
- Storage and memory utilization

## 🚨 Alerting Rules

### **Critical Alerts**
- Service down or unhealthy
- High error rate (>5% for 5 minutes)
- Response time degradation (>2x normal)

### **Warning Alerts**
- Performance degradation
- Resource usage approaching limits
- Business metrics anomalies

### **Notification Channels**
- **Slack**: Team notifications for critical alerts
- **Email**: Escalation for unresolved issues
- **PagerDuty**: On-call engineer notifications

## 📈 Metrics Collection

### **Application Metrics**
- **Metric list and PromQL:** [docs/METRICS.md](../docs/METRICS.md)
- **Endpoints:** Gateway `GET /metrics`; each backend `GET /internal/metrics`; plus `GET /health`, `GET /health/ready`, `GET /health/live`

### **Business Metrics (Planned)**
- **Trading Operations**: Orders created, executed, cancelled
- **User Activity**: Registrations, logins, transactions
- **Portfolio Performance**: Asset balance changes, P&L tracking

### **Infrastructure Metrics**
- **Kubernetes**: Pod status, resource usage, node health
- **AWS Services**: DynamoDB performance, EKS cluster health
- **Network**: Request rates, latency, bandwidth usage

## 🔍 Logging & Tracing

### **Structured Logging Format**
```json
{
  "timestamp": "2025-08-20T10:00:00Z",
  "level": "INFO",
  "service": "user_service",
  "request_id": "uuid-123-456-789",
  "username": "username",
  "message": "User balance updated",
  "context": {
    "operation": "deposit",
    "amount": 100.00
  }
}
```

### **Log Correlation**
- **Request IDs**: Unique identifiers across service boundaries
- **Correlation IDs**: Link related operations
- **Centralized Storage**: Loki-based log aggregation
- **Search & Analysis**: Full-text search and visualization

## 🚀 Deployment

### **Helm Installation**
```bash
# Create namespace
kubectl create namespace monitoring

# Install Prometheus stack
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring

# Verify deployment
kubectl get pods -n monitoring
```

### **Port Forwarding**
```bash
# Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Prometheus
kubectl port-forward svc/monitoring-kube-prometheus-stack-prometheus -n monitoring 9090:9090
```

### **Access URLs**
- **Grafana**: http://localhost:3000 (admin / <password>)
- **Prometheus**: http://localhost:9090

## 🔄 Maintenance

### **Regular Tasks**
- Update Prometheus and Grafana versions
- Review and optimize alerting rules
- Monitor storage usage and retention
- Validate dashboard accuracy

### **Performance Optimization**
- Optimize Prometheus query performance
- Implement metric cardinality limits
- Use recording rules for complex queries
- Monitor and adjust scrape intervals

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.
