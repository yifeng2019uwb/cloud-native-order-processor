# Limit Order System - Architecture Design Document

**Document Version:** 1.0
**Created:** November 1, 2025
**Status:** Design Phase
**Priority:** High

---

## 📋 Executive Summary

This document outlines the architecture design for implementing a limit order system in the Cloud Native Order Processor platform. The system enables users to create limit buy/sell orders that automatically execute when market prices reach specified thresholds.

**Key Features:**
1. Auto-updating market prices (every 5 minutes from CoinGecko)
2. Limit buy/sell order support with automatic execution
3. Email notifications for all order events

**Design Philosophy:** Efficient, decoupled, scalable architecture using hybrid DynamoDB + Redis with smart caching strategy.

---

## 🎯 Business Requirements

### User Stories

1. **As a trader**, I want prices to update automatically so I don't have to manually refresh
2. **As a trader**, I want to create limit orders that execute when price conditions are met
3. **As a trader**, I want email notifications when my orders execute so I stay informed

### Acceptance Criteria

- Market prices update every 5 minutes from external API
- Limit orders execute within 5-10 seconds of price reaching threshold
- Email notifications sent for all order events (creation, execution, failure)
- System handles 100-1,000+ pending limit orders efficiently
- No code coupling between price fetching and order matching

---

## 🏗️ Architecture Decision: Decoupled Design

### Core Principle

**Loose coupling through shared data contract (Redis state), not direct service calls or events.**

```
┌────────────────────┐         ┌─────────┐         ┌────────────────────┐
│ Inventory Service  │────────→│  Redis  │←────────│  Order Service     │
│ (Price Provider)   │  writes │         │  reads  │  (Price Consumer)  │
└────────────────────┘         └─────────┘         └────────────────────┘
```

**Coupling Type:**
- ✅ **Loose coupling** through shared data contract (Redis keys)
- ❌ **Not zero coupling** (services share Redis data format)
- ✅ **No tight coupling** (no direct service-to-service calls)

**Benefits:**
- ✅ Services are independently deployable
- ✅ Each service owns its implementation
- ✅ Easy to test and deploy separately
- ✅ Can change internal logic without coordination
- ⚠️ Must maintain Redis data contract (price:{asset_id} format)

---

## 💡 Solution Options Evaluated

### Option 1: Event-Driven with Redis Pub/Sub ❌

**Design:**
- Inventory service publishes price change events
- Order service subscribes and reacts to events

**Pros:**
- Instant notification when prices change
- No polling overhead
- Standard event-driven pattern

**Cons:**
- ❌ Tight coupling through event contract
- ❌ If event schema changes, both services must update simultaneously
- ❌ Requires coordination for deployment
- ❌ More complex error handling (missed events)
- ❌ Harder to test independently
- ❌ Service-to-service dependency (publisher must know about subscribers)

**Verdict:** Rejected in favor of looser coupling through shared state

---

### Option 2: Traditional Polling with DynamoDB ❌

**Design:**
- Order service polls DynamoDB every 1-5 minutes
- Queries all pending orders and checks against current price

**Pros:**
- Simple to understand
- No caching layer needed
- Direct database access

**Cons:**
- ❌ Expensive: 1,000+ DynamoDB reads per check
- ❌ Slow: 500ms+ per full scan
- ❌ Doesn't scale: Cost grows with order count
- ❌ High latency: Minutes between checks

**Verdict:** Rejected due to cost and performance issues

---

### Option 3: Full Redis Cache (All Orders) ❌

**Design:**
- Load ALL pending orders into Redis sorted sets
- Check Redis for matches (very fast)

**Pros:**
- Very fast matching (<1ms)
- Simple query logic

**Cons:**
- ❌ High memory usage: 1,000 orders = ~1MB per asset
- ❌ Cache invalidation complexity
- ❌ Need to keep Redis and DynamoDB in sync
- ❌ Memory grows with order volume

**Verdict:** Rejected due to memory inefficiency

---

### Option 4: Decoupled Polling with Smart Redis Cache ✅ **SELECTED**

**Design:**
- Inventory service updates prices in Redis (no coordination)
- Order service polls Redis prices every 5 seconds (no coordination)
- Only cache orders within ±5% of current price (smart range)
- DynamoDB as source of truth, Redis as hot cache

**Pros:**
- ✅ **Loose coupling:** Services communicate through shared data contract only
- ✅ **Independent deployment:** Each service deploys without coordinating with others
- ✅ **Efficient:** 80% less memory, 99% fewer DB queries
- ✅ **Fast:** 5-second reaction time
- ✅ **Scalable:** Cost doesn't grow with order count
- ✅ **Flexible:** Each service owns its implementation
- ✅ **Simple:** No event management, just state polling
- ✅ **Reliable:** No missed events, just direct reads
- ✅ **Testable:** Easy to mock Redis for testing

