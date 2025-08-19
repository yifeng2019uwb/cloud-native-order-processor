# 🧪 Testing & Validation

> CI/CD pipeline and testing automation

## 🚀 Quick Start
```bash
# Full pipeline (build → deploy → test → destroy)
./test-local.sh --environment dev --all

# Development cycle (keeps infrastructure running)
./test-local.sh --environment dev --dev-cycle

# Component testing
./test-local.sh --frontend
./test-local.sh --gateway
./test-local.sh --services
```

## 🧪 Component Testing

```bash
# Frontend
./frontend/build.sh --test-only

# Gateway
./gateway/build.sh --test-only

# Services
./services/build.sh --test-only user_service
```

## 🔍 Troubleshooting

```bash
# Tests failing due to service unavailability
./manage-services.sh start all
./smoke-test.sh

# Component build failures
./validate-environment.sh
./frontend/build.sh --clean --build-only
```

---

**Note**: For service management, see Service Management guide.
