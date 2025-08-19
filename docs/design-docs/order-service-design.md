# 📋 Order Service Design

## 🎯 **Purpose**
Document design decisions, options considered, and rationale for the Order Service to prevent re-designing and maintain consistency.

---

## 📋 **Component Design: Order Service**
**Date**: 2025-08-20
**Author**: System Design Team
**Status**: Completed

#### **🎯 Problem Statement**
- **Problem**: Need order processing and portfolio management system for trading operations
- **Requirements**: Order creation, execution, portfolio tracking, balance integration
- **Constraints**: Real-time processing, atomic operations, balance validation, multi-asset support

#### **🔍 Options Considered**

- **Option A: Simple Order Tracking**
  - ✅ Pros: Easy to implement, simple data model
  - ❌ Cons: Limited functionality, no portfolio management, basic trading
  - 💰 Cost: Low cost, limited business value
  - ⏱️ Complexity: Low complexity, low functionality

- **Option B: Full Trading Platform (Chosen)**
  - ✅ Pros: Complete trading functionality, portfolio management, real-time updates
  - ❌ Cons: More complex implementation, higher development cost
  - 💰 Cost: Medium cost, high business value
  - ⏱️ Complexity: Medium complexity, high functionality

- **Option C: Third-Party Trading Integration**
  - ✅ Pros: Quick implementation, proven reliability, advanced features
  - ❌ Cons: Vendor lock-in, limited customization, ongoing costs
  - 💰 Cost: High cost, medium business value
  - ⏱️ Complexity: Low complexity, medium customization

#### **🏗️ Final Decision**
- **Chosen Option**: Custom trading platform with comprehensive order management
- **Rationale**: Full control over functionality, cost-effective for personal project, learning opportunity
- **Trade-offs Accepted**: Higher development cost for complete trading capabilities

#### **🔧 Implementation Details**

**Key Components**:
- **Order Controller**: Order creation, management, and execution
- **Asset Controller**: Asset balance tracking and management
- **Portfolio Controller**: Portfolio calculation and management
- **Integration**: User Service (balance validation), Inventory Service (asset data)

**Data Structures**:
- **Order Entity**: order_id, username, asset_id, order_type, status, quantity, price
- **Asset Balance Entity**: username, asset_id, quantity, last_updated
- **Asset Transaction Entity**: transaction_id, username, asset_id, type, quantity, price, order_id

**Configuration**:
- **Order Types**: Market buy/sell, limit buy/sell (future)
- **Order Status**: Pending, confirmed, processing, completed, cancelled, failed
- **Transaction Types**: BUY, SELL
- **Balance Validation**: Pre-order balance checks, atomic operations

#### **🧪 Testing Strategy**
- **Unit Tests**: Order logic, validation, business rules
- **Integration Tests**: Service communication, balance integration
- **End-to-End Tests**: Complete trading workflows, portfolio calculations
- **Performance Tests**: Order processing speed, concurrent operations

#### **📝 Notes & Future Considerations**
- **Known Limitations**: Basic order types, no advanced trading features
- **Future Improvements**: Limit orders, stop-loss, take-profit, order book

---

## 📝 **Quick Decision Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Order Types | Market orders first | Simplicity, immediate value | High | ✅ Done |
| 8/17 | Portfolio | Real-time calculation | User experience, accuracy | High | ✅ Done |
| 8/17 | Balance Integration | Atomic operations | Data consistency | Medium | ✅ Done |
| 8/17 | Asset Management | Multi-asset support | Trading flexibility | Medium | ✅ Done |

**Status Indicators:**
- ✅ **Done** - Decision implemented and working
- 🔄 **In Progress** - Decision made, implementation ongoing
- 📋 **Planned** - Decision made, not yet started
- ❌ **Rejected** - Decision was made but later rejected
- 🔍 **Under Review** - Decision being reconsidered

---

## 🏗️ **Simple Architecture Diagrams**

### **Order Service Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Order Service │    │   Common        │
│   (Auth Check)  │◄──►│   (FastAPI)     │◄──►│   Package       │
│                 │    │   - Controllers │    │   - Entities    │
│                 │    │   - Validation  │    │   - DAOs        │
│                 │    │   - Business    │    │   - Security    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   - Orders      │
                       │   - Asset       │
                       │   Balances      │
                       │   - Asset       │
                       │   Transactions  │
                       └─────────────────┘