**Cons:**
- ⚠️ 5-second polling overhead (144 Redis reads/min)
  - Mitigation: Redis handles 100k+ reads/sec, this is 0.0024% usage
- ⚠️ Potential 5-second delay in execution
  - Mitigation: Acceptable for limit orders (not high-frequency trading)

**Verdict:** ✅ **SELECTED** - Best balance of efficiency, simplicity, and decoupling

---

## 🏗️ Detailed Architecture Design

### Component 1: Price Update System

**Service:** Inventory Service
**Responsibility:** Keep market prices fresh
**Decoupling:** Writes to Redis, no knowledge of consumers

**Two-Layer Update Strategy:**

**Layer 1: External API Fetch (Every 5 minutes)**
```
Purpose: Get prices from CoinGecko
Frequency: Every 5 minutes (batch call for all assets)
Cost: 12 API calls/hour (well within free tier)
Storage: DynamoDB inventory table + Redis cache
API: Single batch call for 12 assets
```

**Layer 2: Internal Monitoring (Every 5 seconds)**
```
Purpose: Check if prices changed in our DB
Frequency: Every 5 seconds
Cost: FREE (local Redis reads)
Action: Update Redis price:{asset_id} if changed
No external API calls
```

**Redis Keys Written:**
```
price:BTC = "45000.00"
price:ETH = "3200.50"
price:SOL = "105.25"
```

**Configuration:**
- `COINGECKO_FETCH_INTERVAL` = 300 seconds (5 min)
- `PRICE_MONITOR_INTERVAL` = 5 seconds
- `PRICE_CHANGE_THRESHOLD` = 0.001 (0.1% - optional filtering)

---

### Component 2: Limit Order Matching Engine

**Service:** Order Service
**Responsibility:** Monitor prices, execute limit orders
**Decoupling:** Reads from Redis, no knowledge of price source

**Polling Strategy:**
```
Every 5 seconds:
  1. Read prices from Redis (all tracked assets)
  2. Compare with previous check
  3. If price changed >0.1%:
     - Refresh hot cache from DynamoDB (±5% range)
     - Check for triggered orders
     - Execute matches
```

**Smart Cache Management (±5% Range):**
```
Current price: $45,000
Cache range: $42,750 - $47,250 (±5%)

Load from DynamoDB:
  - BUY orders with limit_price: $45,000 - $47,250
  - SELL orders with limit_price: $42,750 - $45,000

Store in Redis:
  - hot_orders:BTC:BUY (sorted set)
  - hot_orders:BTC:SELL (sorted set)

Cache metadata:
  - cache_meta:BTC (min/max/center prices)
```

**Configuration:**
- `PRICE_CHECK_INTERVAL` = 5 seconds
- `CACHE_RANGE_PERCENT` = 0.05 (±5%)
- `CACHE_REFRESH_THRESHOLD` = 0.02 (refresh if price moves >2%)
- `SAFETY_SCAN_INTERVAL` = 1800 seconds (30 min backup)

---

### Component 3: Email Notification System

**Service:** Common package (shared utility)
**Responsibility:** Send emails for order events
**Decoupling:** Called by any service, no business logic

**Integration:** AWS SES (Simple Email Service)

**Email Events:**
- Order created (market or limit)
- Limit order triggered
- Order executed successfully
- Order execution failed
- Order cancelled
- Order expired

---

## 📊 Data Architecture

### DynamoDB Schema Updates

**Current Structure:**
```
Primary Key:
  Pk = order_id
  Sk = "ORDER"

GSI-1 (UserOrdersIndex):
  GSI-PK = username
  GSI-SK = asset_id
```

**New Structure (Added):**

**New Fields in Order Entity:**
- `limit_price`: Decimal (required for limit orders)
- `side`: String ("BUY" or "SELL")
- `triggered_at`: DateTime (when condition met)
- `execution_price`: Decimal (actual execution price)
- `expires_at`: DateTime (optional, default 30 days)
- `held_amount`: Decimal (amount of balance/assets held for this order)

**New Fields in Balance Entity:**
- `held_balance`: Decimal (funds reserved for pending limit orders)
- Existing: `available_balance` (funds available for trading)

**New GSI-2 (PendingLimitBuyOrders):**
```
GSI-2-PK: asset_id + "#LIMIT_BUY" (e.g., "BTC#LIMIT_BUY")
GSI-2-SK: limit_price (numeric, for sorting)
Projection: ALL
Purpose: Efficiently query BUY limit orders by price range
```

**New GSI-3 (PendingLimitSellOrders):**
```
GSI-3-PK: asset_id + "#LIMIT_SELL" (e.g., "BTC#LIMIT_SELL")
GSI-3-SK: limit_price (numeric, for sorting)
Projection: ALL
Purpose: Efficiently query SELL limit orders by price range
```

