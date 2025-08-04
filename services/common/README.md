# Common Package

Shared components and utilities for the Cloud Native Order Processor microservices.

## 📁 Package Structure

```
services/common/src/
├── entities/           # Data models and entities
│   ├── user/          # User-related entities
│   ├── order/         # Order-related entities
│   └── inventory/     # Inventory-related entities
├── dao/               # Data Access Objects
│   ├── user/          # User and balance DAOs
│   ├── order/         # Order DAO
│   └── inventory/     # Asset DAO
├── database/          # Database connections and dependencies
├── exceptions/        # Shared exception classes
├── health/           # Health check utilities
├── aws/              # AWS utilities (STS, etc.)
├── security/         # Security management (NEW)
│   ├── password_manager.py    # Password hashing and validation
│   ├── token_manager.py       # JWT token management
│   └── audit_logger.py        # Security event logging
└── utils/            # Common utilities (pagination, etc.)
```

## 🏗️ Architecture Overview

### **Service-Based Entity Organization**
Entities are organized by service domain to avoid naming conflicts and improve maintainability:

- **User Service**: `User`, `Balance`, `BalanceTransaction`
- **Order Service**: `Order`, `OrderCreate`, `OrderResponse`
- **Inventory Service**: `Asset`, `AssetListResponse`

### **Database Design**
- **Single Table Approach**: All entities stored in service-specific tables
- **Composite Keys**: Efficient querying with PK/SK patterns
- **GSI Support**: Global Secondary Indexes for complex queries

## 📊 Entities

### **User Entities**
- `User` - Core user model with authentication data
- `Balance` - User account balance (current_balance, totals)
- `BalanceTransaction` - Transaction history (deposits, withdrawals, order payments)
- `TransactionType` - DEPOSIT, WITHDRAW, ORDER_PAYMENT, ORDER_REFUND, SYSTEM_ADJUSTMENT
- `TransactionStatus` - PENDING, COMPLETED, FAILED, CANCELLED

### **Order Entities**
- `Order` - Core order model with full lifecycle support
- `OrderCreate` - Request model for order creation
- `OrderResponse` - Response model for order data
- `OrderUpdate` - Update model for order modifications
- `OrderType` - MARKET_BUY, MARKET_SELL, LIMIT_BUY, LIMIT_SELL
- `OrderStatus` - PENDING, CONFIRMED, QUEUED, PROCESSING, COMPLETED, CANCELLED, FAILED, EXPIRED

### **Inventory Entities**
- `Asset` - Asset information and metadata
- `AssetListResponse` - Paginated asset listings

## 🗄️ Data Access Objects (DAOs)

### **User DAO**
- `UserDAO` - User CRUD operations with integrated security
- `BalanceDAO` - Balance and transaction management

**Key Methods:**
- `create_user()`, `get_user_by_username()`, `update_user()`, `authenticate_user()`
- `create_balance()`, `get_balance()`, `update_balance()`
- `create_transaction()`, `get_user_transactions()`, `update_transaction_status()`

**Security Integration:**
- Password hashing via `PasswordManager`
- Password verification via `PasswordManager`
- Centralized security operations

### **Order DAO**
- `OrderDAO` - Order lifecycle management

**Key Methods:**
- `create_order()`, `get_order()`, `update_order()`
- `update_order_status()`, `get_orders_by_user()`
- `get_orders_by_user_and_asset()`, `get_orders_by_user_and_status()`

### **Inventory DAO**
- `AssetDAO` - Asset management

**Key Methods:**
- `create_asset()`, `get_asset()`, `update_asset()`
- `get_assets()`, `activate_asset()`, `deactivate_asset()`

## 🔐 Security Management

### **Security Components**
The common package now includes centralized security management:

#### **PasswordManager**
- **Purpose**: Centralized password hashing and verification
- **Features**: bcrypt-based hashing, password strength validation
- **Integration**: Used by `UserDAO` for all password operations
- **Methods**: `hash_password()`, `verify_password()`, `validate_password_strength()`

#### **TokenManager**
- **Purpose**: JWT token creation, verification, and management
- **Features**: Access token generation, payload decoding, expiration checking
- **Methods**: `create_access_token()`, `verify_access_token()`, `decode_token_payload()`, `is_token_expired()`

