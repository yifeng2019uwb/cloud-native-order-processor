# 🔧 Common Package Design

## 🎯 **Purpose**
Document design decisions, options considered, and rationale for the Common Package to prevent re-designing and maintain consistency.

---

## 📋 **Component Design: Common Package**
**Date**: 2025-08-20
**Author**: System Design Team
**Status**: Completed

#### **🎯 Problem Statement**
- **Problem**: Need shared components and utilities across all microservices
- **Requirements**: Data models, database access, security, validation, exceptions
- **Constraints**: Python ecosystem, AWS integration, maintainability, consistency

#### **🔍 Options Considered**

- **Option A: Duplicate Code in Each Service**
  - ✅ Pros: Service independence, no shared dependencies
  - ❌ Cons: Code duplication, maintenance overhead, inconsistency
  - 💰 Cost: Low initial cost, high long-term cost
  - ⏱️ Complexity: Low complexity, high maintenance

- **Option B: Shared Package (Chosen)**
  - ✅ Pros: Code reuse, consistency, centralized maintenance
  - ❌ Cons: Coupling between services, version management complexity
  - 💰 Cost: Medium initial cost, low long-term cost
  - ⏱️ Complexity: Medium complexity, low maintenance

- **Option C: Microservice Template**
  - ✅ Pros: Consistent structure, easy service creation
  - ❌ Cons: Rigid structure, limited flexibility, over-engineering
  - 💰 Cost: High initial cost, medium long-term cost
  - ⏱️ Complexity: High complexity, medium maintenance

#### **🏗️ Final Decision**
- **Chosen Option**: Shared package with modular components and dependency injection
- **Rationale**: Perfect balance of code reuse, consistency, and maintainability
- **Trade-offs Accepted**: Service coupling for development efficiency and consistency

#### **🔧 Implementation Details**

**Key Components**:
- **Entities**: Shared data models and business objects
- **DAOs**: Data Access Objects for database operations
- **Security**: Centralized authentication and authorization
- **Database**: Connection management and utilities
- **Exceptions**: Domain-specific error handling
- **Validation**: Input validation and business rules

**Data Structures**:
- **User Entities**: User, Balance, BalanceTransaction
- **Order Entities**: Order, OrderCreate, OrderResponse
- **Asset Entities**: Asset, AssetBalance, AssetTransaction
- **Shared Models**: Pydantic-based validation and serialization

**Configuration**:
- **Database**: DynamoDB connection and configuration
- **Security**: JWT settings, password policies, audit logging
- **Validation**: Field constraints, business rules, error messages
- **Dependencies**: Service injection and configuration management

#### **🧪 Testing Strategy**
- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: Database operations and external service integration
- **Security Tests**: Authentication, authorization, and validation
- **Performance Tests**: Database query optimization and caching

#### **📝 Notes & Future Considerations**
- **Known Limitations**: Service coupling, version management complexity
- **Future Improvements**: Advanced caching, connection pooling, performance optimization

---

## 📝 **Quick Decision Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Architecture | Shared package over duplication | Code reuse, consistency | High | ✅ Done |
| 8/17 | Database | DynamoDB over PostgreSQL | Serverless, cost efficiency | Medium | ✅ Done |
| 8/17 | Security | Centralized over distributed | Consistency, maintainability | Medium | ✅ Done |
| 8/17 | Validation | Pydantic over custom | Type safety, validation | Low | ✅ Done |

**Status Indicators:**
- ✅ **Done** - Decision implemented and working
- 🔄 **In Progress** - Decision made, implementation ongoing
- 📋 **Planned** - Decision made, not yet started
- ❌ **Rejected** - Decision was made but later rejected
- 🔍 **Under Review** - Decision being reconsidered

---

## 🏗️ **Simple Architecture Diagrams**

### **Common Package Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Microservices │    │   Common        │    │   External      │
│   (FastAPI)     │◄──►│   Package       │◄──►│   Services      │
│                 │    │   - Entities    │    │   - AWS         │
│                 │    │   - DAOs        │    │   - DynamoDB    │
│                 │    │   - Security    │    │   - Redis       │
│                 │    │   - Validation  │    │   - IAM         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   - DynamoDB    │
                       │   - Redis       │
                       │   - IAM Roles   │
                       └─────────────────┘
