# 🔄 Common Package Restructuring Migration Guide

> **Migration**: Restructuring the common package for better separation of concerns and maintainability

## 📋 Overview

This document outlines the migration plan to restructure the `services/common` package from its current monolithic structure to a clean, modular architecture with clear separation of concerns.

## 🎯 Goals

- **Eliminate Code Duplication**: Centralize authentication logic across all services
- **Improve Maintainability**: Clear package boundaries and single responsibilities
- **Reduce Coupling**: Services import only what they need
- **Enhance Testing**: Each package can be tested independently
- **Future-Proof Architecture**: Scalable structure for new features

## 🏗️ New Package Structure

```
services/
├── common/
│   ├── src/
│   │   ├── auth/                    # Pure authentication domain
│   │   │   ├── __init__.py
│   │   │   ├── security/           # JWT, passwords, tokens
│   │   │   ├── gateway/            # Gateway header validation
│   │   │   └── exceptions/         # Auth-specific exceptions
│   │   ├── data/                   # Pure data access domain
│   │   │   ├── __init__.py
│   │   │   ├── database/           # DB connections
│   │   │   ├── dao/               # Data access objects
│   │   │   ├── entities/          # Data models
│   │   │   └── exceptions/        # Data-specific exceptions
│   │   ├── core/                  # Pure utilities domain
│   │   │   ├── __init__.py
│   │   │   ├── utils/             # Business utilities
│   │   │   ├── validation/        # Business validation
│   │   │   └── exceptions/        # Business logic exceptions
│   │   └── shared/                # Cross-cutting infrastructure
│   │       ├── __init__.py
│   │       ├── logging/           # Structured logging
│   │       ├── health/            # Health checks
│   │       └── monitoring/        # Metrics, observability
│   ├── tests/
│   ├── requirements.txt
│   └── setup.py
```

## 🔄 Migration Phases

### **Phase 1: Foundation - Data Package Migration**
**Goal**: Move all data-related functionality to `common.data.*`

**Tasks**:
1. Create new `common/src/data/` package structure
2. Move existing data code:
   - `common/src/database/` → `common/src/data/database/`
   - `common/src/dao/` → `common/src/data/dao/`
   - `common/src/entities/` → `common/src/data/entities/`
3. Update `common/src/data/__init__.py` with proper exports
4. Update common package unit tests to use new paths
5. Update all service imports to use new data paths
6. Run manual integration tests to confirm stability
7. **Git Commit**: "REFACTOR: Move data package to new structure"

**Validation**:
- [ ] All common unit tests pass
- [ ] All services can import data modules
- [ ] Manual integration tests pass
- [ ] No import errors in any service

---

### **Phase 2: Authentication - Auth Package Migration**
**Goal**: Move all authentication functionality to `common.auth.*`

**Tasks**:
1. Create new `common/src/auth/` package structure
2. Move existing auth code:
   - `common/src/security/` → `common/src/auth/security/`
   - Create `common/src/auth/gateway/` for gateway validation functions
   - Create `common/src/auth/exceptions/` for auth-specific exceptions
3. Update `common/src/auth/__init__.py` with proper exports
4. Update all service imports to use new auth paths
5. Run manual integration tests to confirm stability
6. **Git Commit**: "REFACTOR: Move auth package to new structure"

**Validation**:
- [ ] All services can import auth modules
- [ ] Authentication still works in all services
- [ ] Manual integration tests pass
- [ ] No import errors in any service

---

### **Phase 3: Business Logic - Core Package Migration**
**Goal**: Move all business logic utilities to `common.core.*`

**Tasks**:
1. Create new `common/src/core/` package structure
2. Move existing business logic code:
   - `common/src/utils/` → `common/src/core/utils/`
   - `common/src/validation/` → `common/src/core/validation/`
   - Business logic exceptions → `common/src/core/exceptions/`
3. Update `common/src/core/__init__.py` with proper exports
4. Update all service imports to use new core paths
5. Run manual integration tests to confirm stability
6. **Git Commit**: "REFACTOR: Move core package to new structure"

**Validation**:
- [ ] All services can import core modules
- [ ] Business logic still works in all services
- [ ] Manual integration tests pass
- [ ] No import errors in any service

---

### **Phase 4: Infrastructure - Shared Package Migration**
**Goal**: Move all cross-cutting infrastructure to `common.shared.*`

**Tasks**:
1. Create new `common/src/shared/` package structure
2. Move existing infrastructure code:
   - `common/src/logging/` → `common/src/shared/logging/`
   - `common/src/health/` → `common/src/shared/health/`
   - Monitoring/metrics → `common/src/shared/monitoring/`
3. Update `common/src/shared/__init__.py` with proper exports
4. Update all service imports to use new shared paths
5. Run manual integration tests to confirm stability
6. **Git Commit**: "REFACTOR: Move shared package to new structure"