#### **AuditLogger**
- **Purpose**: Security event logging and audit trails
- **Features**: Structured logging for login, logout, password changes, access denied events
- **Methods**: `log_login_success()`, `log_login_failure()`, `log_password_change()`, `log_access_denied()`

### **Security Integration**
- **UserDAO**: Integrated with `PasswordManager` for password operations
- **Services**: Can use `TokenManager` for JWT operations
- **Audit**: All services can use `AuditLogger` for security event tracking
- **Centralized**: All security operations use common components

## 🔗 Database Dependencies

### **Dependency Injection**
```python
from common.database import get_user_dao, get_balance_dao, get_order_dao, get_asset_dao

# FastAPI dependency injection
user_dao = Depends(get_user_dao)
balance_dao = Depends(get_balance_dao)
order_dao = Depends(get_order_dao)
asset_dao = Depends(get_asset_dao)
```

### **Connection Management**
- **DynamoDB Manager**: Centralized connection management
- **STS Integration**: AWS role assumption for cross-account access
- **Health Checks**: Database connectivity monitoring

## 🎯 Order-Balance Integration Design

### **Current Implementation**
- **Balance Validation**: Check sufficient funds before order creation
- **Transaction Creation**: Automatic balance transactions for orders
- **Status Synchronization**: Order and transaction status coordination

### **Market Order Flow**
```
Market Buy:
1. Validate user balance
2. Create order record
3. Create ORDER_PAYMENT transaction
4. Update user balance
5. Return success/fail

Market Sell:
1. Create order record
2. When executed: Create ORDER_PAYMENT transaction
3. Update user balance
4. Return success/fail
```

### **Limit Order Flow (Future)**
```
Limit Buy:
1. Validate user balance
2. Create order record
3. Create ORDER_HOLD transaction
4. Update user balance (hold money)
5. Queue order for execution

Limit Sell:
1. Create order record
2. Queue order for execution
3. When executed: Create ORDER_PAYMENT transaction
4. Update user balance
```

## 🚀 Future Enhancements

### **High Priority**
- [ ] **Limit Order Implementation**
  - Order hold/release mechanisms
  - Price trigger logic
  - Expiration handling
- [ ] **Transaction Atomicity**
  - Database transactions for order-balance operations
  - Rollback mechanisms for partial failures
- [ ] **Balance DAO Tests**
  - Improve test coverage (currently 18%)
  - Integration tests for order-balance flow

### **Medium Priority**
- [ ] **Validation Framework**
  - Common validation utilities
  - Field validation patterns
  - Business rule validation
- [ ] **Middleware Components**
  - Request/response logging
  - Error handling middleware
  - Authentication middleware
- [ ] **Caching Layer**
  - Redis integration for balance caching
  - Order status caching
  - Asset price caching

### **Low Priority**
- [ ] **Advanced Order Types**
  - Stop-loss orders
  - Take-profit orders
  - Trailing stop orders
- [ ] **Analytics Support**
  - Order analytics entities
  - Trading volume tracking
  - Performance metrics
- [ ] **Multi-Currency Support**
  - Currency conversion
  - Multi-currency balances
  - Exchange rate management

## 🔧 Development Guidelines

### **Async/Sync Design Pattern**
The system uses a hybrid async/sync pattern for transaction atomicity:

#### **Transaction Manager (Async)**
- **Purpose**: Orchestrates complex multi-step transactions
- **Pattern**: `async def` methods that use `UserLock` async context manager
- **DAO Calls**: Synchronous (no `await` needed)
- **Example**:
  ```python
  async def deposit_funds(self, user_id: str, amount: Decimal):
      async with UserLock(user_id, "deposit", timeout):
          # Sync DAO calls (no await)
          transaction = self.balance_dao.create_transaction(...)
          balance = self.balance_dao.get_balance(user_id)
  ```

#### **Lock Manager (Hybrid)**
- **UserLock Context Manager**: `async def` (required for `async with`)
- **Lock Functions**: `def` (sync - DynamoDB operations are sync)
- **Pattern**: Async context manager calls sync functions
- **Example**:
  ```python
  class UserLock:
      async def __aenter__(self):
          self.lock_id = acquire_lock(...)  # sync call

      async def __aexit__(self):
          release_lock(...)  # sync call
  ```

#### **DAOs (Sync)**
- **All DAO methods**: `def` (synchronous)
- **No async/await**: All database operations are sync
- **Called by**: Transaction manager (without `await`)