```

### **Component Integration Flow**
```
1. Service Request
2. Common Package Import
3. Entity Validation
4. DAO Operations
5. Database Interaction
6. Security Checks
7. Response Transformation
8. Service Response
```

---

## 🔐 **API Design & Models**

### **Entity Models**

#### **User Entity**
```python
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    password_hash: str = Field(..., min_length=60, max_length=60)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = Field(UserRole.CUSTOMER)
    status: UserStatus = Field(UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
```

#### **Balance Entity**
```python
class Balance(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    current_balance: Decimal = Field(..., ge=0)
    total_deposits: Decimal = Field(..., ge=0)
    total_withdrawals: Decimal = Field(..., ge=0)
    total_orders: Decimal = Field(..., ge=0)
    total_refunds: Decimal = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_transaction: Optional[datetime] = None
```

#### **Balance Transaction Entity**
```python
class BalanceTransaction(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    amount: Decimal = Field(..., gt=0)
    transaction_type: TransactionType = Field(...)
    status: TransactionStatus = Field(TransactionStatus.PENDING)
    description: Optional[str] = Field(None, max_length=500)
    reference_id: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
```

#### **Order Entity**
```python
class Order(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    asset_id: str = Field(..., min_length=1, max_length=10)
    order_type: OrderType = Field(...)
    status: OrderStatus = Field(OrderStatus.PENDING)
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
```

#### **Asset Entity**
```python
class Asset(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=10)
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    current_price: Decimal = Field(..., gt=0)
    market_cap: Optional[Decimal] = Field(None, ge=0)
    volume_24h: Optional[Decimal] = Field(None, ge=0)
    price_change_24h: Optional[Decimal] = None
    price_change_percentage_24h: Optional[Decimal] = None
    status: AssetStatus = Field(AssetStatus.ACTIVE)
    category: AssetCategory = Field(AssetCategory.CRYPTOCURRENCY)
    website: Optional[str] = Field(None, max_length=500)
    whitepaper: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_price_update: datetime = Field(default_factory=datetime.utcnow)
```

#### **Asset Balance Entity**
```python
class AssetBalance(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    asset_id: str = Field(..., min_length=1, max_length=10)
    quantity: Decimal = Field(..., ge=0)
    average_purchase_price: Decimal = Field(..., gt=0)
    total_invested: Decimal = Field(..., ge=0)
    current_market_value: Decimal = Field(..., ge=0)
    unrealized_pnl: Decimal = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_transaction: Optional[datetime] = None
```

#### **Asset Transaction Entity**
```python
class AssetTransaction(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    asset_id: str = Field(..., min_length=1, max_length=10)
    transaction_type: AssetTransactionType = Field(...)
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    order_id: str = Field(..., min_length=1, max_length=100)
    status: AssetTransactionStatus = Field(AssetTransactionStatus.PENDING)
    fees: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### **Enum Models**

#### **User Role**
```python
class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MODERATOR = "moderator"
```

#### **User Status**
```python
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
```

#### **Transaction Type**
```python
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    ORDER_PAYMENT = "order_payment"
    ORDER_REFUND = "order_refund"
    SYSTEM_ADJUSTMENT = "system_adjustment"
    TRANSFER = "transfer"
```

#### **Transaction Status**
```python
class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PROCESSING = "processing"
```

#### **Order Type**
```python
class OrderType(str, Enum):
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
```

#### **Order Status**
```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    EXPIRED = "expired"
```

#### **Asset Status**
```python
class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
```

#### **Asset Category**
```python
class AssetCategory(str, Enum):
    CRYPTOCURRENCY = "cryptocurrency"
    STABLECOIN = "stablecoin"
    TOKEN = "token"
    NFT = "nft"
    COMMODITY = "commodity"
```

#### **Asset Transaction Type**
```python
class AssetTransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    TRANSFER = "transfer"
    AIRDROP = "airdrop"
    STAKING = "staking"
```

#### **Asset Transaction Status**
```python
class AssetTransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PROCESSING = "processing"
```

---

## 🔗 **Related Documentation**

- **[Services Design](./services-design.md)**: Overall services architecture
- **[User Service Design](./user-service-design.md)**: User entity usage
- **[Order Service Design](./order-service-design.md)**: Order entity usage
- **[Inventory Service Design](./inventory-service-design.md)**: Asset entity usage
- **[Common Package README](../services/common/README.md)**: Implementation and usage guide

---

**🎯 This common package design provides shared components, entities, and utilities for all microservices with comprehensive data models and validation.**