**Why two GSIs:**
- Better partitioning (BUY and SELL separated)
- No filter expressions needed (more efficient)
- Cleaner query logic
- Better DynamoDB performance

---

### Redis Data Structures

**1. Current Prices (Inventory Service writes, Order Service reads):**
```
Key: price:{asset_id}
Type: String
Value: Decimal string
TTL: 600 seconds (10 min, ensures freshness)
Example: price:BTC = "45000.00"
```

**2. Hot Cache - BUY Orders (Order Service manages):**
```
Key: hot_orders:{asset_id}:BUY
Type: Sorted Set
Members: order_id
Scores: limit_price
Example: ZADD hot_orders:BTC:BUY 45000 order123
```

**3. Hot Cache - SELL Orders (Order Service manages):**
```
Key: hot_orders:{asset_id}:SELL
Type: Sorted Set
Members: order_id
Scores: limit_price
Example: ZADD hot_orders:BTC:SELL 46000 order999
```

**4. Cache Metadata (Order Service manages):**
```
Key: cache_meta:{asset_id}
Type: Hash
Fields: min_price, max_price, center_price, updated_at
Purpose: Track cached price range to know when refresh needed
TTL: 1800 seconds (30 min)
```

**5. Execution Locks (Order Service manages):**
```
Key: lock:order:{order_id}
Type: String
Value: "1"
TTL: 30 seconds
Purpose: Prevent duplicate execution
```

---

## ⚡ Smart Caching Strategy: ±5% Range

### Problem Statement

**Challenge:** How to efficiently match 1,000+ pending limit orders against live prices?

**Naive approach:** Load all orders into memory
- Memory: 1,000 orders × 1KB = 1MB per asset
- For 12 assets: 12MB
- Scales poorly

### Solution: Range-Based Caching

**Key Insight:** Most limit orders are FAR from current price
- Current BTC: $45,000
- Order at $30,000: Won't trigger for days/weeks
- Order at $60,000: Won't trigger for days/weeks
- **Only orders near current price matter!**

**Implementation:**
```
Current price: $45,000
Cache range: ±5%
  Min: $42,750 (-5%)
  Max: $47,250 (+5%)

Load into Redis:
  - BUY orders: $45,000 - $47,250 (will trigger if price rises)
  - SELL orders: $42,750 - $45,000 (will trigger if price drops)

Ignore:
  - Orders outside this range (stay in DynamoDB only)
```

**Benefits:**
- Cache only ~10-20% of orders (huge memory saving)
- Only query DynamoDB when price moves >5%
- Fast matching (all relevant orders in memory)

### Cache Refresh Logic

**When to refresh:**
1. Price moves outside cached range (e.g., >5% move)
2. Cache expired (30-min safety refresh)
3. First time loading (cache empty)

**When NOT to refresh:**
- Price moves within cached range (most of the time)
- Just added new order (add directly to cache)
- Order cancelled (remove directly from cache)

**Result:** 99%+ reduction in DynamoDB queries

---

## 🔄 Complete System Workflow

### Workflow 1: Price Updates (Inventory Service)

**Every 5 minutes:**
1. Fetch all asset prices from CoinGecko (1 batch API call)
2. For each asset:
   - Save to DynamoDB inventory table
   - Update Redis: `price:{asset_id} = new_price`
3. Done (no events, no coordination)

**Decoupling benefit:** Can change to 1-min, 30-sec, or real-time without affecting order service

---

### Workflow 2: Price Monitoring (Order Service)

**Every 5 seconds:**
1. Read all price keys from Redis
2. Compare with last checked prices
3. For each asset with meaningful change (>0.1%):
   - Check if cache refresh needed
   - If price moved >5% from cache center: Refresh cache
   - Otherwise: Just check existing cache
4. Store current prices for next comparison

**Decoupling benefit:** Can change check frequency, thresholds, or logic without affecting inventory service

---

### Workflow 3: Cache Management (Order Service)

**When price moves >5% from cached center:**

1. Calculate new ±5% range around current price

2. Query DynamoDB GSI-2 for BUY orders in range:
   ```
   # For BUY orders (trigger when price >= limit)
   query(
     pk = "BTC#LIMIT_BUY",
     sk <= current_price
   )
   Returns: All BUY orders where limit_price <= current_price
   Range optimization: sk BETWEEN (current_price * 0.95) AND current_price
   ```

3. Query DynamoDB GSI-3 for SELL orders in range:
   ```
   # For SELL orders (trigger when price <= limit)
   query(
     pk = "BTC#LIMIT_SELL",
     sk >= current_price
   )
   Returns: All SELL orders where limit_price >= current_price
   Range optimization: sk BETWEEN current_price AND (current_price * 1.05)
   ```

