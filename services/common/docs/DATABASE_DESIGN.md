# 🗄️ Database Design Documentation

## 🎯 **Overview**
This document tracks the database schema designs, query patterns, and design decisions for the Cloud Native Order Processor system.

---

## 📊 **Database Architecture**

### **Design Philosophy**
- **Single-Table Design**: All entities stored in service-specific tables
- **Cost Optimization**: Minimize DynamoDB RCU/WCU usage
- **Query Efficiency**: Optimize for 80% use cases (user-specific queries)
- **Atomic Operations**: Use conditional expressions instead of complex transactions

---

## 🏗️ **Schema Designs**

### **1. Users Table Schema**
**Table**: `users`
**Service**: User Service
**Design Date**: 2024-01-01

#### **Key Structure**
```
PK: username
SK: USER
GSI2: EmailIndex (PK: email)
```

#### **Data Items**
```
User Records:
- PK: "john_doe"
- SK: "USER"
- username: "john_doe"
- email: "john@example.com"
- password_hash: "bcrypt_hash"
- created_at: "2024-01-01T12:00:00Z"
- updated_at: "2024-01-01T12:00:00Z"
- status: "ACTIVE"
```

#### **Query Patterns**
```python
# Get user by username (primary query)
def get_user_by_username(username: str):
    return table.get_item(Key={'PK': username, 'SK': 'USER'})

# Get user by email (GSI2 query)
def get_user_by_email(email: str):
    return table.get_item(
        IndexName='EmailIndex',
        Key={'email': email}
    )
```

#### **Design Decisions**
- **Why username as PK**: Direct user lookup, most common query pattern
- **Why USER as SK**: Distinguishes from other user-related items
- **Why email as GSI2 PK**: Enables email-based lookups for login/registration
- **No GSI2 SK**: Email is unique, no need for additional sorting

---

### **2. Balances Table Schema**
**Table**: `users` (same table as users)
**Service**: User Service
**Design Date**: 2024-01-01

#### **Key Structure**
```
PK: username
SK: BALANCE
```

#### **Data Items**
```
Balance Records:
- PK: "john_doe"
- SK: "BALANCE"
- username: "john_doe"
- current_balance: "1000.00"
- total_deposits: "1500.00"
- total_withdrawals: "500.00"
- created_at: "2024-01-01T12:00:00Z"
- updated_at: "2024-01-01T12:00:00Z"
```

#### **Query Patterns**
```python
# Get user balance
def get_balance(username: str):
    return table.get_item(Key={'PK': username, 'SK': 'BALANCE'})
```

#### **Design Decisions**
- **Same table as users**: Reduces table operations, cost efficient
- **BALANCE as SK**: Distinguishes from user records
- **Decimal precision**: Store as strings to avoid floating point issues

---

### **3. Balance Transactions Schema**
**Table**: `users` (same table as users)
**Service**: User Service
**Design Date**: 2024-01-01

#### **Key Structure**
```
PK: username
SK: TRANS#{transaction_id}
```

#### **Data Items**
```
Balance Transaction Records:
- PK: "john_doe"
- SK: "TRANS#deposit-123"
- username: "john_doe"
- transaction_id: "deposit-123"
- transaction_type: "DEPOSIT"
- amount: "500.00"
- previous_balance: "1000.00"
- new_balance: "1500.00"
- status: "COMPLETED"
- description: "Bank transfer"
- created_at: "2024-01-01T12:00:00Z"

- PK: "john_doe"
- SK: "TRANS#withdraw-456"
- username: "john_doe"
- transaction_id: "withdraw-456"
- transaction_type: "WITHDRAW"
- amount: "200.00"
- previous_balance: "1500.00"
- new_balance: "1300.00"
- status: "COMPLETED"
- description: "ATM withdrawal"
- created_at: "2024-01-02T12:00:00Z"

- PK: "john_doe"
- SK: "TRANS#order-payment-789"
- username: "john_doe"
- transaction_id: "order-payment-789"
- transaction_type: "ORDER_PAYMENT"
- amount: "100.00"
- previous_balance: "1300.00"
- new_balance: "1200.00"
- status: "COMPLETED"
- description: "Order #123 payment"
- order_id: "order-123"
- created_at: "2024-01-03T12:00:00Z"
```

