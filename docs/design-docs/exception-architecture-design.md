# 🚨 Exception Architecture Design

## 🎯 **Purpose**
Document the correct exception architecture for the CNOP system, clarifying the separation between internal data exceptions, service business logic exceptions, and cross-service shared exceptions.

---

## 🏗️ **Exception Architecture Overview**

### **Layer Separation Principle**
```
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                │
│              Internal Data Exceptions ONLY                  │
│              CNOPUserDataException (DAO/DB issues)          │
│              CNOPDatabaseException (DB connection issues)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVICE LAYER                              │
│              Business Logic Exceptions                      │
│              CNOPUserValidationException                    │
│              CNOPUserNotFoundException                      │
│              CNOPUserAccessDeniedException                  │
│                                                             │
│              ┌─────────────────────────────────────────────┐│
│              │            SHARED LAYER                     ││
│              │      Cross-Service Exceptions               ││
│              │      (Available to Service Layer)           ││
│              │      CNOPUserNotFoundException              ││
│              │      CNOPOrderNotFoundException             ││
│              │      CNOPInsufficientBalanceException       ││
│              └─────────────────────────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    GATEWAY                                  │
│              Maps CNOP Exceptions → HTTP                    │
│              CNOPUserValidationException → HTTP 422         │
│              CNOPUserNotFoundException → HTTP 404           │
│              CNOPInsufficientBalanceException → HTTP 400    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (External)                        │
│              Receives HTTP Standard Errors                  │
│              HTTP 422, 404, 401, 400, etc.                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **Exception Layer Definitions**

### **1. Data Layer (Internal Only - Never to Gateway)**
**Purpose**: Pure internal data problems (DAO failures, database connection issues, internal system errors)
**Inheritance**: `CNOPInternalException` (internal only)
**Visibility**: Never exposed to clients

**Current Exceptions (to be renamed with CNOP prefix)**:
- `DatabaseConnectionException` → `CNOPDatabaseConnectionException` - Database connection failures
- `DatabaseOperationException` → `CNOPDatabaseOperationException` - Database operation failures
- `ConfigurationException` → `CNOPConfigurationException` - Configuration loading failures
- `AWSServiceException` → `CNOPAWSServiceException` - AWS service failures
- `ExternalServiceException` → `CNOPExternalServiceException` - External service failures
- `LockAcquisitionException` → `CNOPLockAcquisitionException` - Lock acquisition failures
- `LockTimeoutException` → `CNOPLockTimeoutException` - Lock timeout failures
- `CommonServerException` → `CNOPCommonServerException` - Generic common server errors
- `EntityValidationException` → `CNOPEntityValidationException` - Generic entity validation failures (internal data validation)

**Key Point**: Data layer exceptions are for system/data infrastructure problems, NOT business logic validation or "not found" scenarios.

**Key Characteristics**:
- ✅ **Internal only**: Never leave the service
- ✅ **No HTTP knowledge**: Just describe the data problem
- ✅ **Service-specific**: Each service has its own data exceptions
- ✅ **Inheritance**: `CNOPInternalException` → `CNOPException`

---

### **2. Shared Layer (Cross-Service - Side Resource)**
**Purpose**: Cross-service exceptions that multiple services can directly raise
**Inheritance**: `CNOPClientException`
**Visibility**: Available to services as a side resource, exposed to clients via Gateway

**Current Exceptions (to be renamed with CNOP prefix)**:

**Cross-Service External Exceptions (CNOPClientException) - ACTIVELY USED in Common Package:**

**Authentication/Authorization (Used in Common Security & DAOs):**
- `InvalidCredentialsException` → `CNOPInvalidCredentialsException` - Authentication failures (used in user_dao.py)
- `TokenExpiredException` → `CNOPTokenExpiredException` - Expired authentication tokens (used in token_manager.py)
- `TokenInvalidException` → `CNOPTokenInvalidException` - Invalid authentication tokens (used in token_manager.py)
- `AuthorizationException` → `CNOPAuthorizationException` - General authorization failures
- `AccessDeniedException` → `CNOPAccessDeniedException` - Access permission denied
- `InsufficientPermissionsException` → `CNOPInsufficientPermissionsException` - Insufficient user permissions

**Data Access (Used in Common DAOs):**
- `EntityNotFoundException` → `CNOPEntityNotFoundException` - Generic entity not found
- `EntityAlreadyExistsException` → `CNOPEntityAlreadyExistsException` - Generic entity already exists
- `UserNotFoundException` → `CNOPUserNotFoundException` - User not found (used in user_dao.py)
- `OrderNotFoundException` → `CNOPOrderNotFoundException` - Order not found (used in order_dao.py)
- `AssetNotFoundException` → `CNOPAssetNotFoundException` - Asset not found (used in asset_dao.py)
- `BalanceNotFoundException` → `CNOPBalanceNotFoundException` - Balance not found (used in balance_dao.py)
- `TransactionNotFoundException` → `CNOPTransactionNotFoundException` - Transaction not found (used in balance_dao.py)

**Note**: Service-specific validation exceptions like `UserValidationException`, `OrderValidationException`, `AssetValidationException` should NOT be used in common package. If common package needs validation, it should use generic `EntityValidationException` and let services handle business logic validation before calling common package.

**Generic Errors:**
- `InternalServerException` → `CNOPInternalServerException` - Generic internal server errors

**Cross-Service Internal Exceptions (CNOPInternalException) - Used in Common Package:**
- `ExternalServiceException` → `CNOPExternalServiceException` - External service failures (internal only)

**Note**: These exceptions are actively used within the common package and should remain in shared exceptions for cross-service use.

**Key Characteristics**:
- ✅ **Cross-service**: Multiple services use these
- ✅ **Side resource**: Available to service layer, not in main flow
- ✅ **Generic names**: Not tied to specific service
- ✅ **Inheritance**: `CNOPClientException` → `CNOPException`
- ✅ **Direct access**: Services can import and raise these directly

---

### **3. Service Layer (External to Gateway)**
**Purpose**: Business logic exceptions that services expose to clients
**Inheritance**: `CNOPClientException`
**Visibility**: Exposed to clients via Gateway

**Current Exceptions (to be renamed with CNOP prefix)**:
- `InsufficientBalanceException` → `CNOPInsufficientBalanceException` - Business logic: insufficient balance for operations

**Service-Specific Exceptions (NOT used in Common Package - Move to Services Only)**:

**User Service**:
- `UserAlreadyExistsException` → `CNOPUserAlreadyExistsException` - User already exists (NOT used in common)
- `UserServerException` → `CNOPUserServerException` - User service internal errors
- `UserValidationException` → `CNOPUserValidationException` - User business logic validation failures (422 error)

**Order Service**:
- `OrderAlreadyExistsException` → `CNOPOrderAlreadyExistsException` - Order already exists (NOT used in common)
- `OrderServerException` → `CNOPOrderServerException` - Order service internal errors
- `OrderValidationException` → `CNOPOrderValidationException` - Order business logic validation failures including invalid status (422 error)

**Migration Note**: `OrderStatusException` has been consolidated into `OrderValidationException`. During migration, replace all `OrderStatusException` usage with `OrderValidationException` since invalid status is a validation failure.

**Inventory Service**:
- `AssetAlreadyExistsException` → `CNOPAssetAlreadyExistsException` - Asset already exists (NOT used in common)
- `InventoryServerException` → `CNOPInventoryServerException` - Inventory service internal errors
- `AssetValidationException` → `CNOPAssetValidationException` - Asset business logic validation failures (422 error)

**Auth Service**:
- **Note**: `TokenExpiredException` and `TokenInvalidException` are USED in common package (token_manager.py), so they should stay in shared exceptions, not move to auth service.

**Migration Strategy**:
1. **Keep in Common Package**: All exceptions actively used by common package components
2. **Move to Services**: Only exceptions that are NOT used by common package (like `*AlreadyExistsException`)
3. **Avoid Duplication**: Services should import from common package, not redefine

**Validation Architecture Correction**:
- **Data Layer**: Generic `EntityValidationException` for internal data validation failures (500 error)
- **Service Layer**: Business logic validation (`UserValidationException`, `OrderValidationException`, `AssetValidationException`) (422 error)
- **Data Layer**: Should never throw service-specific validation exceptions
- **If Data Layer Throws Validation Exception**: It's an internal service error (500), indicating business logic validation was missed in service layer

**Key Characteristics**:
- ✅ **External interface**: Exposed to clients
- ✅ **Business logic**: Service-specific business rule violations
- ✅ **Service attribution**: Exception name shows which service
- ✅ **Inheritance**: `CNOPClientException` → `CNOPException`
- ✅ **Can use shared exceptions**: Services can raise shared exceptions directly

---

### **4. Gateway Layer (HTTP Mapping)**
**Purpose**: Convert CNOP exceptions to HTTP standard responses
**Function**: Exception mapping and HTTP status code assignment
**Examples**:
- `CNOPUserValidationException` → HTTP 422 Validation Error
- `CNOPUserNotFoundException` → HTTP 404 Not Found
- `CNOPAuthInvalidCredentialsException` → HTTP 401 Unauthorized

**Key Characteristics**:
- ✅ **HTTP mapping**: CNOP exceptions → HTTP status codes
- ✅ **Standard responses**: RFC 7807 Problem Details
- ✅ **Client experience**: Standard HTTP errors, not CNOP-specific names

---

## 🔄 **Exception Flow Examples**

### **How the Flow Actually Works:**

**Data Layer** → **Service Layer** → **Gateway** → **Client**

**Shared Layer** is a side resource available to the Service Layer, not part of the main flow.

1. **Data Layer**: Throws internal exceptions for system/data infrastructure problems
2. **Service Layer**:
   - Can raise shared exceptions directly (from shared layer)
   - Can catch data exceptions and convert to appropriate exceptions
   - Can raise service-specific business logic exceptions
3. **Gateway**: Maps business logic exceptions to appropriate HTTP status codes
4. **Client**: Receives standard HTTP error responses

**Important**:
- Data layer exceptions are NEVER exposed to clients. They are always caught by the service layer and converted to appropriate business logic exceptions.
- Service layer can use both service-specific exceptions and shared exceptions.
- Shared exceptions provide consistency across multiple services.

### **Example 1: User Validation Failure (Business Logic)**
```
1. Service Layer: CNOPUserValidationException (external, 422)
   "User validation failed in User service" - Business logic validation