4. Clear old cache, load new orders
5. Store cache metadata (range, timestamp)

**Frequency:** Only when price moves significantly (~12 times/day typically)

---

### Workflow 4: Order Matching (Order Service)

**After cache refresh or price change:**

1. Check BUY order triggers (trigger when price >= limit):
   ```
   Query Redis: ZRANGEBYSCORE hot_orders:BTC:BUY -inf current_price
   Returns: All BUY orders with limit_price <= current_price
   Logic: Market price reached or exceeded the limit, execute the buy
   ```

2. Check SELL order triggers (trigger when price <= limit):
   ```
   Query Redis: ZRANGEBYSCORE hot_orders:BTC:SELL current_price +inf
   Returns: All SELL orders with limit_price >= current_price
   Logic: Market price reached or dropped below the limit, execute the sell
   ```

3. For each triggered order:
   - Acquire distributed lock (prevent duplicate execution)
   - Verify order still pending in DynamoDB
   - Execute order

**Performance:** Redis queries complete in <1ms

---

### Workflow 5: Balance Management (Critical for Limit Orders)

**Challenge:** How to reserve funds for pending limit orders?

**Solution:** Held balance system (already exists in balance entity)

#### When User Creates Limit Order:

1. **Validate Sufficient Balance:**
   - Check user has enough available_balance
   - For BUY order: Need (quantity × limit_price) in USD
   - For SELL order: Need quantity of asset

2. **Reserve Funds:**
   - Deduct from `available_balance`
   - Add to `held_balance`
   - Store `held_amount` in order record

3. **Example:**
   ```
   Before: available_balance = $50,000, held_balance = $0
   Create: BUY 0.5 BTC @ $45,000 limit
   Hold: $22,500
   After: available_balance = $27,500, held_balance = $22,500
   ```

#### When Order Executes:

1. **Convert Held Balance:**
   - Deduct from `held_balance`
   - Add assets to user portfolio
   - No additional balance check needed (already reserved)

2. **Example:**
   ```
   Before: held_balance = $22,500
   Execute: 0.5 BTC @ $45,000 market price
   After: held_balance = $0, user has 0.5 BTC
   ```

#### When Order Cancelled or Expires:

1. **Return Held Balance:**
   - Move from `held_balance` → `available_balance`
   - Update order status to CANCELLED/EXPIRED
   - Send email notification

2. **Example:**
   ```
   Before: available = $27,500, held = $22,500
   Cancel: Return held funds
   After: available = $50,000, held = $0
   ```

#### Partial Fill Handling (Future):

**Current:** All-or-nothing execution
- Execute full quantity or nothing
- Simple, no partial balance releases

**Future Enhancement:**
- Execute partial quantity if available
- Release proportional held_balance
- Update order with partial fill status

**Verdict:** Start with all-or-nothing, add partial fills in Phase 2 if needed

---

### Workflow 6: Complete Example - BUY Limit Order

**Scenario:** User wants to buy BTC when price drops to $45,000

#### Initial State:
```
User balance:
  - available_balance: $50,000
  - held_balance: $0

Market:
  - BTC current price: $47,000
```

#### Step 1: User Creates Limit Order

**Request:**
```
POST /api/v1/orders
{
  "order_type": "LIMIT_BUY",
  "asset_id": "BTC",
  "quantity": 0.5,
  "limit_price": 45000
}
```

**Order Service Actions:**
1. Validate: User has $50,000 available (need $22,500)
2. Reserve funds:
   - Deduct $22,500 from available_balance
   - Add $22,500 to held_balance
3. Create order in DynamoDB:
   - order_id: order_123
   - status: PENDING
   - limit_price: $45,000
   - held_amount: $22,500
4. Add to GSI: `BTC#LIMIT_BUY` with SK=$45,000
5. Send email: "Limit order created: BUY 0.5 BTC @ $45,000"

**New State:**
```
User balance:
  - available_balance: $27,500
  - held_balance: $22,500 (reserved for order_123)

Order:
  - order_123: PENDING, limit=$45,000, held=$22,500
```

---

#### Step 2: Price Updates (Inventory Service Background Task)

**Every 5 minutes:**
```
T=0min:  Fetch CoinGecko → BTC = $47,000
         Update Redis: price:BTC = "47000.00"
         Update DynamoDB inventory table

T=5min:  Fetch CoinGecko → BTC = $46,000
         Update Redis: price:BTC = "46000.00"

T=10min: Fetch CoinGecko → BTC = $45,000
         Update Redis: price:BTC = "45000.00"  ← Target reached!
```

**No coordination with order service!**

---

#### Step 3: Price Monitoring (Order Service Background Task)

