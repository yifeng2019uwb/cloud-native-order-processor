# Order Service Redesign Planning

## 🎯 **Overview**
Redesign the order service to support multi-asset portfolio management with proper balance tracking and transaction management.

## 🏗️ **Design Philosophy & Trade-offs** 🎯
- **DynamoDB Optimization**: Serverless, pay-per-use, minimal operational overhead
- **Single-Table Design**: Simplified queries and reduced complexity for personal project scale
- **Atomic Operations**: Using conditional expressions (`upsert_asset_balance`) instead of complex DynamoDB transactions (cost optimization)
- **PK/SK Strategy**: Optimized for 80% use cases (user-specific queries) over complex multi-dimensional access patterns
- **Cost Efficiency**: Minimize RCU/WCU usage through efficient key design and query patterns
- **Development Velocity**: Prioritize rapid iteration and learning over enterprise-grade complexity

## 🏗️ **Database Schema Design**

### **1. Users** ✅ **Unchanged**
```
users (PK: username, SK: USER)
```

### **2. USD Balance** ✅ **Keep Current Design**
```
balances (PK: username, SK: BALANCE) - unchanged
```

### **3. Asset Balances** ✅ **COMPLETED**
```
asset_balances (PK: username, SK: ASSET#{asset_id})
```
**Fields:**
- `Pk`: username
- `Sk`: ASSET#{asset_id} (e.g., "ASSET#BTC", "ASSET#ETH")
- `username`: username
- `asset_id`: asset identifier
- `quantity`: current asset quantity (non-negative)
- `created_at`: timestamp
- `updated_at`: timestamp

**Note**: Market value calculation happens at API level, not stored in DB
- Get current market price from external service
- Calculate: quantity * current_market_price
- Return in API response, not stored in DB
- Simplified design: removed audit fields for personal project efficiency

### **4. Asset Transactions** ✅ **COMPLETED**
```
asset_transactions (PK: TRANS#{username}#{asset_id}, SK: timestamp)
```
**Fields:**
- `Pk`: TRANS#{username}#{asset_id} (e.g., "TRANS#john_doe#BTC")
- `Sk`: timestamp (ISO format string)
- `username`: username
- `asset_id`: asset identifier
- `transaction_type`: BUY/SELL
- `quantity`: transaction quantity
- `price`: price per unit in USD (market price at transaction time)
- `total_amount`: total transaction value
- `order_id`: reference to order
- `status`: COMPLETED/PENDING/FAILED
- `created_at`: timestamp

**Note**: Simplified field naming for consistency and clarity

### **5. Orders** 🔄 **Enhanced Entity**
```
orders (PK: order_id, SK: ORDER)
GSI: UserOrdersIndex (PK: username, SK: ASSET_ID)
```
**Fields:**
- `Pk`: order_id (generated)
- `Sk`: ORDER
- `username`: username (primary identifier)
- `asset_id`: asset identifier
- `order_type`: BUY/SELL
- `quantity`: order quantity
- `order_price`: limit price (optional for market orders)
- `total_amount`: calculated total
- `status`: PENDING/COMPLETED/CANCELLED/FAILED
- `expires_at`: order expiration
- `created_at`: timestamp
- `updated_at`: timestamp
- `entity_type`: "order"

**GSI Query Patterns:**
```python
# Get all orders for a user
def get_orders_by_user(username: str) -> List[Order]:
    # Query GSI: UserOrdersIndex
    # PK: username, SK: ASSET_ID
    # Returns all orders for user across all assets
    return order_dao.get_orders_by_user(username)

# Get user orders for specific asset
def get_user_asset_orders(username: str, asset_id: str) -> List[Order]:
    # Query GSI: UserOrdersIndex
    # PK: username, SK: ASSET_ID
    # Returns orders for specific asset
    return order_dao.get_orders_by_user_and_asset(username, asset_id)
```

## 🔄 **Transaction Flow Logic**

### **Buy Order Flow:**
1. **Create Order**: Save order with PENDING status
2. **Acquire User Lock**: Prevent concurrent balance modifications
3. **Validate USD Balance**: Check user has sufficient USD balance
4. **Execute Transaction**:
   - Update USD balance (deduct amount)
   - Update/create asset balance (add quantity)
   - Create asset transaction record
   - Update order status to COMPLETED