2. Gateway: HTTP 422 Validation Error
   Standard RFC 7807 response

3. Client: Receives HTTP 422 with validation error details

**Note**: Data layer should NEVER throw validation exceptions if business logic is properly implemented.
If data layer throws validation exception, it indicates a bug in service layer business logic.
```

### **Example 2: User Not Found (Business Logic)**
```
1. Service Layer: CNOPUserNotFoundException (external, 404)
   "User not found in User service" - Business logic check

2. Gateway: HTTP 404 Not Found
   Standard RFC 7807 response

3. Client: Receives HTTP 404 with "User not found" message

**Note**: Data layer should NEVER throw "not found" exceptions if business logic is properly implemented.
If data layer throws "not found" exception, it indicates a bug in service layer business logic.
```

### **Example 3: Internal Data Issue (System Error)**
```
1. Data Layer: CNOPDatabaseConnectionException (internal, 500)
   "Database connection timeout" - Infrastructure/system issue

2. Service Layer: CNOPInternalServerException (external, 500)
   "Internal server error in User service" - Caught and converted to generic internal error

3. Gateway: HTTP 500 Internal Server Error
   Standard RFC 7807 response

4. Client: Receives HTTP 500 with generic error message

**Note**: This is the ONLY scenario where data layer exceptions should reach the service layer.
Data layer exceptions are for infrastructure/system failures, not business logic issues.
```

### **Example 4: Cross-Service Business Rule (Using Shared Layer)**
```
1. Service Layer: CNOPInsufficientBalanceException (external, 400)
   "Insufficient balance for order" (directly raising shared exception)