**Every 5 seconds:**
```
T=10:00 - Read Redis: price:BTC = "46000.00"
          No change from last check

T=10:05 - Read Redis: price:BTC = "45000.00"
          Changed! $46k → $45k (2.2% drop)

T=10:05 - Check if cache refresh needed:
          Current cache range: $44,650 - $49,350 (±5% of $47k)
          New price: $45,000 (still in range)
          Decision: No refresh needed, just check cache

T=10:05 - Query Redis hot cache:
          ZRANGEBYSCORE hot_orders:BTC:BUY -inf 45000
          Returns: order_123 (limit_price=$45,000)

T=10:05 - Match found! Trigger execution
```

**Reaction time: 5 seconds from price update to detection**

---

#### Step 4: Order Execution

**Execution Steps:**

1. **Acquire Lock:**
   ```
   Redis: SET lock:order:order_123 1 NX EX 30
   Lock acquired: Proceed
   ```

2. **Verify Order State:**
   ```
   DynamoDB: Get order_123
   Status: PENDING ✅
   Held amount: $22,500 ✅
   ```

3. **Execute at Market Price:**
   ```
   Current market price: $45,000
   Quantity: 0.5 BTC
   Cost: $22,500

   Actions:
   - Deduct $22,500 from held_balance
   - Add 0.5 BTC to user asset_balance
   - Create transaction record
   ```

4. **Update Order:**
   ```
   DynamoDB: Update order_123
   - status: PENDING → EXECUTED
   - triggered_at: 2025-11-01T10:10:05Z
   - execution_price: $45,000
   - updated_at: 2025-11-01T10:10:05Z
   ```

5. **Clean Up Cache:**
   ```
   Redis: ZREM hot_orders:BTC:BUY order_123
   Redis: DEL order:order_123
   ```

6. **Send Email:**
   ```
   To: user@example.com
   Subject: "Limit Order Executed: BUY 0.5 BTC"
   Body:
     Your limit order has been executed!
     - Asset: BTC
     - Quantity: 0.5
     - Limit Price: $45,000
     - Execution Price: $45,000
     - Total: $22,500
     - Time: 2025-11-01 10:10:05 UTC
   ```

7. **Release Lock:**
   ```
   Redis: DEL lock:order:order_123
   ```

**Total execution time: ~500ms**

---

#### Final State:
```
User balance:
  - available_balance: $27,500
  - held_balance: $0 (released)

User assets:
  - BTC: 0.5

Order:
  - order_123: EXECUTED
  - execution_price: $45,000
  - triggered_at: 2025-11-01T10:10:05Z
```

#### Timeline Diagram:
```
┌─────────────────────────────────────────────────────────────────┐
│ Timeline: From Order Creation to Execution                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ T=0:00   User creates limit order                              │
│          └→ Balance held: $22,500                              │
│          └→ Order saved: PENDING                               │
│          └→ Email sent: "Order created"                        │
│                                                                 │
│ T=0:00   ┌──────────────────────────────────────────────┐     │
│   to     │ Inventory Service (independent loop)         │     │
│ T=10:00  │ • Fetches prices every 5 min                 │     │
│          │ • Updates Redis price:BTC                    │     │
│          │ • Updates DynamoDB inventory                 │     │
│          └──────────────────────────────────────────────┘     │
│                                                                 │
│          ┌──────────────────────────────────────────────┐     │
│          │ Order Service (independent loop)             │     │
│          │ • Checks Redis prices every 5 sec            │     │
│          │ • Compares with last check                   │     │
│          │ • Waits for price to reach $45,000...        │     │
│          └──────────────────────────────────────────────┘     │
│                                                                 │
│ T=10:00  Inventory fetches: BTC = $45,000                     │
│          └→ Updates Redis: price:BTC = "45000.00"             │
│                                                                 │
│ T=10:05  Order service checks Redis                            │
│          └→ Detects change: $46k → $45k                        │
│          └→ Queries hot cache                                  │
│          └→ Finds: order_123 matches!                          │
│          └→ Executes order                                     │
│          └→ Held balance → BTC assets                          │
│          └→ Email sent: "Order executed!"                      │
│                                                                 │
│ T=10:06  COMPLETE                                              │
│          └→ User has: 0.5 BTC                                  │
│          └→ Balance: $27,500 available, $0 held                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Total time from condition met to execution: 5 seconds
Total time from order creation to execution: 10 minutes (depends on market)
```

---

### Workflow 7: Email Notifications (All Services)

**Email Events:**

| Event | Trigger | Template |
|-------|---------|----------|
| Limit order created | POST /orders (limit type) | "Limit Order Created: BUY 0.5 BTC @ $45,000" |
| Market order executed | POST /orders (market type) | "Order Executed: BUY 0.5 BTC @ $45,500" |
| Limit order triggered | Matcher finds match | "Limit Order Executed: BUY 0.5 BTC @ $45,500" |
| Order failed | Execution error | "Order Failed: Insufficient balance" |
| Order cancelled | DELETE /orders/:id | "Order Cancelled: BUY 0.5 BTC @ $45,000" |

