# 🚀 Service Management

> Start, stop, and monitor local services

## 🚀 Quick Start
```bash
# Start all services
./manage-services.sh start all

# Check status
./manage-services.sh status

# View logs
./manage-services.sh logs [service-name]

# Stop all services
./manage-services.sh stop all
```

## 📁 Services

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | React development server |
| **User Service** | 8000 | Authentication |
| **Inventory Service** | 8001 | Asset management |
| **Order Service** | 8002 | Order processing |
| **Gateway** | 8080 | API Gateway |

## 🛠️ Commands

```bash
# Start/stop specific service
./manage-services.sh start frontend
./manage-services.sh stop user-service

# Restart service
./manage-services.sh restart user-service

# View all logs
./manage-services.sh logs all
```

## 🔍 Troubleshooting

```bash
# Service won't start
./manage-services.sh check-prerequisites
./manage-services.sh check-ports

# Port conflicts
lsof -i :3000
kill -9 [PID]

# Debug mode
export DEBUG=1
./manage-services.sh start all
```

---

**Note**: For production deployment, see Build & Deploy guide.
