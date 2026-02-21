# 🔐 Auth Service

> Centralized authentication service for JWT token validation and user context extraction

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Build & Test**: `./dev.sh` (builds and runs unit tests)
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` (local) or `./docker/deploy.sh auth deploy` (dev/AWS), or K8s (see [Docker](../../docker/README.md), [Kubernetes](../../kubernetes/README.md))
- **Integration Tests**: `./integration_tests/run_all_tests.sh`
- **Example**: `curl http://localhost:8003/health`

## ✨ Key Features
- JWT token validation and signature verification
- User context extraction from JWT claims
- Security analytics and audit logging
- Rate limiting and abuse prevention
- Health monitoring and metrics (see [Metrics](../../docs/METRICS.md) for plan and PromQL)

## 📁 Project Structure
```
auth_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── controllers/            # API controllers and endpoints
│   │   └── auth_controller.py  # Authentication endpoints
│   ├── services/               # Business logic services
│   │   └── auth_service.py     # Core authentication logic
│   ├── models/                 # Data models and schemas
│   │   └── auth_models.py      # Authentication request/response models
│   └── utils/                  # Utility functions
│       └── jwt_utils.py        # JWT token utilities
├── tests/                      # Unit and integration tests
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🔗 Quick Links
- [Services Overview](../README.md)
- [API Documentation](http://localhost:8003/docs)
- [Common Package](../common/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - JWT validation and user context extraction working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.