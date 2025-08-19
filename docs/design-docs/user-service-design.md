# 👤 User Service Design

## 🎯 **Purpose**
Document design decisions, options considered, and rationale for the User Service to prevent re-designing and maintain consistency.

---

## 📋 **Component Design: User Service**
**Date**: 2025-08-20
**Author**: System Design Team
**Status**: Completed

#### **🎯 Problem Statement**
- **Problem**: Need secure user authentication and balance management system
- **Requirements**: User registration, login, profile management, balance operations
- **Constraints**: JWT authentication, secure password handling, atomic balance operations

#### **🔍 Options Considered**

- **Option A: Session-Based Authentication**
  - ✅ Pros: Simple, familiar, easy to implement
  - ❌ Cons: Server-side state, scaling issues, CSRF vulnerabilities
  - 💰 Cost: Low cost, high storage overhead
  - ⏱️ Complexity: Low complexity, high maintenance

- **Option B: JWT Authentication (Chosen)**
  - ✅ Pros: Stateless, scalable, secure, mobile-friendly
  - ❌ Cons: Token size, revocation complexity, storage requirements
  - 💰 Cost: Medium cost, low storage overhead
  - ⏱️ Complexity: Medium complexity, low maintenance

- **Option C: OAuth2/OpenID Connect**
  - ✅ Pros: Industry standard, third-party integration, security
  - ❌ Cons: Complex implementation, external dependencies, overkill
  - 💰 Cost: High cost, low storage overhead
  - ⏱️ Complexity: High complexity, low maintenance

#### **🏗️ Final Decision**
- **Chosen Option**: JWT-based authentication with centralized security management
- **Rationale**: Perfect balance of security, scalability, and implementation complexity
- **Trade-offs Accepted**: Token revocation complexity for stateless scalability

#### **🔧 Implementation Details**

**Key Components**:
- **Authentication Controller**: Login, registration, logout logic
- **Profile Controller**: User profile management
- **Balance Controller**: Balance operations and transaction management
- **Security Integration**: PasswordManager, TokenManager, AuditLogger

**Data Structures**:
- **User Entity**: username, email, password_hash, profile data
- **Balance Entity**: username, current_balance, total_deposits, total_withdrawals
- **Transaction Entity**: transaction_id, username, amount, type, status, timestamp

**Configuration**:
- **JWT Settings**: Secret key, algorithm, expiration time
- **Password Policy**: Minimum length, complexity requirements
- **Rate Limiting**: Login attempts, API calls per minute

#### **🧪 Testing Strategy**
- **Unit Tests**: Controller logic, validation, security components
- **Integration Tests**: Database operations, external service integration
- **Security Tests**: Password validation, JWT handling, rate limiting
- **API Tests**: Endpoint functionality, error handling, response validation

#### **📝 Notes & Future Considerations**
- **Known Limitations**: JWT token revocation requires additional infrastructure
- **Future Improvements**: OAuth2 integration, multi-factor authentication, social login

---

## 📝 **Quick Decision Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Auth Method | JWT over Sessions | Stateless, scalable | High | ✅ Done |
| 8/17 | Password Hashing | bcrypt over SHA | Security, industry standard | High | ✅ Done |
| 8/17 | Balance Operations | Atomic with Redis locks | Data consistency | Medium | ✅ Done |
| 8/17 | Security | Centralized over Distributed | Consistency, maintainability | Medium | ✅ Done |

**Status Indicators:**
- ✅ **Done** - Decision implemented and working
- 🔄 **In Progress** - Decision made, implementation ongoing
- 📋 **Planned** - Decision made, not yet started
- ❌ **Rejected** - Decision was made but later rejected
- 🔍 **Under Review** - Decision being reconsidered

---

## 🏗️ **Simple Architecture Diagrams**

### **User Service Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   User Service  │    │   Common        │
│   (Auth Check)  │◄──►│   (FastAPI)     │◄──►│   Package       │
│                 │    │   - Controllers │    │   - Entities    │
│                 │    │   - Validation  │    │   - DAOs        │
│                 │    │   - Security    │    │   - Security    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   - Users       │
                       │   - Balances    │
                       │   - Transactions│
                       └─────────────────┘
```

### **Authentication Flow**
```
1. User Login Request
2. Password Verification (bcrypt)
3. JWT Token Generation
4. Token Response to Client
5. Client Stores Token
6. Subsequent Requests Include Token
7. Gateway Validates Token
8. Service Processes Request
```

---

## 🔐 **API Design & Models**

### **Authentication Endpoints**

#### **User Registration**
```python
# Request Model
class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

# Response Model
class UserRegistrationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[UserProfile]
    timestamp: datetime
```

#### **User Login**
```python
# Request Model
class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

# Response Model
class UserLoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LoginData]
    timestamp: datetime

class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_profile: UserProfile
```

#### **User Logout**
```python
# Request Model
class UserLogoutRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)

# Response Model
class UserLogoutResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime
```

### **Profile Management Endpoints**

#### **Get User Profile**
```python
# Response Model
class UserProfileResponse(BaseModel):
    success: bool
    message: str
    data: Optional[UserProfile]
    timestamp: datetime

class UserProfile(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### **Update User Profile**
```python
# Request Model
class UserProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

# Response Model
class UserProfileUpdateResponse(BaseModel):
    success: bool
    message: str
    data: Optional[UserProfile]
    timestamp: datetime
```

### **Balance Management Endpoints**

#### **Get User Balance**
```python
# Response Model
class UserBalanceResponse(BaseModel):
    success: bool
    message: str
    data: Optional[BalanceData]
    timestamp: datetime

class BalanceData(BaseModel):
    username: str
    current_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    last_updated: datetime
```

#### **Deposit Funds**
```python
# Request Model
class DepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=1000000)
    description: Optional[str] = Field(None, max_length=500)

# Response Model
class DepositResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TransactionData]
    timestamp: datetime

class TransactionData(BaseModel):
    transaction_id: str
    username: str
    amount: Decimal
    transaction_type: TransactionType
    status: TransactionStatus
    description: Optional[str]
    created_at: datetime
```

#### **Withdraw Funds**
```python
# Request Model
class WithdrawRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=1000000)
    description: Optional[str] = Field(None, max_length=500)

# Response Model
class WithdrawResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TransactionData]
    timestamp: datetime
```

#### **Get Transaction History**
```python
# Request Model
class TransactionHistoryRequest(BaseModel):
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)
    transaction_type: Optional[TransactionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Response Model
class TransactionHistoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TransactionHistoryData]
    timestamp: datetime

class TransactionHistoryData(BaseModel):
    username: str
    transactions: List[TransactionData]
    total_count: int
    has_more: bool
```

### **System Endpoints**

#### **Health Check**
```python
# Response Model
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
    uptime: float
    database: str
    redis: str
```

#### **Metrics**
```python
# Response Model
class MetricsResponse(BaseModel):
    request_count: int
    error_count: int
    average_response_time: float
    active_users: int
    total_transactions: int
    timestamp: datetime
```

---

## 🔗 **Related Documentation**

- **[Services Design](./services-design.md)**: Overall services architecture
- **[Common Package Design](./common-package-design.md)**: Shared components design
- **[Exception Package Design](./exception-package-design.md)**: Error handling design
- **[User Service README](../services/user_service/README.md)**: Implementation and usage guide

---

**🎯 This user service design provides secure authentication, profile management, and balance operations with comprehensive API models and validation.**