#### **Design Rationale**
- **Personal project**: Low traffic, simple concurrency control
- **User-level locking**: Sufficient for preventing race conditions
- **Atomic operations**: Ensures data consistency
- **Simple pattern**: Async context manager + sync database operations

### **Adding New Entities**
1. Create entity in appropriate service directory
2. Add to service's `__init__.py` exports
3. Update main entities `__init__.py`
4. Create corresponding DAO
5. Add dependency injection function
6. Write comprehensive tests

### **Database Schema Changes**
1. Update entity models
2. Modify DAO operations
3. Update test data
4. Document migration steps
5. Update this README

### **Integration Patterns**
1. **Validation First**: Always validate before creating records
2. **Atomic Operations**: Use transactions for multi-step operations
3. **Error Handling**: Fail fast with clear error messages
4. **Status Tracking**: Keep related entities in sync

## 📝 API Integration Notes

### **Order Service Integration**
- Uses `OrderDAO` for order management
- Calls `BalanceDAO` for balance validation
- Creates balance transactions for order payments
- Handles order completion and cancellation

### **User Service Integration**
- Uses `UserDAO` for user management
- Uses `BalanceDAO` for balance operations
- Provides balance and transaction APIs
- Handles deposits and withdrawals

### **Inventory Service Integration**
- Uses `AssetDAO` for asset management
- Provides asset listing and details
- Supports asset activation/deactivation

## 🧪 Testing

### **Current Coverage**
- **Total Coverage**: 96.81%
- **Entities**: 100% coverage
- **DAOs**: 95%+ coverage (UserDAO: 99%, Balance DAO: 85%)
- **Database**: 92% coverage
- **Security**: 100% coverage (PasswordManager, TokenManager, AuditLogger)
- **Utilities**: 100% coverage

### **Test Structure**
```
tests/
├── entities/          # Entity model tests
├── dao/              # DAO operation tests
├── database/         # Database connection tests
├── security/         # Security component tests (NEW)
└── conftest.py       # Test configuration and fixtures
```

## 📚 Dependencies

### **Core Dependencies**
- `pydantic==2.5.0` - Data validation and serialization
- `boto3==1.29.7` - AWS SDK
- `fastapi==0.104.1` - Web framework
- `python-dotenv==1.0.0` - Environment management
- `bcrypt==4.0.1` - Password hashing
- `python-jose[cryptography]==3.3.0` - JWT token management

### **Development Dependencies**
- `pytest==7.4.3` - Testing framework
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-asyncio==0.21.1` - Async testing support

## 🔄 Version History

### **v1.1.0** (Current)
- ✅ Service-based entity organization
- ✅ Complete DAO implementations
- ✅ Order-balance integration design
- ✅ Balance transaction system
- ✅ Database dependency injection
- ✅ **Security Manager Integration** (NEW)
- ✅ **Centralized Password Management** (NEW)
- ✅ **JWT Token Management** (NEW)
- ✅ **Security Audit Logging** (NEW)
- ✅ **UserDAO Security Integration** (NEW)
- ✅ Comprehensive test coverage (96.81%)

### **Planned v1.2.0**
- 🔄 Limit order implementation
- 🔄 Transaction atomicity
- 🔄 Enhanced validation framework
- 🔄 Service integration with security components
- 🔄 Gateway JWT integration

---

**Note**: This package serves as the foundation for all microservices. Changes here affect the entire system, so thorough testing and documentation are required for all modifications.

## 🔐 Security Integration Notes

### **For Service Integration**
Services can now use the centralized security components:

```python
# Import security components
from common.security import PasswordManager, TokenManager, AuditLogger

# Use in services
password_manager = PasswordManager()
token_manager = TokenManager()
audit_logger = AuditLogger()

# Password operations
hashed_password = password_manager.hash_password("user_password")
is_valid = password_manager.verify_password("user_password", hashed_password)

# Token operations
token_data = token_manager.create_access_token("username", "role")
username = token_manager.verify_access_token(token)

# Audit logging
audit_logger.log_login_success("username", ip_address="192.168.1.1")
audit_logger.log_access_denied("username", "/admin", "insufficient_permissions")
```

### **Migration from Service-Specific Security**
- Remove duplicate password hashing logic from services
- Replace service-specific JWT utilities with `TokenManager`
- Add audit logging for security events
- Update tests to use centralized security components