2. Gateway: HTTP 400 Bad Request
   Standard RFC 7807 response

3. Client: Receives HTTP 400 with "Insufficient balance" message

**Note**: No data layer exception involved. Service directly raises business logic exception.
```

### **Example 5: Cross-Service Resource Not Found (Using Shared Layer)**
```
1. Service Layer: CNOPUserNotFoundException (external, 404)
   "User not found" (directly raising shared exception)

2. Gateway: HTTP 404 Not Found
   Standard RFC 7807 response

3. Client: Receives HTTP 404 with "User not found" message

**Note**: No data layer exception involved. Service directly raises business logic exception.
```

### **Example 6: Service Directly Raising Shared Exception**
```
1. Service Layer: CNOPUserNotFoundException (external, 404)
   "User not found" (directly raising shared exception, no data layer involved)

2. Gateway: HTTP 404 Not Found
   Standard RFC 7807 response

3. Client: Receives HTTP 404 with "User not found" message
```

---

## 📝 **Exception Naming Convention**

### **Data Layer Exceptions**
```
CNOP + Service + Data + Exception
Examples:
- CNOPUserDataException
- CNOPOrderDataException
- CNOPDatabaseException
- CNOPDataValidationException
```

### **Service Layer Exceptions**
```
CNOP + Service + BusinessLogic + Exception
Examples:
- CNOPUserValidationException
- CNOPOrderValidationException
- CNOPAuthInvalidCredentialsException
- CNOPInventoryAssetNotFoundException
```

### **Shared Layer Exceptions**
```
CNOP + Generic + Exception
Examples:
- CNOPUserNotFoundException
- CNOPOrderNotFoundException
- CNOPInsufficientBalanceException
- CNOPResourceNotFoundException
```

---

## 🏗️ **Implementation Structure**

### **Package Organization**
```
services/common/src/
├── exceptions/                    # Base exception classes
│   ├── base_exception.py         # CNOPException, CNOPInternalException, CNOPClientException
│   ├── shared_exceptions.py      # Cross-service exceptions (CNOPClientException)
│   └── exceptions.py             # Internal common exceptions (CNOPInternalException)
├── data/                         # Data package
│   └── exceptions/               # Data-specific exceptions (CNOPInternalException)
│       ├── database.py           # Database exceptions
│       ├── dao.py                # DAO exceptions
│       └── validation.py         # Internal data validation
└── shared/                       # Shared package
    └── exceptions/               # Cross-service exceptions (CNOPClientException)
        ├── auth.py               # Authentication exceptions
        ├── user.py               # User service exceptions
        ├── order.py              # Order service exceptions
        └── inventory.py          # Inventory service exceptions