**Service:** AWS SES (Simple Email Service)
**Cost:** FREE (62,000 emails/month free tier)
**Integration:** Common package email utility

---

## 📊 Efficiency Analysis

### Memory Efficiency

**Scenario:** 1,000 pending BTC orders across $30k-$60k range

| Approach | Orders Cached | Memory Usage | Efficiency |
|----------|---------------|--------------|------------|
| Full cache | 1,000 | 1 MB | Baseline |
| ±10% range | 333 | 333 KB | 3x better |
| **±5% range** | **167** | **167 KB** | **6x better ✅** |
| ±2% range | 67 | 67 KB | 15x better (maybe too narrow) |

**Selected:** ±5% range - Good balance of memory efficiency and coverage

---

### Query Efficiency

**Comparison over 24 hours:**

| Approach | DynamoDB Queries | Redis Reads | Cost |
|----------|-----------------|-------------|------|
| Polling every 1 min | 1,440 | 0 | $$ High |
| Polling every 5 min | 288 | 0 | $ Medium |
| Event-driven (Pub/Sub) | 144* | 17,280 | $ Low |
| **Decoupled polling + ±5% cache** | **12-24** | **17,280** | **¢ Very Low ✅** |

*Only when prices change

**Selected approach:** 99%+ fewer DynamoDB queries vs traditional polling

---

### Scalability Analysis

**Does performance degrade as orders increase?**

| Total Orders | Cached Orders | DB Queries/Day | Redis Reads/Day | Scales? |
|--------------|---------------|----------------|-----------------|---------|
| 100 | 20 | 12 | 17,280 | ✅ |
| 1,000 | 150 | 12 | 17,280 | ✅ |
| 10,000 | 1,500 | 12 | 17,280 | ✅ |
| 100,000 | 15,000 | 12 | 17,280 | ✅ |

**Key insight:** Query count is independent of order volume!
**Scalability:** Linear memory growth, constant query cost ✅

---

## 🎯 Design Decisions & Rationale

### Decision 1: Two Separate GSIs (BUY/SELL)

**Alternative:** Single GSI with status + side filtering

**Why two GSIs:**
- ✅ Better DynamoDB partitioning (split load across partitions)
- ✅ No filter expressions needed (lower read cost)
- ✅ Cleaner query logic
- ✅ Better performance at scale

**Trade-off:** Two GSIs vs one (minimal cost difference in pay-per-request mode)

**Verdict:** Two GSIs provide better performance and clearer semantics

---

### Decision 2: Decoupled Polling vs Event-Driven

**Why decoupling:**
- ✅ Services can evolve independently
- ✅ No deployment coordination needed
- ✅ Easier testing (mock Redis, not events)
- ✅ Simpler error handling
- ✅ Can change inventory fetch logic without touching order service

**Trade-off:** 144 Redis reads/min vs event-based wake-up

**Verdict:** Decoupling worth the minimal polling cost

---

### Decision 3: ±5% Cache Range

**Alternatives evaluated:**

| Range | Orders Cached | Refresh Frequency | Memory | Queries |
|-------|---------------|-------------------|--------|---------|
| ±1% | 33 | Very high | Very low | High |
| ±2% | 67 | High | Low | Medium |
| **±5%** | **167** | **Low** | **Medium** | **Low ✅** |
| ±10% | 333 | Very low | High | Very low |
| All | 1,000 | Never | Very high | None |

**Why ±5%:**
- ✅ Catches most realistic price movements (crypto typically <5%/hour)
- ✅ Good memory efficiency (cache only ~15-20% of orders)
- ✅ Minimal cache refreshes (only on >5% moves)
- ✅ Fast enough for limit orders (not HFT)

**Verdict:** ±5% is the sweet spot

---

### Decision 4: 5-Second Check Interval

**Alternatives:**

| Interval | Reaction Time | Redis Reads/Day | User Experience |
|----------|---------------|-----------------|-----------------|
| 1 second | Best | 86,400 | Excellent |
| **5 seconds** | **Excellent** | **17,280** | **Very good ✅** |
| 10 seconds | Good | 8,640 | Good |
| 30 seconds | Acceptable | 2,880 | Acceptable |
| 60 seconds | Poor | 1,440 | Poor for trading |

**Why 5 seconds:**
- ✅ Fast enough for trading platform (not HFT)
- ✅ Minimal Redis overhead (0.0024% of capacity)
- ✅ Sub-10-second order execution
- ✅ Good user experience

**Verdict:** 5 seconds balances speed and efficiency

---

### Decision 5: Execute at Market Price (Not Limit Price)

**User sets:** BUY limit at $45,000
**Price reaches:** $45,000
**We execute at:** $45,000 (current market price)