```

### **Order Processing Flow**
```
1. Order Creation Request
2. Balance Validation (User Service)
3. Asset Availability Check (Inventory Service)
4. Order Record Creation
5. Balance Transaction Creation
6. Asset Balance Update
7. Asset Transaction Record
8. Order Status Update
9. Response to Client
```

---

## 🔐 **API Design & Models**

### **Order Management Endpoints**

#### **Create Order**
```python
# Request Model
class OrderCreateRequest(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=10)
    order_type: OrderType = Field(...)
    quantity: Decimal = Field(..., gt=0, le=1000000)
    description: Optional[str] = Field(None, max_length=500)

# Response Model
class OrderCreateResponse(BaseModel):
    success: bool
    message: str
    data: Optional[OrderData]
    timestamp: datetime

class OrderData(BaseModel):
    order_id: str
    username: str
    asset_id: str
    order_type: OrderType
    status: OrderStatus
    quantity: Decimal
    price: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
```

#### **Get Order Details**
```python
# Response Model
class OrderDetailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[OrderData]
    timestamp: datetime
```

#### **List User Orders**
```python
# Request Model
class OrderListRequest(BaseModel):
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)
    order_type: Optional[OrderType] = None
    status: Optional[OrderStatus] = None
    asset_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Response Model
class OrderListResponse(BaseModel):
    success: bool
    message: str
    data: Optional[OrderListData]
    timestamp: datetime

class OrderListData(BaseModel):
    username: str
    orders: List[OrderData]
    total_count: int
    has_more: bool
```

#### **Cancel Order**
```python
# Request Model
class OrderCancelRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)

# Response Model
class OrderCancelResponse(BaseModel):
    success: bool
    message: str
    data: Optional[OrderData]
    timestamp: datetime
```

### **Asset Management Endpoints**

#### **Get Asset Balance**
```python
# Response Model
class AssetBalanceResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetBalanceData]
    timestamp: datetime

class AssetBalanceData(BaseModel):
    username: str
    asset_id: str
    quantity: Decimal
    current_price: Decimal
    market_value: Decimal
    last_updated: datetime
```

#### **Get All Asset Balances**
```python
# Request Model
class AssetBalancesRequest(BaseModel):
    limit: Optional[int] = Field(100, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)

# Response Model
class AssetBalancesResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetBalancesData]
    timestamp: datetime

class AssetBalancesData(BaseModel):
    username: str
    asset_balances: List[AssetBalanceData]
    total_count: int
    total_market_value: Decimal
    has_more: bool
```

#### **Get Asset Transaction History**
```python
# Request Model
class AssetTransactionHistoryRequest(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=10)
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)
    transaction_type: Optional[AssetTransactionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Response Model
class AssetTransactionHistoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetTransactionHistoryData]
    timestamp: datetime

class AssetTransactionHistoryData(BaseModel):
    username: str
    asset_id: str
    transactions: List[AssetTransactionData]
    total_count: int
    has_more: bool

class AssetTransactionData(BaseModel):
    transaction_id: str
    username: str
    asset_id: str
    transaction_type: AssetTransactionType
    quantity: Decimal
    price: Decimal
    total_amount: Decimal
    order_id: str
    status: AssetTransactionStatus
    timestamp: datetime
```

### **Portfolio Management Endpoints**

#### **Get User Portfolio**
```python
# Response Model
class PortfolioResponse(BaseModel):
    success: bool
    message: str
    data: Optional[PortfolioData]
    timestamp: datetime

class PortfolioData(BaseModel):
    username: str
    usd_balance: Decimal
    total_asset_value: Decimal
    total_portfolio_value: Decimal
    asset_count: int
    assets: List[PortfolioAssetData]
    last_updated: datetime

class PortfolioAssetData(BaseModel):
    asset_id: str
    quantity: Decimal
    current_price: Decimal
    market_value: Decimal
    percentage: Decimal
    last_updated: datetime
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

#### **Health Readiness**
```python
# Response Model
class HealthReadyResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    redis: str
    external_services: Dict[str, str]
```

#### **Health Liveness**
```python
# Response Model
class HealthLiveResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
```

---

## 🔗 **Related Documentation**

- **[Services Design](./services-design.md)**: Overall services architecture
- **[User Service Design](./user-service-design.md)**: Balance management integration
- **[Inventory Service Design](./inventory-service-design.md)**: Asset data integration
- **[Common Package Design](./common-package-design.md)**: Shared components design
- **[Order Service README](../services/order_service/README.md)**: Implementation and usage guide

---

**🎯 This order service design provides comprehensive order processing, portfolio management, and multi-asset trading capabilities with detailed API models.**