**Validation**:
- [ ] All services can import shared modules
- [ ] Logging, health, and monitoring still work
- [ ] Manual integration tests pass
- [ ] No import errors in any service

---

### **Phase 5: Cleanup & Finalization**
**Goal**: Complete the migration and update documentation

**Tasks**:
1. Remove old package structure (after confirming new structure works)
2. Update common package `setup.py` and `requirements.txt`
3. Update all documentation to reflect new structure
4. Final integration test across all services
5. **Git Commit**: "REFACTOR: Complete package restructuring"

**Validation**:
- [ ] Old structure completely removed
- [ ] All documentation updated
- [ ] Final integration tests pass
- [ ] No broken imports anywhere

## 🧪 Testing Strategy

### **Unit Testing**
- **Common Package**: Test each new package independently
- **Service Tests**: Ensure services can import from new structure
- **Import Tests**: Verify all import paths work correctly

### **Integration Testing**
- **Service Startup**: Confirm each service starts without errors
- **API Endpoints**: Test key endpoints in each service
- **Authentication**: Verify auth flows still work
- **Database Operations**: Confirm data access still functions

### **Manual Validation**
- **Service Startup**: `python -m uvicorn src.main:app --reload`
- **Health Checks**: Verify `/health` endpoints respond
- **Logging**: Check that logging appears correctly
- **Error Handling**: Test error scenarios

## 📝 Import Path Changes

### **Before (Current Structure)**
```python
from common.database import get_user_dao
from common.dao.user import UserDAO
from common.entities.user import User
from common.security import verify_jwt
from common.utils import validate_email
from common.logging import setup_logging
```

### **After (New Structure)**
```python
from common.data.database import get_user_dao
from common.data.dao.user import UserDAO
from common.data.entities.user import User
from common.auth.security import verify_jwt
from common.core.utils import validate_email
from common.shared.logging import setup_logging
```

## 🚨 Risk Mitigation

### **Rollback Strategy**
- Each phase is committed separately
- Can rollback to any phase if issues arise
- Keep old structure until new one is fully validated
- Test thoroughly before removing old code

### **Breaking Changes**
- **Phase 1**: Data package changes affect all services
- **Phase 2**: Auth package changes affect all services
- **Phase 3**: Core package changes affect all services
- **Phase 4**: Shared package changes affect all services

### **Dependency Management**
- Update `setup.py` to include new package structure
- Ensure all packages are properly exported
- Test imports in isolation before updating services

## 📊 Success Criteria

### **Phase 1 Success**
- [ ] Data package structure created and functional
- [ ] All services can import data modules from new paths
- [ ] No data-related functionality broken
- [ ] Integration tests pass

### **Phase 2 Success**
- [ ] Auth package structure created and functional
- [ ] All services can import auth modules from new paths
- [ ] Authentication still works in all services
- [ ] Integration tests pass

### **Phase 3 Success**
- [ ] Core package structure created and functional
- [ ] All services can import core modules from new paths
- [ ] Business logic still works in all services
- [ ] Integration tests pass

### **Phase 4 Success**
- [ ] Shared package structure created and functional
- [ ] All services can import shared modules from new paths
- [ ] Infrastructure still works in all services
- [ ] Integration tests pass

### **Overall Success**
- [ ] All services use new package structure
- [ ] No broken imports or functionality
- [ ] Clean, maintainable architecture
- [ ] Comprehensive documentation updated

## 🔍 Pre-Migration Checklist

- [ ] Current codebase is stable and all tests pass
- [ ] Git repository is clean (no uncommitted changes)
- [ ] All services are documented and understood
- [ ] Integration test procedures are documented
- [ ] Rollback procedures are understood
- [ ] Team is available for migration support

## 📚 Post-Migration Tasks

- [ ] Update service documentation to reflect new import paths
- [ ] Update API documentation if needed
- [ ] Update deployment scripts if they reference old paths
- [ ] Update CI/CD pipelines if they reference old paths
- [ ] Create migration guide for future developers
- [ ] Schedule follow-up review of new architecture

## 🎯 Timeline Estimate

- **Phase 1 (Data)**: 1-2 days
- **Phase 2 (Auth)**: 1-2 days
- **Phase 3 (Core)**: 1-2 days
- **Phase 4 (Shared)**: 1-2 days
- **Phase 5 (Cleanup)**: 0.5-1 day

**Total Estimated Time**: 4.5-9 days

## 📞 Support & Escalation

- **Primary Contact**: Development Team Lead
- **Escalation Path**: Technical Architect
- **Emergency Rollback**: Git revert to last working commit
- **Documentation**: All changes documented in this guide

---

**Last Updated**: Aug 25, 2025
**Migration Lead**: Development Team
**Status**: Planning Phase