**Why market price:**
- User wants to buy at $45k or better
- If market is at $45k when triggered, that's the fair price
- Matches real exchange behavior
- Simpler implementation (reuse market order logic)

**Edge case:** Price moves during execution
- Add 1% slippage tolerance
- If market moves to $45,450 (>1% higher), cancel order
- Protects user from unexpected execution price

**Verdict:** Market price execution with slippage protection

---

## 🚨 Edge Cases & Solutions

### Edge Case 1: Multiple Orders Trigger Simultaneously

**Problem:** 10 orders trigger when BTC hits $45,000

**Solution:**
- Process in FIFO order (DynamoDB insertion order)
- Distributed locks prevent duplicate execution
- Each order gets fair execution

**Expected:** Rare (most orders at different prices)

---

### Edge Case 2: Insufficient Balance/Assets

**Problem:** BUY order triggers but user spent money elsewhere

**Solution:**
- Check balance/assets before execution (already do this)
- If insufficient: Mark order as FAILED
- Send email: "Order failed - insufficient balance"
- User can cancel or wait for balance

**Expected:** Uncommon (funds reserved on creation - future enhancement)

---

### Edge Case 3: Price Gaps (Jumps Over Limit)

**Problem:** Price jumps $44k → $46k, skipping $45k limit

**Solution:**
- Order at $45k still executes at $46k
- User wanted $45k or better
- Getting $46k is worse but still valuable
- Standard limit order behavior

**Alternative:** Add "max acceptable price" field
- User sets: Limit $45k, max acceptable $46k
- Cancel if execution would be >$46k
- More complex, defer to Phase 2

**Verdict:** Execute at current price, add max price later if needed

---

### Edge Case 4: Stale Prices

**Problem:** CoinGecko fetch fails, prices stop updating

**Solution:**
- Redis keys have 10-min TTL
- If price key expires: Order service knows data is stale
- Stop executing limit orders until fresh data
- Log warning, send admin alert

**Expected:** Very rare (CoinGecko uptime >99.9%)

---

### Edge Case 5: Service Restart

**Problem:** Order service restarts, loses in-memory state

**Solution:**
- On startup: Rebuild hot cache from DynamoDB
- Subscribe to price updates
- Resume normal operation
- No orders lost (source of truth is DynamoDB)

**Downtime:** <30 seconds to rebuild cache and resume

---

## 💰 Cost Analysis

### Infrastructure Costs

| Component | Service | Monthly Cost |
|-----------|---------|--------------|
| Price fetching | CoinGecko Free API | **$0** |
| Redis | Existing container | **$0** (already running) |
| DynamoDB reads | Pay-per-request | **~$0.25** (minimal reads) |
| DynamoDB storage | Pay-per-GB | **~$0.25** (order data) |
| Email notifications | AWS SES Free tier | **$0** (under 62k/month) |
| **TOTAL** | | **~$0.50/month** |

**Scaling costs:**
- 100 orders: $0.50/month
- 1,000 orders: $0.75/month
- 10,000 orders: $2.00/month

**Essentially free for personal project!**

---

### API Usage

**CoinGecko Free Tier:** 10-50 calls/minute

**Our usage:**
- 1 batch call every 5 minutes
- 12 calls/hour
- 288 calls/day
- **Well within limits!**

**No paid API needed!**

---

## ⏱️ Implementation Timeline

### Phase 1: Foundation (4-5 hours)
**Goal:** Auto price updates + email service

**Components:**
- Inventory service background task (price fetcher)
- Redis price caching
- Email service setup (AWS SES)
- Email templates

**Deliverable:** Prices update automatically, emails working

---

### Phase 2: Database Schema (2-3 hours)
**Goal:** Support limit orders in database

**Components:**
- Add new GSIs to Terraform (PendingLimitBuyOrders, PendingLimitSellOrders)
- Add new fields to Order entity
- Update order creation logic
- Deploy Terraform changes

**Deliverable:** Can create limit orders, stored in DynamoDB

---

### Phase 3: Limit Order Engine (8-10 hours)
**Goal:** Automatic limit order execution

**Components:**
- Order service price monitor (5-sec polling)
- Smart cache manager (±5% range logic)
- Order matcher (Redis sorted set queries)
- Order executor (with locks and slippage protection)
- Email integration for all order events
- Safety scanner (30-min backup)

**Deliverable:** Complete limit order system working end-to-end

---

### Total Estimated Time: 14-18 hours
**Breakdown:**
- Design & planning: Already done ✅
- Implementation: 14-18 hours
- Testing: Included in each phase
- Deployment: Minimal (use existing infrastructure)

---

## 🎯 Success Metrics

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Price update frequency | 5 minutes | Balance API usage vs freshness |
| Limit order reaction time | 5-10 seconds | Fast enough for limit orders |
| Cache hit rate | >95% | Most checks don't need DB query |
| DynamoDB queries | <50/day per asset | Cost efficiency |
| Email delivery rate | >99% | Reliable notifications |

