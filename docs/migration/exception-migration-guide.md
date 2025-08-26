# 🔄 Exception System Migration Guide

> **Migration**: Restructure exception system to align with common package refactoring and introduce CNOP exception hierarchy

## 📋 Overview

This document outlines the migration plan to refactor the exception system in parallel with the common package restructuring. The goal is to create a clean, maintainable exception architecture that eliminates hardcoded paths, manual registrations, and fragile import strategies.

## 🎯 Goals

- **Eliminate Hardcoded Paths**: Remove fragile relative path imports
- **Configuration-Driven**: Move exception mappings to configuration files
- **CNOP Exception Hierarchy**: Introduce project-specific exception naming
- **Dynamic Discovery**: Auto-discover services and exceptions
- **Clean Architecture**: Separate concerns between mapping logic and configuration
- **Package Alignment**: Exception system works with new common package structure

## 🏗️ New Exception Architecture

### **CNOP Exception Hierarchy**
```python
# common/src/shared/exceptions/base.py
class CNOPException(Exception):
    """Base exception for all CNOP system exceptions"""
    pass

class CNOPInternalException(CNOPException):
    """Base for internal/system issues (500 errors) - NOT exposed to clients"""
    pass

class CNOPClientException(CNOPException):
    """Base for client request issues (400, 404, 409, 422) - exposed to clients"""
    pass
```

### **Exception Package Structure**
```
services/exception/                 # Keep existing structure
├── src/
│   ├── __init__.py
│   ├── exception_mapper.py        # Core mapping logic (existing)
│   ├── error_codes.py             # Error code definitions (existing)
│   ├── error_models.py            # RFC 7807 models (existing)
│   └── exception_mapping.py       # Exception mapping (existing)
└── tests/                         # Test suite (existing)
```

**Note**: We're keeping the existing exception package structure. Only updating import paths and exception names when common package changes.

## 🔄 Migration Phases

### **Phase 1: Foundation - Create CNOP Exception Hierarchy**
**Goal**: Establish new exception base classes and structure

**Tasks**:
1. Create `common/src/shared/exceptions/` package structure
2. Create `base.py` with CNOP exception hierarchy
3. Create `internal.py` for internal exceptions (500 errors)
4. Create `client.py` for client exceptions (400, 404, 409, 422)
5. Update `common/src/shared/exceptions/__init__.py` with exports
6. **Git Commit**: "REFACTOR: Create CNOP exception hierarchy"

**Validation**:
- [ ] CNOP exception classes can be imported
- [ ] Inheritance hierarchy works correctly
- [ ] No conflicts with Python built-in exceptions

---

### **Phase 2: Update Exception Package Imports**
**Goal**: Update services/exception to work with new common package structure

**Tasks**:
1. Update import paths in `exception_mapping.py` to use new common package paths
2. Update exception class names to use new CNOP naming convention
3. Update exception registration calls with new class names
4. Test that exception mapping still works correctly
5. **Git Commit**: "REFACTOR: Update exception package for CNOP exceptions"

**Validation**:
- [ ] Exception package can import from new common package paths
- [ ] Exception mapping works with new CNOP exception names
- [ ] RFC 7807 responses are still correctly formatted
- [ ] No broken imports or references

---

### **Phase 3: Common Package Exception Migration**
**Goal**: Migrate common package to use new CNOP exception hierarchy

**Tasks**:
1. Update `common/src/exceptions/` to inherit from CNOP classes
2. Move data-specific exceptions to `common/src/data/exceptions/`
3. Update import paths throughout common package
4. Ensure all exceptions use CNOP naming convention
5. **Git Commit**: "REFACTOR: Migrate common package to CNOP exceptions"

**Validation**:
- [ ] All common package exceptions use CNOP hierarchy
- [ ] Data exceptions are properly organized
- [ ] Import paths work correctly
- [ ] No broken exception references

---

### **Phase 4: Integration & Testing**
**Goal**: Ensure all services work with new exception system

**Tasks**:
1. Update all service imports to use new exception paths
2. Test exception handling in each service
3. Verify RFC 7807 responses are correct
4. Run integration tests across all services
5. **Git Commit**: "FEAT: Complete exception system migration"

**Validation**:
- [ ] All services can import exceptions correctly
- [ ] Exception handling works as expected
- [ ] RFC 7807 responses are properly formatted
- [ ] Integration tests pass

