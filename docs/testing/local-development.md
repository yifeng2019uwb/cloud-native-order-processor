# Local Development Testing

## Quick Commands

### Python Services
```bash
cd services
./build.sh --test-only
```

### Gateway
```bash
cd gateway
./build.sh --test-only
```

### Frontend
```bash
cd frontend
./build.sh --test-only
```

### Integration Tests
```bash
cd integration_tests
./run_all_tests.sh all
```

## Health Checks
```bash
curl http://localhost:8000/health  # User Service
curl http://localhost:8001/health  # Inventory Service
curl http://localhost:8002/health  # Order Service
curl http://localhost:8080/health  # API Gateway
```