### Scalability Targets

| Scale | Orders | Cached | Memory | Queries/Day |
|-------|--------|--------|--------|-------------|
| Initial | 100 | 20 | 50 KB | 24 |
| Growth | 1,000 | 150 | 200 KB | 24 |
| Large | 10,000 | 1,500 | 2 MB | 24 |

**Target:** System performs equally well from 100 to 10,000 orders

---

## 🔒 Reliability & Safety

### Distributed Locks

**Purpose:** Prevent duplicate order execution

**Implementation:** Redis `SET NX EX`
- Atomic operation (no race conditions)
- 30-second timeout (auto-release if crash)
- Per-order locking (fine-grained)

### Safety Scanner

**Purpose:** Catch any missed orders (backup mechanism)

**Implementation:**
- Runs every 30 minutes
- Queries DynamoDB for all pending orders
- Checks against current prices
- Catches orders if:
  - Cache refresh failed
  - Price check failed
  - Redis was down temporarily

**Guarantee:** Every order checked at least every 30 minutes

### Order Expiration

**Default:** 30 days
- User can set custom expiration
- Auto-cancel after expiration
- Email notification sent

**Rationale:** Prevents stale orders from executing unexpectedly

---

## 🚀 Future Enhancements (Out of Scope)

### Phase 2 Features (Possible Later)

1. **Stop-Loss Orders:** Sell when price drops below threshold
2. **Trailing Stop Orders:** Dynamic threshold that follows price
3. **Partial Fills:** Execute portion of order if full quantity unavailable
4. **OCO Orders:** One-Cancels-Other (linked orders)
5. **Time-in-Force:** FOK (Fill-or-Kill), IOC (Immediate-or-Cancel)
6. **Price Alerts:** Notify without executing
7. **Order Modification:** Change limit price without cancelling
8. **Real-time WebSocket:** Sub-second price updates

**Decision:** Start with MVP, add complexity based on user feedback

---

## 🎯 Technical Constraints & Assumptions

### Constraints

1. **CoinGecko Free Tier:** 10-50 calls/minute maximum
2. **Personal Project Scale:** Optimize for 100-1,000 orders, not millions
3. **Existing Infrastructure:** Must use current Redis, DynamoDB, AWS setup
4. **No New Services:** Work within existing microservices
5. **Development Time:** 14-18 hours total

### Assumptions

1. **User Behavior:** Most users have 1-10 active limit orders
2. **Price Volatility:** Crypto prices change meaningfully every 5-30 minutes
3. **Order Distribution:** Orders spread across price ranges (not clustered)
4. **Execution Speed:** 5-10 second delay is acceptable
5. **Email Volume:** <100 emails per user per month

---

## ✅ Design Approval Checklist

### Architecture
- ✅ Loosely coupled services (shared data contract, no direct calls)
- ✅ Independently deployable services
- ✅ Uses existing infrastructure (no new containers)
- ✅ Scalable design (handles 100-10,000 orders)
- ✅ Cost-efficient (essentially free)

### Performance
- ✅ Fast price updates (5-second checks)
- ✅ Efficient caching (±5% range)
- ✅ Minimal database queries (<50/day)
- ✅ Quick order execution (<10 seconds)

### Reliability
- ✅ Distributed locks (prevent duplicates)
- ✅ Safety scanner (backup mechanism)
- ✅ Source of truth in DynamoDB
- ✅ Graceful degradation if Redis down

### User Experience
- ✅ Email notifications (all events)
- ✅ Fast execution (sub-10 seconds)
- ✅ Predictable behavior (market price execution)
- ✅ Order cancellation support

---

## 📋 Next Steps

1. **Design Review:** Review and approve this document
2. **Create Implementation Tasks:** Break down into BACKLOG tasks
3. **Terraform Updates:** Add new GSIs to DynamoDB
4. **Phase 1 Implementation:** Price updates + email service
5. **Phase 2 Implementation:** Database schema updates
6. **Phase 3 Implementation:** Limit order matching engine
7. **Testing:** Integration tests for all scenarios
8. **Documentation:** Update API docs and user guides

---

## 📚 References

- **DynamoDB GSI Best Practices:** AWS Documentation
- **Redis Sorted Sets:** Redis Documentation
- **CoinGecko API Limits:** https://www.coingecko.com/en/api/pricing
- **AWS SES Free Tier:** AWS Documentation
- **Existing System Docs:**
  - `/docs/design-docs/centralized-authentication-architecture.md`
  - `/docs/design-docs/monitoring-design.md`

---

**Document Status:** ✅ Ready for Review
**Next Action:** Create BACKLOG tasks for implementation
