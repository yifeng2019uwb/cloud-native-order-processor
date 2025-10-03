# 🔄 INFRA-005.6: Migration Plan - boto3 → PynamoDB

## 🎯 **Overview**
This document outlines the comprehensive plan to migrate from raw boto3 DynamoDB operations to PynamoDB ORM, eliminating hardcoded strings and improving type safety across all services.

## 📝 **Why Migrate to PynamoDB?**

### **Current Problems with Raw boto3:**
- **Hardcoded strings everywhere** - `'Pk'`, `'Sk'`, `'username'`, `'email'`, etc.
- **No type safety** - Dictionary access without validation
- **Repetitive code** - Manual serialization/deserialization
- **Error-prone** - Typos in field names, missing fields
- **Hard to maintain** - Changes require updates in multiple places

### **Benefits of PynamoDB:**
- **Type safety** - Pydantic model validation
- **No hardcoded strings** - Object properties instead of dictionary keys
- **Auto-serialization** - Automatic conversion between Python objects and DynamoDB
- **Query abstraction** - High-level query methods
- **Transaction support** - Built-in transaction handling
- **FastAPI integration** - Excellent compatibility

---

## 🏗️ **MIGRATION STRATEGY**

### **Core Principle:**
**Incremental migration - one entity at a time, with full testing after each migration.**

### **Safe Migration Strategy:**
1. **Move existing DAOs to archive** - `dao/user_dao.py` → `dao/_archived_boto3/user_dao.py`
2. **Create new PynamoDB DAOs** - `dao/user_dao.py` (same interface, new implementation)
3. **Test side-by-side** - Run integration tests with both DAOs
4. **Compare behavior** - Ensure identical results, no business logic changes
5. **Switch services gradually** - Update imports to use new DAOs
6. **Remove archived DAOs** - Delete `dao/_archived_boto3/` after verification

### **Key Safety Measures:**
- **Archive old code** - Move to `dao/_archived_boto3/` directory
- **Same interface** - New DAOs must have identical method signatures
- **Zero service changes** - Services and integration tests remain completely unchanged
- **One entity at a time** - Don't change everything at once

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Setup & First Model**
- **Install PynamoDB** - `pip install pynamodb`
- **Create archive directory** - `dao/_archived_boto3/`
- **Move existing UserDAO** - `dao/user_dao.py` → `dao/_archived_boto3/user_dao.py`
- **Create UserModel** - Start with User entity (simplest)
- **Create new UserDAO** - `dao/user_dao.py` using PynamoDB (same interface)
- **Test new UserDAO** - Basic CRUD operations
- **Compare with archived DAO** - Ensure identical behavior using existing integration tests

### **Phase 2: Core Models**
- **Move remaining DAOs to archive** - `dao/balance_dao.py` → `dao/_archived_boto3/balance_dao.py`, etc.
- **Create BalanceModel** - Handle decimal precision for money
- **Create new BalanceDAO** - `dao/balance_dao.py` using PynamoDB
- **Create OrderModel** - With proper indexing and GSI
- **Create new OrderDAO** - `dao/order_dao.py` using PynamoDB
- **Create AssetModels** - Asset, AssetBalance, AssetTransaction
- **Create corresponding new DAOs** - For each asset model
- **Test each model** - Run integration tests after each, compare with archived DAOs

### **Phase 3: Service Updates (Zero Changes)**
- **No service code changes** - Services import from `common.data.dao` (unchanged)
- **No integration test changes** - Tests use same DAO interface (unchanged)
- **No import changes** - All import paths remain identical
- **Run existing integration tests** - Should pass without any modifications
- **Time estimate**: **1-2 hours** (just running tests to verify)

### **Phase 4: Cleanup**
- **Remove archived DAOs** - Delete `dao/_archived_boto3/` directory
- **Remove entity_constants.py** - No longer needed
- **Update requirements.txt** - Remove boto3 if not used elsewhere
- **Test everything** - Full integration test suite

---

## 📋 **IMPLEMENTATION APPROACH**

### **Step 1: PynamoDB Model Creation**
- Create PynamoDB models for each entity
- Map all fields from existing entities
- Add proper type hints and validation
- Configure table settings and indexes

### **Step 2: DAO Implementation**
- Implement PynamoDB DAO classes
- Add CRUD operations using PynamoDB methods
- Add query methods for common patterns
- Add error handling and exception mapping

### **Step 3: Controller Updates**
- Replace boto3 calls with PynamoDB DAO calls
- Update error handling for PynamoDB exceptions
- Maintain existing API contracts

---

## 🎯 **BENEFITS OF MIGRATION**

### **1. Eliminate Hardcoded Strings**
- Replace dictionary access with object properties
- Use model constants instead of hardcoded strings
- Centralize field definitions in models

### **2. Type Safety**
- Add Pydantic model validation
- Enable IDE autocomplete and type checking
- Prevent runtime errors from typos

### **3. Maintainability**
- Single source of truth in model definitions
- Easier to add new fields and features
- Consistent patterns across all services

### **4. Error Prevention**
- Compile-time checking for field names
- Automatic validation of data types
- Better error messages and handling

### **5. Developer Experience**
- Object-oriented interface instead of raw dictionaries
- High-level query methods
- Better debugging and development tools

---

## ⚠️ **RISKS AND MITIGATION**

### **Risks:**
1. **Learning Curve** - Need to learn PynamoDB patterns
2. **Breaking Changes** - Potential behavior differences
3. **Performance Issues** - PynamoDB might be slower

### **Mitigation:**
1. **Start Simple** - Begin with User entity (easiest)
2. **Test Each Step** - Run integration tests after each model
3. **Git Revert** - Easy rollback if issues arise
4. **One Entity at a Time** - Don't change everything at once

---

## 📊 **SUCCESS METRICS**

### **Technical Metrics:**
- **Hardcoded strings eliminated**: 100% of database field names
- **Code reduction**: 60-70% less data layer code
- **Type safety**: All database operations use typed models
- **Zero data loss**: No data corruption during migration

### **Developer Experience:**
- **Code maintainability**: Easier to add new fields
- **Error reduction**: Fewer runtime errors from typos
- **Development speed**: Faster feature development
- **Code cleanliness**: Cleaner, more understandable codebase

---

## ❓ **QUESTIONS FOR REVIEW**

1. **Should we start with User entity (simplest) or Order entity (most complex)?**
2. **Do we need to backup existing data before migration?**
3. **Should we keep boto3 as fallback or remove it completely?**
4. **What's the estimated timeline for this migration?**

---

## 📝 **NEXT STEPS**

1. **Review this plan** and provide feedback
2. **Decide on timeline** and resource allocation
3. **Start with Phase 1** - Setup and User entity
4. **Create POC** - Small proof-of-concept
5. **Iterate and refine** based on POC results

---

*This migration plan will eliminate hardcoded strings, improve type safety, and provide a more maintainable codebase while keeping the existing functionality intact.*