#### **Query Patterns**
```python
# Get specific transaction
def get_transaction(username: str, transaction_id: str):
    return table.get_item(Key={'PK': username, 'SK': f'TRANS#{transaction_id}'})

# Get all transactions for user
def get_user_transactions(username: str, limit: int = 50):
    return table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={':pk': username, ':sk': 'TRANS#'},
        ScanIndexForward=False,  # Most recent first
        Limit=limit
    )

# Get transactions by type
def get_user_transactions_by_type(username: str, transaction_type: str, limit: int = 50):
    return table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        FilterExpression='transaction_type = :type',
        ExpressionAttributeValues={
            ':pk': username,
            ':sk': 'TRANS#',
            ':type': transaction_type
        },
        ScanIndexForward=False,
        Limit=limit
    )
```

#### **Design Decisions**
- **Why TRANS# prefix**: Distinguishes transaction records from other user items
- **Same table as users**: Cost efficient, user-centric queries
- **Transaction ID in SK**: Enables direct transaction lookup
- **Amount as string**: Avoid floating point precision issues
- **Balance tracking**: Store previous and new balance for audit trail
- **Transaction types**: DEPOSIT, WITHDRAW, ORDER_PAYMENT, ORDER_REFUND, SYSTEM_ADJUSTMENT

---

### **3. Asset Balances Schema**
**Table**: `users` (same table as users)
**Service**: Order Service
**Design Date**: 2024-08-06

#### **Key Structure**
```
PK: username
SK: ASSET#{asset_id}
```

#### **Data Items**
```
Asset Balance Records:
- PK: "john_doe"
- SK: "ASSET#BTC"
- username: "john_doe"
- asset_id: "BTC"
- quantity: "2.5"
- created_at: "2024-01-01T12:00:00Z"
- updated_at: "2024-01-01T12:00:00Z"

- PK: "john_doe"
- SK: "ASSET#ETH"
- username: "john_doe"
- asset_id: "ETH"
- quantity: "10.0"
- created_at: "2024-01-01T12:00:00Z"
- updated_at: "2024-01-01T12:00:00Z"
```

#### **Query Patterns**
```python
# Get specific asset balance
def get_asset_balance(username: str, asset_id: str):
    return table.get_item(Key={'PK': username, 'SK': f'ASSET#{asset_id}'})

# Get all asset balances for user
def get_all_asset_balances(username: str):
    return table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={':pk': username, ':sk': 'ASSET#'}
    )

# Get all balances for specific asset (admin function)
def get_all_balances_for_asset(asset_id: str):
    return table.query(
        IndexName='AssetIndex',
        KeyConditionExpression='asset_id = :asset_id',
        ExpressionAttributeValues={':asset_id': asset_id}
    )
```

#### **Design Decisions**
- **Why ASSET# prefix**: Distinguishes from other user items, enables efficient queries
- **Same table as users**: Cost efficient, user-centric queries
- **Quantity as string**: Avoid floating point precision issues
- **No market value stored**: Calculated at API level for real-time accuracy

---

### **5. Asset Transactions Schema**
**Table**: `users` (same table as users)
**Service**: Order Service
**Design Date**: 2024-08-06

#### **Key Structure**
```
PK: TRANS#{username}#{asset_id}
SK: timestamp (ISO format)
```

#### **Data Items**
```
Asset Transaction Records:
- PK: "TRANS#john_doe#BTC"
- SK: "2024-01-01T12:00:00Z"
- username: "john_doe"
- asset_id: "BTC"
- transaction_type: "BUY"
- quantity: "1.5"
- price: "50000.00"
- total_amount: "75000.00"
- order_id: "order-123"
- status: "COMPLETED"
- created_at: "2024-01-01T12:00:00Z"

- PK: "TRANS#john_doe#BTC"
- SK: "2024-01-02T12:00:00Z"
- username: "john_doe"
- asset_id: "BTC"
- transaction_type: "SELL"
- quantity: "0.5"
- price: "55000.00"
- total_amount: "27500.00"
- order_id: "order-124"
- status: "COMPLETED"
- created_at: "2024-01-02T12:00:00Z"
```

#### **Query Patterns**
```python
# Get specific transaction
def get_asset_transaction(username: str, asset_id: str, timestamp: str):
    return table.get_item(Key={
        'PK': f'TRANS#{username}#{asset_id}',
        'SK': timestamp
    })

# Get all transactions for user and asset
def get_user_asset_transactions(username: str, asset_id: str, limit: int = 50):
    return table.query(
        KeyConditionExpression='PK = :pk',
        ExpressionAttributeValues={':pk': f'TRANS#{username}#{asset_id}'},
        ScanIndexForward=False,  # Most recent first
        Limit=limit
    )

# Get all transactions for user (requires GSI)
def get_user_transactions(username: str, limit: int = 50):
    return table.query(
        IndexName='UserTransactionsIndex',
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': username},
        ScanIndexForward=False,
        Limit=limit
    )
```

