# Order Service Redesign Planning

## 🎯 **Overview**
Redesign the order service to support multi-asset portfolio management with proper balance tracking and transaction management.

## 🏗️ **Database Schema Design**

### **1. Users** ✅ **Unchanged**
```
users (PK: username, SK: USER)
```

### **2. USD Balance** ✅ **Keep Current Design**
```
balances (PK: username, SK: BALANCE) - unchanged
```

### **3. Asset Balances** 🆕 **New Entity**
```
asset_balances (PK: username, SK: ASSET#{asset_id})
```
**Fields:**
- `Pk`: username
- `Sk`: ASSET#{asset_id} (e.g., "ASSET#BTC", "ASSET#ETH")
- `username`: username
- `asset_id`: asset identifier
- `quantity`: current asset quantity (non-negative)
- `average_purchase_price`: average purchase price in USD
- `total_bought`: total quantity bought (for audit)
- `total_sold`: total quantity sold (for audit)
- `last_transaction_at`: timestamp of last transaction
- `created_at`: timestamp
- `updated_at`: timestamp
- `entity_type`: "asset_balance"

**Note**: Market value calculation happens at API level, not stored in DB
- Get current market price from external service
- Calculate: quantity * current_market_price
- Return in API response, not stored in DB

### **4. Asset Transactions** 🆕 **New Entity**
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
- `price_per_unit`: price per unit in USD (market price at transaction time)
- `total_amount`: total transaction value
- `order_id`: reference to order
- `status`: COMPLETED/PENDING/FAILED
- `created_at`: timestamp
- `entity_type`: "asset_transaction"

### **5. Orders** 🔄 **Enhanced Entity**
```
orders (PK: order_id, SK: ORDER)
GSI: UserOrdersIndex (PK: username, SK: ASSET_ID)
```
**Fields:**
- `Pk`: order_id (generated)
- `Sk`: ORDER
- `username`: username (changed from user_id for consistency)
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

### **1. Asset Balance Entity**
- `services/common/src/entities/asset_balance/`
  - `asset_balance.py`: Main entity
  - `enums.py`: Transaction types, status

### **2. Asset Transaction Entity**
- `services/common/src/entities/asset_transaction/`
  - `asset_transaction.py`: Main entity
  - `enums.py`: Transaction types, status

### **3. Enhanced Order Entity**
- `services/common/src/entities/order/`
  - Update existing `order.py` with new fields
  - Update `enums.py` with new status values

## 🗄️ **New DAOs to Create**

### **1. Asset Balance DAO**
- `services/common/src/dao/asset_balance/`
  - `asset_balance_dao.py`: CRUD operations for asset balances

### **2. Asset Transaction DAO**
- `services/common/src/dao/asset_transaction/`
  - `asset_transaction_dao.py`: CRUD operations for asset transactions

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
1. Create new entities (AssetBalance, AssetTransaction)
2. Create new DAOs (AssetBalanceDAO, AssetTransactionDAO)
3. Update Order entity and DAO with GSI support
   - Change SK from `created_at` to `ORDER`
   - Update GSI to `UserOrdersIndex (PK: username, SK: ASSET_ID)`
   - Change `user_id` to `username` for consistency
4. Enhance TransactionManager with multi-asset support
5. Update unit tests

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
- Change `user_id` to `username` for consistency

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

## 📝 **Next Steps**

1. ✅ Review and approve this planning document
2. Start with Phase 1: Common package updates
3. Create entities and DAOs
4. Update transaction manager
5. Test common package changes
6. Proceed to Phase 2: Order service updates