## 🧪 Testing Strategy

### **Unit Testing**
- **CNOP Exceptions**: Test inheritance and behavior
- **Exception Mapper**: Test mapping logic with configuration
- **Service Discovery**: Test dynamic service detection
- **Configuration Loading**: Test YAML configuration parsing

### **Integration Testing**
- **Service Startup**: Confirm services start without exception errors
- **Exception Handling**: Test exception flow from service to client
- **RFC 7807 Compliance**: Verify error responses follow standard
- **Configuration Changes**: Test runtime configuration updates

### **Manual Validation**
- **Service Startup**: `python -m uvicorn src.main:app --reload`
- **Exception Scenarios**: Trigger various error conditions
- **Response Format**: Verify RFC 7807 compliance
- **Configuration**: Test configuration file modifications

## 📝 What We're Actually Changing

### **Exception Package Updates**
- **Import paths**: Update from `common.exceptions.shared_exceptions` to `common.shared.exceptions`
- **Class names**: Update from `InvalidCredentialsException` to `CNOPInvalidCredentialsException`
- **Registration calls**: Update exception mapper registrations with new class names

### **Common Package Updates**
- **Structure**: Move exceptions to new package organization
- **Naming**: Rename to CNOP convention (e.g., `CNOPInvalidCredentialsException`)
- **Imports**: Update all internal import paths

## 🚨 Risk Mitigation

### **Rollback Strategy**
- Each phase is committed separately
- Can rollback to any phase if issues arise
- Keep old exception system until new one is fully validated
- Test thoroughly before removing old code

### **Breaking Changes**
- **Phase 1**: New exception classes (no breaking changes)
- **Phase 2**: Exception package structure (affects imports)
- **Phase 3**: Common package exceptions (affects all services)
- **Phase 4**: Configuration changes (affects exception mapping)
- **Phase 5**: Service imports (affects all services)

### **Dependency Management**
- Update `setup.py` files to include new package structure
- Ensure all packages are properly exported
- Test imports in isolation before updating services

## 📊 Success Criteria

### **Phase 1 Success**
- [ ] CNOP exception hierarchy created and functional
- [ ] No naming conflicts with Python built-ins
- [ ] Inheritance works correctly

### **Phase 2 Success**
- [ ] Exception package can import from new common package paths
- [ ] Exception mapping works with new CNOP exception names
- [ ] RFC 7807 responses are still correctly formatted

### **Phase 3 Success**
- [ ] Common package uses CNOP exception hierarchy
- [ ] Data exceptions properly organized
- [ ] All import paths work correctly

### **Phase 4 Success**
- [ ] All services work with new exception system
- [ ] Exception handling works correctly
- [ ] RFC 7807 compliance maintained

### **Overall Success**
- [ ] CNOP exception hierarchy established
- [ ] Common package restructured successfully
- [ ] Exception package works with new structure
- [ ] All services integrated successfully

## 🔍 Pre-Migration Checklist

- [ ] Current exception system is stable and all tests pass
- [ ] Git repository is clean (no uncommitted changes)
- [ ] All services are documented and understood
- [ ] Integration test procedures are documented
- [ ] Rollback procedures are understood
- [ ] Team is available for migration support

## 📚 Post-Migration Tasks

- [ ] Update service documentation to reflect new exception paths
- [ ] Update API documentation if needed
- [ ] Update deployment scripts if they reference old paths
- [ ] Update CI/CD pipelines if they reference old paths
- [ ] Create migration guide for future developers
- [ ] Schedule follow-up review of new architecture

## 🎯 Timeline Estimate

- **Phase 1 (CNOP Hierarchy)**: 0.5-1 day
- **Phase 2 (Exception Package)**: 0.5-1 day
- **Phase 3 (Common Package)**: 1-2 days
- **Phase 4 (Integration)**: 1-2 days

**Total Estimated Time**: 3-6 days

## 📞 Support & Escalation

- **Primary Contact**: Development Team Lead
- **Escalation Path**: Technical Architect
- **Emergency Rollback**: Git revert to last working commit
- **Documentation**: All changes documented in this guide

---

**Last Updated**: Aug 25, 2025
**Migration Lead**: Development Team
**Status**: Planning Phase
**Related Tasks**: INFRA-008 (Common Package Restructuring)