```

### **Service-Specific Exception Packages**
```
services/user_service/src/
└── exceptions/
    ├── __init__.py
    ├── user_exceptions.py        # CNOPUserValidationException, etc.
    └── business_exceptions.py    # Business logic exceptions

services/order_service/src/
└── exceptions/
    ├── __init__.py
    ├── order_exceptions.py       # CNOPOrderValidationException, etc.
    └── business_exceptions.py    # Business logic exceptions
```

---

## 🔧 **Migration Strategy**

### **Phase 1: Foundation**
- ✅ Create CNOP exception hierarchy (DONE)
- ✅ Define clear layer boundaries
- ✅ Document exception flow

### **Phase 2: Data Layer**
- 🔄 Create data exception package
- 🔄 Move internal exceptions to data package
- 🔄 Ensure no HTTP knowledge in data exceptions

### **Phase 3: Service Layer**
- 📋 Create service-specific exception packages
- 📋 Move business logic exceptions to service packages
- 📋 Update service imports

### **Phase 4: Shared Layer**
- 📋 Clean up shared exceptions
- 📋 Remove HTTP status comments
- 📋 Ensure only cross-service exceptions remain

### **Phase 5: Gateway Integration**
- 📋 Update exception mapping
- 📋 Test HTTP status code mapping
- 📋 Validate RFC 7807 compliance

---

## 🚨 **Key Rules**

### **Data Layer Rules**
- ❌ **Never** include HTTP status codes in comments
- ❌ **Never** inherit from `CNOPClientException`
- ❌ **Never** handle business logic validation
- ❌ **Never** handle "not found" scenarios
- ✅ **Always** inherit from `CNOPInternalException`
- ✅ **Always** focus on system/data infrastructure problems
- ✅ **Always** use service-specific naming
- ✅ **Always** be caught and converted by service layer

### **Service Layer Rules**
- ❌ **Never** include HTTP status codes in comments
- ✅ **Always** inherit from `CNOPClientException`
- ✅ **Always** include service name in exception class
- ✅ **Always** focus on business logic description
- ✅ **Always** be service-specific

### **Shared Layer Rules**
- ❌ **Never** include HTTP status codes in comments
- ✅ **Always** inherit from `CNOPClientException`
- ✅ **Always** use generic names (no service prefix)
- ✅ **Always** be truly cross-service
- ✅ **Always** focus on business logic description

### **Gateway Rules**
- ✅ **Always** map CNOP exceptions to HTTP status codes
- ✅ **Always** provide RFC 7807 compliant responses
- ✅ **Always** include service context in error details
- ✅ **Never** expose internal exception details

---

## 📊 **Exception Classification Matrix**

| Exception Type | Layer | Inheritance | HTTP Status | Example |
|----------------|-------|-------------|-------------|---------|
| Data Issues | Data | `CNOPInternalException` | 500 (Internal) | `CNOPUserDataException` |
| Business Logic | Service | `CNOPClientException` | 400, 422 | `CNOPUserValidationException` |
| Cross-Service | Shared | `CNOPClientException` | 400, 404, 409 | `CNOPUserNotFoundException` |
| Authentication | Service | `CNOPClientException` | 401 | `CNOPAuthInvalidCredentialsException` |
| Authorization | Service | `CNOPClientException` | 403 | `CNOPUserAccessDeniedException` |

---

## 🔍 **Validation Checklist**

### **Data Layer Validation**
- [ ] No HTTP status codes in comments
- [ ] All exceptions inherit from `CNOPInternalException`
- [ ] All exceptions are service-specific
- [ ] All exceptions focus on data problems only
- [ ] No business logic knowledge

### **Service Layer Validation**
- [ ] No HTTP status codes in comments
- [ ] All exceptions inherit from `CNOPClientException`
- [ ] All exceptions include service name
- [ ] All exceptions focus on business logic
- [ ] No data layer knowledge

### **Shared Layer Validation**
- [ ] No HTTP status codes in comments
- [ ] All exceptions inherit from `CNOPClientException`
- [ ] All exceptions use generic names
- [ ] All exceptions are truly cross-service
- [ ] No service-specific knowledge

---

## 📚 **Related Documentation**

- **[Exception Package Design](./exception-package-design.md)**: Implementation details
- **[Common Package Design](./common-package-design.md)**: Shared components
- **[Migration Guide](../migration/exception-migration-guide.md)**: Step-by-step migration
- **[RFC 7807](https://tools.ietf.org/html/rfc7807)**: Problem Details for HTTP APIs

---

## 🎉 **Implementation Status**

**✅ Exception Migration Completed:**
- **CNOP Prefix**: All exceptions now use `CNOP` prefix for clear ownership
- **Package Structure**: Exceptions properly organized in new package structure
- **Import Paths**: All import paths updated to reflect new structure
- **Test Coverage**: 95.48% test coverage with all tests passing
- **No Conflicts**: No naming conflicts with standard Python exceptions

**🏗️ New Exception Structure Achieved:**
```
services/common/src/
├── exceptions/              # Base exceptions & shared exceptions
│   ├── base_exception.py   # CNOPException, CNOPInternalException, CNOPClientException
│   ├── shared_exceptions.py # Cross-service exceptions (CNOPUserNotFoundException, etc.)
│   └── exceptions.py       # Common exceptions
├── data/exceptions/         # Data layer exceptions (internal only)
├── auth/exceptions/         # Auth-specific exceptions
└── core/exceptions/         # Core business logic exceptions
```

**🎯 This exception architecture provides clear separation of concerns, proper inheritance hierarchy, and clean exception flow from data layer through services to clients.**
