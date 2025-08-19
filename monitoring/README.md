# 📊 Monitoring & Observability System

## 🎯 **System Overview**

This directory contains the monitoring and observability infrastructure for the Cloud Native Order Processor system. The monitoring stack provides comprehensive visibility into system health, performance, and business metrics.

## 🏗️ **Current Architecture**

### **Monitoring Stack Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │      Loki      │
│   (Metrics)     │◄──►│   (Dashboards)  │◄──►│   (Logs)       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  AlertManager   │    │ Node Exporter   │    │Kube State      │
│   (Alerts)      │    │(Infrastructure) │    │ Metrics        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Component Status**
- **Prometheus**: ✅ Defined, ready for deployment
- **Grafana**: ✅ Defined, ready for deployment
- **Loki**: ✅ Defined, ready for deployment
- **AlertManager**: ✅ Defined, ready for deployment
- **Node Exporter**: ✅ Defined, ready for deployment
- **Kube State Metrics**: ✅ Defined, ready for deployment

## 📊 **Current Monitoring Status**

### **✅ What's Already Working**
- **Service Metrics**: All services expose Prometheus metrics at `/metrics`
- **Health Checks**: Comprehensive health endpoints on all services
- **Basic Observability**: Service status and basic performance metrics

### **🔄 What's Ready for Implementation**
- **Infrastructure**: Complete Prometheus stack configuration
- **Service Integration**: Metrics collection from all microservices
- **Dashboard Templates**: Pre-configured Grafana dashboards

### **📋 What's Planned (MONITOR-001)**
- **Request Tracing**: Unique request IDs across service boundaries
- **Structured Logging**: Consistent JSON logging with correlation
- **Business Metrics**: Trading operations, portfolio performance
- **Alerting**: Proactive monitoring and incident response

## 🚀 **Quick Start**

### **1. Deploy Monitoring Stack**
```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Deploy Prometheus stack
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring

# Verify deployment
kubectl get pods -n monitoring
```

### **2. Access Monitoring Interfaces**
```bash
# Port forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Port forward Prometheus
kubectl port-forward svc/monitoring-kube-prometheus-stack-prometheus -n monitoring 9090:9090

# Access in browser
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### **3. Get Grafana Credentials**
```bash
# Get admin password
kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# Default login: admin / <password from above>
```

## 📁 **Directory Structure**

```
monitoring/
├── prometheus/           # Prometheus configuration
│   ├── README.md        # Prometheus deployment guide
│   └── values.yaml      # Helm values for Prometheus stack
├── grafana/             # Grafana dashboards and configuration
│   └── dashboards/      # Pre-configured dashboard templates
├── alertmanager/        # Alert routing and notification
│   └── config.yaml     # Alert rules and routing
├── kube-state-metrics/  # Kubernetes resource metrics
├── node-exporter/       # Infrastructure metrics
└── README.md            # This file
```

## 🔧 **Configuration**

### **Prometheus Configuration**
- **Scrape Interval**: 15s for infrastructure, 30s for applications
- **Retention**: 15 days for metrics, 7 days for logs
- **Storage**: Local storage (can be upgraded to persistent volumes)

### **Grafana Dashboards**
- **System Health**: Service status, response times, error rates
- **Business Metrics**: Trading operations, user activity, portfolio performance
- **Infrastructure**: Kubernetes resources, AWS service metrics

### **Alerting Rules**
- **Service Down**: Alert when any service becomes unavailable
- **High Error Rate**: Alert when error rate exceeds threshold
- **Performance Degradation**: Alert when response times degrade
- **Resource Usage**: Alert when resources approach limits

## 📈 **Metrics Collection**

### **Application Metrics**
```python
# Current metrics endpoints
GET /metrics                    # Prometheus metrics
GET /health                    # Service health status
GET /health/ready             # Readiness probe
GET /health/live              # Liveness probe
```

### **Business Metrics (Planned)**
- **Trading Operations**: Orders created, executed, cancelled
- **User Activity**: Registrations, logins, transactions
- **Portfolio Performance**: Asset balance changes, P&L tracking
- **System Performance**: Response times, throughput, error rates

### **Infrastructure Metrics**
- **Kubernetes**: Pod status, resource usage, node health
- **AWS Services**: DynamoDB performance, EKS cluster health
- **Network**: Request rates, latency, bandwidth usage

## 🔍 **Logging & Tracing (Planned)**

### **Request Tracing**
```python
# Planned request ID propagation
X-Request-ID: uuid-123-456-789
X-Correlation-ID: uuid-987-654-321

# Structured logging format
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

### **Log Aggregation**
- **Loki**: Centralized log storage and querying
- **Correlation**: Link logs across services using request IDs
- **Search**: Full-text search across all service logs
- **Visualization**: Log analysis in Grafana dashboards

## 🚨 **Alerting & Notifications**

### **Alert Categories**
- **Critical**: Service down, high error rates
- **Warning**: Performance degradation, resource usage
- **Info**: Business metrics, system events

### **Notification Channels**
- **Slack**: Team notifications for critical alerts
- **Email**: Escalation for unresolved issues
- **PagerDuty**: On-call engineer notifications

### **Escalation Policies**
- **Immediate**: Critical alerts to on-call engineers
- **Delayed**: Warning alerts with 15-minute delay
- **Business Hours**: Info alerts during business hours

## 📊 **Dashboard Examples**

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

## 🔄 **Maintenance & Updates**

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

## 📚 **Additional Resources**

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Loki Documentation**: https://grafana.com/docs/loki/
- **Kubernetes Monitoring**: https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/

## 🎯 **Next Steps (MONITOR-001)**

### **Phase 1: Infrastructure Deployment**
- [ ] Deploy Prometheus stack to Kubernetes
- [ ] Configure service discovery and scraping
- [ ] Set up basic dashboards and alerts

### **Phase 2: Application Integration**
- [ ] Implement request ID middleware
- [ ] Add structured logging to all services
- [ ] Create business metrics collection

### **Phase 3: Advanced Features**
- [ ] Implement log correlation and tracing
- [ ] Create business intelligence dashboards
- [ ] Set up advanced alerting and escalation

**The monitoring infrastructure is ready for deployment - let's make the system production-ready!** 🚀
