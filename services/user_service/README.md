# 👤 User Service

> User management service for authentication, profile management, and balance operations

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Build & Test**: `./dev.sh` (builds and runs unit tests)
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` (local) or `./docker/deploy.sh user_service deploy` (dev/AWS), or K8s (see [Docker](../../docker/README.md), [Kubernetes](../../kubernetes/README.md))
- **Integration Tests**: `./integration_tests/run_all_tests.sh`
- **Example**: `curl http://localhost:8000/health`

## ✨ Key Features
- User registration and authentication
- Profile management and account operations
- Balance management (deposits, withdrawals)
- Password hashing and security
- Audit logging and compliance

## 📁 Project Structure
```
user_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── controllers/            # API controllers and endpoints
│   │   ├── auth_controller.py  # Authentication endpoints
│   │   ├── user_controller.py  # User management endpoints
│   │   └── balance_controller.py # Balance management endpoints
│   ├── services/               # Business logic services
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── user_service.py     # User management logic
│   │   └── balance_service.py  # Balance operations logic
│   ├── models/                 # Data models and schemas
│   │   ├── user_models.py      # User request/response models
│   │   └── balance_models.py   # Balance request/response models
│   └── validation/             # Input validation
│       └── validators.py       # Field and business validators
├── tests/                      # Unit and integration tests
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🔗 Quick Links
- [Services Overview](../README.md)
- [API Documentation](http://localhost:8000/docs)
- [Common Package](../common/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - User management and balance operations working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.