#### **Design Decisions**
- **Why TRANS# prefix**: Distinguishes transaction records, enables efficient queries
- **Timestamp as SK**: Natural ordering, enables time-based queries
- **Composite PK**: Groups transactions by user and asset
- **No GSI initially**: Optimize for common query patterns first

---

### **6. Orders Schema (Planned)**
**Table**: `orders`
**Service**: Order Service
**Design Date**: 2024-08-06 (Planned)

#### **Key Structure**
```
PK: order_id (generated)
SK: ORDER
GSI: UserOrdersIndex (PK: username, SK: ASSET_ID)
```

#### **Data Items**
```
Order Records:
- PK: "order-123"
- SK: "ORDER"
- username: "john_doe"
- asset_id: "BTC"
- order_type: "BUY"
- quantity: "1.5"
- order_price: "50000.00"
- total_amount: "75000.00"
- status: "COMPLETED"
- expires_at: "2024-01-02T12:00:00Z"
- created_at: "2024-01-01T12:00:00Z"
- updated_at: "2024-01-01T12:00:00Z"
- entity_type: "order"
```

#### **Query Patterns**
```python
# Get specific order
def get_order(order_id: str):
    return table.get_item(Key={'PK': order_id, 'SK': 'ORDER'})

# Get all orders for user
def get_orders_by_user(username: str):
    return table.query(
        IndexName='UserOrdersIndex',
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': username},
        ScanIndexForward=False
    )

# Get user orders for specific asset
def get_user_asset_orders(username: str, asset_id: str):
    return table.query(
        IndexName='UserOrdersIndex',
        KeyConditionExpression='username = :username AND asset_id = :asset_id',
        ExpressionAttributeValues={
            ':username': username,
            ':asset_id': asset_id
        },
        ScanIndexForward=False
    )
```

#### **Design Decisions**
- **Separate table**: Orders have different access patterns
- **ORDER as SK**: Distinguishes from potential future order-related items
- **GSI for user queries**: Enables efficient user-specific queries
- **Generated order_id**: Ensures uniqueness, enables direct lookup

---

## 🔍 **Global Secondary Indexes (GSI)**

### **EmailIndex (Implemented)**
```
PK: email
```

**Purpose**: Enable email-based user lookups for login/registration
**Query Patterns**:
- Get user by email (login)
- Check email uniqueness (registration)
- Email-based user search

### **UserOrdersIndex (Planned)**
```
PK: username
SK: ASSET_ID
```

**Purpose**: Enable efficient user-specific order queries
**Query Patterns**:
- Get all orders for a user
- Get user orders for specific asset
- Get user orders by status

### **AssetIndex (Planned)**
```
PK: asset_id
SK: username
```

**Purpose**: Enable asset-specific queries
**Query Patterns**:
- Get all balances for specific asset
- Get all transactions for specific asset

---

## 💰 **Cost Optimization Strategies**

### **Query Efficiency**
- **User-centric design**: 80% of queries are user-specific
- **Efficient key patterns**: Minimize RCU/WCU consumption
- **Selective GSI usage**: Only create GSIs for frequently used patterns

### **Storage Optimization**
- **Single-table design**: Reduces table operations
- **Efficient key design**: Minimize storage overhead
- **String storage**: Avoid floating point precision issues

### **Atomic Operations**
- **Conditional expressions**: Use instead of complex transactions
- **Upsert patterns**: Efficient create/update operations
- **Optimistic locking**: Reduce conflict scenarios

---

## 🧪 **Testing Patterns**

### **Unit Test Patterns**
```python
# Mock DynamoDB responses
mock_item = {
    'PK': 'john_doe',
    'SK': 'ASSET#BTC',
    'username': 'john_doe',
    'asset_id': 'BTC',
    'quantity': '2.5'
}

# Test query patterns
def test_get_asset_balance():
    mock_response = {'Item': mock_item}
    # Test implementation
```

### **Integration Test Patterns**
```python
# Test complete workflows
def test_buy_order_flow():
    # 1. Create order
    # 2. Update balance
    # 3. Create transaction
    # 4. Verify final state
```

---

## 📝 **Design Decision Log**

### **2024-08-06: Asset Management Schema**
- **Decision**: Use single-table design for asset balances and transactions
- **Rationale**: Cost efficient, user-centric queries, consistent with existing patterns
- **Impact**: Reduces table operations, simplifies queries, maintains consistency

### **2024-08-06: Order Schema Planning**
- **Decision**: Separate orders table with GSI for user queries
- **Rationale**: Different access patterns, enables efficient user-specific queries
- **Impact**: Better query performance, more flexible order management

---

*This design documentation captures the actual database schemas, query patterns, and design decisions for the Cloud Native Order Processor system.*