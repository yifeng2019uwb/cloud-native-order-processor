# 📊 Log Aggregation Setup - Loki + Grafana

> Centralized log collection, storage, and querying for your microservices with beautiful web interface

## 🎯 What This Gives You

### **Instead of Command Line:**
```bash
# Current way - hard to use
grep "login_failed" logs/*.json
tail -f services/user_service/logs/app.log
```

### **With Web Interface:**
- 🌐 **Beautiful Web UI** - View logs in browser at http://localhost:3000
- 🔍 **Powerful Search** - Query by user, service, action, error type
- 📊 **Real-time Streaming** - See logs as they happen
- 📈 **Dashboards** - Create custom views for different teams
- 🚨 **Alerting** - Get notified of errors automatically

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Services │    │      Promtail   │    │      Loki       │
│   (JSON Logs)   │───▶│  (Log Shipper)  │───▶│ (Log Database)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │     Grafana     │
                                               │   (Web UI)      │
                                               └─────────────────┘
```

## 🚀 Quick Setup (Docker Compose)

### **1. Create Log Aggregation Stack**
Create `monitoring/docker-compose.logs.yml`:

```yaml
version: '3.8'

services:
  # Loki - Log database
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki:/etc/loki
      - loki-data:/loki
    networks:
      - monitoring

  # Promtail - Log shipper
  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./promtail:/etc/promtail
      - ../services:/var/log/services:ro  # Mount your services logs
      - /var/log:/var/log:ro              # System logs
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - monitoring

  # Grafana - Web interface
  grafana:
    image: grafana/grafana:10.1.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - loki
    networks:
      - monitoring

volumes:
  loki-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

### **2. Configure Loki**
Create `monitoring/loki/local-config.yaml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

# Retention - keep logs for 30 days
limits_config:
  retention_period: 720h  # 30 days
```

### **3. Configure Promtail (Log Shipper)**
Create `monitoring/promtail/config.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # FastAPI JSON logs from your services
  - job_name: fastapi-services
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi-services
          __path__: /var/log/services/*/logs/*.log

    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            timestamp: timestamp
            level: level
            service: service
            request_id: request_id
            action: action
            message: message
            user: user
            duration_ms: duration_ms

      # Extract labels for filtering
      - labels:
          service:
          level:
          action:
          user:

      # Set timestamp
      - timestamp:
          source: timestamp
          format: RFC3339

  # Docker container logs (if running in Docker)
  - job_name: docker-containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s

    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        target_label: container_name
      - source_labels: [__meta_docker_container_log_stream]
        target_label: log_stream

    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            service: service
            message: message
      - labels:
          service:
          level:
```

### **4. Configure Grafana Data Source**
Create `monitoring/grafana/provisioning/datasources/loki.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
    version: 1
    editable: false
```

### **5. Update Your Services to Output Logs**
Update your `services/.env` to configure log output:

```bash
# Add to services/.env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=/var/log/services
```

Update your service logging to write to files:

```python
# services/common/src/logging/base_logger.py
import json
import os
import logging
from datetime import datetime
from pathlib import Path

class BaseLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name

        # Setup file logging
        log_dir = Path(os.getenv("LOG_FILE_PATH", "logs"))
        log_dir.mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        # File handler
        log_file = log_dir / f"{service_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)

        # Console handler (for development)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)

    def log(self, level: str, action: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.service_name,
            "action": action,
            "message": message,
            **kwargs
        }

        # Output as JSON
        self.logger.info(json.dumps(log_entry))
```

## 🔍 How to Use - Web Interface

### **1. Start the Stack**
```bash
cd monitoring
docker-compose -f docker-compose.logs.yml up -d
```

### **2. Access Grafana**
- Open http://localhost:3000
- Login: `admin` / `admin123`
- Go to "Explore" tab

### **3. Example Queries**

**View all logs from user service:**
```logql
{service="user_service"}
```

**Find all login failures:**
```logql
{service="user_service", action="login_failed"}
```

**Search for specific user activity:**
```logql
{service="user_service"} |= "john_doe"
```

**Find all errors across services:**
```logql
{level="ERROR"}
```

**Get slow requests (>1000ms):**
```logql
{service="user_service"} | json | duration_ms > 1000
```

**Authentication failures in last hour:**
```logql
{action="auth_failed"} [1h]
```

**Count orders by user:**
```logql
count by (user) ({action="create_order_success"})
```

## 📊 Create Dashboards

### **1. Security Dashboard**
```logql
# Failed login attempts
{action="login_failed"}

# Successful logins by user
count by (user) ({action="login_success"})

# Suspicious activity
{action="suspicious_activity"}
```

### **2. Business Operations Dashboard**
```logql
# Order creation rate
rate({action="create_order_success"}[5m])

# Deposit/withdrawal activity
{action=~"deposit_success|withdraw_success"}

# Balance changes
{action="balance_change"}
```

### **3. Performance Dashboard**
```logql
# Average response time
avg by (service, action) ({duration_ms > 0} | json | unwrap duration_ms)

# Error rate
rate({level="ERROR"}[5m])

# Request volume
rate({level="INFO"}[5m])
```

## 🚨 Set Up Alerts

### **1. Create Alert Rules**
In Grafana, create alerts for:

```logql
# Too many failed logins
rate({action="login_failed"}[5m]) > 0.1

# High error rate
rate({level="ERROR"}[5m]) > 0.05

# Slow requests
{duration_ms > 5000}

# Service down
absent_over_time({service="user_service"}[5m])
```

### **2. Notification Channels**
- **Slack**: Get alerts in your team channel
- **Email**: Critical alerts via email
- **Discord**: Alternative team notifications

## 🎯 Benefits for Your Project

### **✅ Professional Setup**
- Enterprise-grade log management
- Shows understanding of observability
- Perfect for portfolio demonstration

### **✅ Easy Debugging**
- Click through logs instead of grep commands
- See request flow across services
- Identify patterns in errors

### **✅ Business Intelligence**
- Track user behavior patterns
- Monitor trading activity
- Identify popular features

### **✅ Security Monitoring**
- Failed authentication attempts
- Suspicious user activity
- Audit trail for compliance

## 🚀 Quick Start Commands

```bash
# 1. Create monitoring directory
mkdir -p monitoring/{loki,promtail,grafana/provisioning/datasources}

# 2. Copy configuration files (from above)
# 3. Start the stack
cd monitoring
docker-compose -f docker-compose.logs.yml up -d

# 4. Access Grafana
open http://localhost:3000

# 5. Start your services (they'll automatically send logs)
cd ../services
./build.sh
```

## 📈 Next Steps

1. **Start with basic setup** - Get Loki + Grafana running
2. **Configure log shipping** - Point Promtail to your service logs
3. **Create dashboards** - Build views for different use cases
4. **Set up alerts** - Get notified of important events
5. **Add business metrics** - Track trading and user activity

---

**🎯 This setup gives you professional log management with beautiful web interface - perfect for demonstrating enterprise observability practices in your portfolio!**
