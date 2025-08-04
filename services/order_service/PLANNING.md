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
- `quantity`: current asset quantity
- `current_value`: current USD value
- `average_purchase_price`: average purchase price in USD
- `created_at`: timestamp
- `updated_at`: timestamp
- `entity_type`: "asset_balance"

### **4. Asset Transactions** 🆕 **New Entity**
```
asset_transactions (PK: TRANS_ASSETID_username, SK: timestamp)
```
**Fields:**
- `Pk`: TRANS_{asset_id}_{username} (e.g., "TRANS_BTC_john_doe")
- `Sk`: timestamp (ISO format)
- `username`: username
- `asset_id`: asset identifier
- `transaction_type`: BUY/SELL
- `quantity`: transaction quantity
- `price_per_unit`: price per unit in USD
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
- `user_id`: username
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

## 🔄 **Transaction Flow Logic**

### **Buy Order Flow:**
1. **Validate Order**: Check user has sufficient USD balance
2. **Create Order**: Save order with PENDING status
3. **Execute Order**:
   - Deduct USD from user balance
   - Add asset quantity to user's asset balance
   - Create asset transaction record
   - Update order status to COMPLETED
4. **Update Balances**: Recalculate asset current_value

### **Sell Order Flow:**
1. **Validate Order**: Check user has sufficient asset quantity
2. **Create Order**: Save order with PENDING status
3. **Execute Order**:
   - Deduct asset quantity from user's asset balance
   - Add USD to user balance
   - Create asset transaction record
   - Update order status to COMPLETED
4. **Update Balances**: Recalculate asset current_value

## 📊 **Portfolio Management**

### **Portfolio Calculation:**
```python
def calculate_portfolio_value(user_id: str) -> dict:
    # Get USD balance
    usd_balance = usd_balance_dao.get_balance(user_id)

    # Get all asset balances
    asset_balances = asset_balance_dao.get_all_asset_balances(user_id)

    # Calculate totals
    total_usd = usd_balance.current_balance
    total_asset_value = sum(balance.current_value for balance in asset_balances)
    total_portfolio_value = total_usd + total_asset_value

    return {
        "user_id": user_id,
        "usd_balance": total_usd,
        "asset_balances": asset_balances,
        "total_asset_value": total_asset_value,
        "total_portfolio_value": total_portfolio_value,
        "asset_count": len(asset_balances)
    }
```

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

## 🔧 **Enhanced Transaction Manager**

### **New Methods:**
- `execute_buy_order()`: Handle buy order execution
- `execute_sell_order()`: Handle sell order execution
- `update_asset_balance()`: Update asset balance after transaction
- `calculate_asset_value()`: Calculate current asset value

## 📋 **Implementation Phases**

### **Phase 1: Common Package Updates**
1. Create new entities (AssetBalance, AssetTransaction)
2. Create new DAOs (AssetBalanceDAO, AssetTransactionDAO)
3. Update Order entity and DAO with GSI support
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
2. **Real-time Portfolio**: Calculate total portfolio value
3. **Transaction History**: Complete audit trail for all asset transactions
4. **Efficient Queries**: GSI for user order history
5. **Scalable Design**: Easy to add new assets

## ❓ **Open Questions**

1. **Asset Price Updates**: How often should we update `current_value`?
2. **Market Price Integration**: How to get real-time asset prices?
3. **Order Matching**: Will we implement order matching engine?
4. **Portfolio Caching**: Should we cache portfolio calculations?

## 📝 **Next Steps**

1. Review and approve this planning document
2. Start with Phase 1: Common package updates
3. Create entities and DAOs
4. Update transaction manager
5. Test common package changes
6. Proceed to Phase 2: Order service updates