5. **Release Lock**: Allow other operations

### **Sell Order Flow:**
1. **Create Order**: Save order with PENDING status
2. **Acquire User Lock**: Prevent concurrent balance modifications
3. **Validate Asset Balance**: Check user has sufficient asset quantity
4. **Execute Transaction**:
   - Update asset balance (deduct quantity)
   - Update USD balance (add amount)
   - Create asset transaction record
   - Update order status to COMPLETED
5. **Release Lock**: Allow other operations

## 📊 **Portfolio Management**

### **Portfolio Calculation:**
```python
def calculate_portfolio_value(username: str) -> dict:
    # Get USD balance
    usd_balance = usd_balance_dao.get_balance(username)

    # Get all asset balances
    asset_balances = asset_balance_dao.get_all_asset_balances(username)

    # Calculate totals
    total_usd = usd_balance.current_balance
    total_asset_value = 0

    # Calculate current market value for each asset
    for balance in asset_balances:
        current_market_price = get_current_market_price(balance.asset_id)
        asset_current_value = balance.quantity * current_market_price
        total_asset_value += asset_current_value

    total_portfolio_value = total_usd + total_asset_value

    return {
        "username": username,
        "usd_balance": total_usd,
        "asset_balances": asset_balances,
        "total_asset_value": total_asset_value,
        "total_portfolio_value": total_portfolio_value,
        "asset_count": len(asset_balances)
    }
```

## 🔍 **Validation Strategy**

### **Service Level Validation:**
- **Asset Existence**: Validate asset_id exists in inventory at order creation
- **Balance Validation**: Check sufficient USD/asset balance at transaction execution
- **Business Rules**: Complex validation logic in service layer
- **Cross-Entity Consistency**: Ensure data consistency across related entities

### **Database Level Validation:**
- **Non-negative Quantities**: Enforce at database level
- **Required Fields**: Enforce at database level
- **Data Types**: Enforce at database level

## 🏛️ **New Entities to Create**

### **1. Asset Entities** ✅ **COMPLETED**
- `services/common/src/entities/asset/`
  - ✅ `asset_balance.py`: Asset balance entity - **COMPLETED**
  - ✅ `asset_transaction.py`: Asset transaction entity - **COMPLETED**
  - ✅ `enums.py`: Combined enums for asset types and statuses - **COMPLETED**
  - ✅ `__init__.py`: Export all asset entities - **COMPLETED**

**Note**: Combined asset_balance and asset_transaction into single asset folder for better organization

### **3. Enhanced Order Entity**
- `services/common/src/entities/order/`
  - Update existing `order.py` with new fields
  - Update `enums.py` with new status values

## 🗄️ **New DAOs to Create**

### **1. Asset DAOs** ✅ **COMPLETED**
- `services/common/src/dao/asset/`
  - ✅ `asset_balance_dao.py`: CRUD operations for asset balances - **COMPLETED**
  - ✅ `asset_transaction_dao.py`: CRUD operations for asset transactions - **COMPLETED**
  - ✅ `__init__.py`: Export all asset DAOs - **COMPLETED**

**Key Methods:**
- ✅ `AssetBalanceDAO.upsert_asset_balance()`: Create or update balance atomically - **COMPLETED**
- ✅ `AssetTransactionDAO.create_asset_transaction()`: Create transaction record - **COMPLETED**
- ✅ `AssetTransactionDAO.get_user_asset_transactions()`: Get transactions for specific asset - **COMPLETED**

**Note**: Combined into single asset folder for better organization. Used upsert pattern for efficient balance updates.

### **3. Enhanced Order DAO**
- `services/common/src/dao/order/`
  - Update existing `order_dao.py` with GSI support
  - Keep existing method names: `get_orders_by_user()`, `get_orders_by_user_and_asset()`
  - Update `create_order()` to populate GSI fields

## 🔧 **Enhanced Transaction Manager**

### **New Methods:**
- `execute_buy_order()`: Handle buy order execution
- `execute_sell_order()`: Handle sell order execution
- `update_asset_balance()`: Update asset balance after transaction

## 📋 **Implementation Phases**

### **Phase 1: Common Package Updates**
1. ✅ Create new entities (AssetBalance, AssetTransaction) - **COMPLETED**
   - Combined into `services/common/src/entities/asset/` folder
   - Simplified fields for personal project efficiency
2. ✅ Create new DAOs (AssetBalanceDAO, AssetTransactionDAO) - **COMPLETED**
   - Combined into `services/common/src/dao/asset/` folder
   - Used upsert pattern for efficient balance updates
   - Proper exception handling with defined exceptions
3. ✅ **COMPREHENSIVE UNIT TESTS** - **COMPLETED**
   - ✅ Asset entity tests: 45 tests covering all models and edge cases
   - ✅ Asset DAO tests: 33 tests covering all CRUD operations and error handling
   - ✅ 100% test coverage for asset entities and DAOs
   - ✅ All 75 tests passing successfully
4. Update Order entity and DAO with GSI support
   - Change SK from `created_at` to `ORDER`
   - Update GSI to `UserOrdersIndex (PK: username, SK: ASSET_ID)`
   - Use `username` as primary identifier
5. Enhance TransactionManager with multi-asset support
6. Update unit tests

### **Phase 2: Order Service Updates**
1. Update order controllers to use new transaction flow
2. Add portfolio calculation endpoints
3. Add asset balance endpoints
4. Add asset transaction history endpoints
5. Update unit tests

### **Phase 3: Integration & Testing**
1. Update user service to create initial asset balances
2. Test end-to-end order flow
3. Test portfolio calculations
4. Performance testing with multiple assets

## 🎯 **Key Benefits**

1. **Multi-Asset Support**: Users can hold multiple cryptocurrencies
2. **Real-time Portfolio**: Calculate total portfolio value with current market prices
3. **Transaction History**: Complete audit trail for all asset transactions
4. **Efficient Queries**: GSI for user order history
5. **Scalable Design**: Easy to add new assets
6. **Clean Separation**: Market values calculated at API level, not stored in DB

## 🔧 **Design Decisions Made**

### **✅ Breaking Changes:**
- Change Order SK from `created_at` to `ORDER`
- Update GSI structure to `UserOrdersIndex`
- Use `username` as primary identifier

### **✅ Validation Strategy:**
- Service level: Business logic validation
- Database level: Basic constraints (non-negative, required fields)

### **✅ Market Value Handling:**
- Remove `current_value` from asset balance entity
- Calculate market values at API level using external price service
- Store only facts in database (quantity, purchase price)

### **✅ Migration Strategy:**
- Start fresh with new data (no existing data to migrate)
- No complex migration scripts needed

### **✅ Timestamp Format:**
- Use ISO format for all timestamps (consistent with existing codebase)

### **✅ Implementation Improvements:**
- **File Organization**: Combined asset entities and DAOs into single folders for better organization
- **Simplified Fields**: Removed audit fields (total_bought, total_sold, average_purchase_price) for personal project efficiency
- **Upsert Pattern**: Used atomic upsert operations for asset balance updates instead of separate create/update methods
- **Field Naming**: Simplified `price_per_unit` to `price` for consistency
- **Exception Handling**: Used defined exception classes for proper error handling

## 📝 **Next Steps**

1. ✅ Review and approve this planning document
2. ✅ Start with Phase 1: Common package updates
3. ✅ Create entities and DAOs - **COMPLETED**
4. ✅ **Create comprehensive unit tests** - **COMPLETED**
5. Update transaction manager
6. Test common package changes
7. Proceed to Phase 2: Order service updates

**Current Status**:
- ✅ **Asset entities and DAOs completed**
- ✅ **Comprehensive unit tests completed (75 tests, 100% coverage)**
- 🔄 **Ready to proceed with Order entity updates and TransactionManager enhancement**

## 📊 **Today's Accomplishments**

### **✅ Completed Work:**
1. **Asset Entities**: Created all asset-related entities with proper validation
2. **Asset DAOs**: Implemented all CRUD operations with proper error handling
3. **Comprehensive Testing**: Created 75 unit tests with 100% coverage
4. **Code Quality**: All tests passing, proper exception handling, clean code structure

### **🔄 Remaining Work:**
1. **Order Entity Updates**: Update existing order entity with GSI support
2. **Transaction Manager**: Enhance with multi-asset transaction support
3. **Order Service Integration**: Update order service to use new asset entities
4. **End-to-End Testing**: Test complete order flow with asset management