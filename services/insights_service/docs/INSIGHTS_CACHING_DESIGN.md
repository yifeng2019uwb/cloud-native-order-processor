# Insights Caching Design Discussion

## 🎯 Requirements

1. **Cache Gemini API results** to avoid redundant API calls
2. **24-hour validity**: Return cached result if retrieved within 24 hours AND portfolio hasn't changed
3. **Portfolio change detection**: Automatically detect when user's portfolio changes
4. **Persistent storage**: Store in database (not just Redis) for durability

---

## 📊 Design Options Analysis

### Option 1: DynamoDB Only (Recommended)

**Storage Location**: DynamoDB `users` table (following single-table design pattern)

**Schema Design**:
```
PK: username
SK: INSIGHTS#{portfolio_hash}
Attributes:
  - summary: str (Gemini-generated insights)
  - generated_at: datetime (when insights were generated)
  - model: str (e.g., "gemini-flash-latest")
  - portfolio_hash: str (hash of portfolio data for change detection)
  - ttl: int (DynamoDB TTL - auto-delete after expiration)
```

**Portfolio Hash Components**:
- `total_portfolio_value`
- `usd_balance`
- Top 10 holdings (asset_id, quantity, allocation_pct)
- Last 10 orders (asset_id, order_type, quantity, created_at)

**Query Pattern**:
1. Generate current portfolio hash
2. Query: `PK=username AND SK=INSIGHTS#{portfolio_hash}`
3. If found AND `generated_at` < 24 hours → return cached
4. If not found OR expired → call Gemini API → save new record

**Pros**:
- ✅ Persistent (survives Redis restarts)
- ✅ Follows existing single-table design pattern
- ✅ DynamoDB TTL can auto-cleanup old records
- ✅ Can query historical insights if needed
- ✅ No additional infrastructure

**Cons**:
- ⚠️ Slightly slower than Redis (but acceptable for this use case)
- ⚠️ Need to manage TTL manually or use DynamoDB TTL feature

---

### Option 2: Redis Only

**Storage Location**: Redis

**Key Format**: `insights:portfolio:{username}:{portfolio_hash}`

**Value**: JSON with `summary`, `generated_at`, `model`

**TTL**: 24 hours (3600 seconds)

**Pros**:
- ✅ Very fast (in-memory)
- ✅ Simple implementation
- ✅ Built-in TTL

**Cons**:
- ❌ Not persistent (lost on Redis restart)
- ❌ No historical data
- ❌ Additional infrastructure dependency

---

### Option 3: Hybrid (Redis + DynamoDB)

**Storage**: 
- Redis: Hot cache (fast access)
- DynamoDB: Persistent backup (durability)

**Flow**:
1. Check Redis first (fast path)
2. If miss, check DynamoDB
3. If miss, call Gemini API
4. Save to both Redis and DynamoDB

**Pros**:
- ✅ Fast (Redis) + Persistent (DynamoDB)
- ✅ Best of both worlds

**Cons**:
- ❌ More complex (two writes, two reads)
- ❌ Higher cost
- ❌ Potential inconsistency between Redis and DynamoDB

---

## 🏗️ Recommended Design: DynamoDB Only

### Schema Details

**Table**: `users` (existing table, following single-table pattern)

**Item Structure**:
```python
{
    "PK": "load_test_user_1",
    "SK": "INSIGHTS#a1b2c3d4e5f6g7h8",  # portfolio hash
    "summary": "Your portfolio is heavily concentrated in...",
    "generated_at": "2026-02-06T19:00:00Z",
    "model": "gemini-flash-latest",
    "portfolio_hash": "a1b2c3d4e5f6g7h8",
    "ttl": 1736208000  # Unix timestamp for DynamoDB TTL (24 hours)
}
```

**GSI Consideration**: 
- Not needed - we query by PK+SK (exact match)
- Each user has one active insights record per portfolio state

---

## 🔄 Portfolio Change Detection

### Hash Generation Strategy

**Components to include**:
1. **Total portfolio value** (changes when prices change or trades occur)
2. **USD balance** (changes on deposit/withdraw)
3. **Holdings** (top 10 by value):
   - asset_id
   - quantity
   - allocation_pct
4. **Recent orders** (last 10):
   - asset_id
   - order_type
   - quantity
   - created_at timestamp

**Hash Algorithm**: SHA256 of sorted JSON representation

**Why this works**:
- ✅ Detects balance changes (deposit/withdraw)
- ✅ Detects new orders
- ✅ Detects holdings changes (buy/sell)
- ✅ Detects significant price movements (affects allocation_pct)
- ⚠️ Note: Price-only changes (without trades) will trigger new insights

---

## ⏰ 24-Hour Validity Logic

### Flow Diagram

```
1. User requests insights
   ↓
2. Aggregate current portfolio data
   ↓
3. Generate portfolio hash
   ↓
4. Query DynamoDB: PK=username, SK=INSIGHTS#{hash}
   ↓
5. If found:
   ├─ Check generated_at timestamp
   │  ├─ If < 24 hours ago → Return cached result ✅
   │  └─ If >= 24 hours ago → Continue to step 6
   └─ If not found → Continue to step 6
   ↓
6. Call Gemini API
   ↓
7. Save to DynamoDB:
   - PK: username
   - SK: INSIGHTS#{hash}
   - summary, generated_at, model, portfolio_hash
   - ttl: now + 24 hours
   ↓
8. Return new insights
```

### Edge Cases

1. **Portfolio changes within 24 hours**:
   - Hash changes → SK changes → Cache miss → New API call ✅

2. **No changes for 25 hours**:
   - Hash same, but timestamp > 24h → New API call ✅

3. **Multiple portfolio states**:
   - Each portfolio state gets its own SK (different hash)
   - Old states auto-expire via TTL
   - User can have multiple cached insights for different portfolio states

---

## 💰 Cost Analysis

### DynamoDB Costs (Pay-per-request)

**Read Operations**:
- 1 read per insights request (if cache hit)
- Cost: ~$0.25 per million reads

**Write Operations**:
- 1 write per new insights generation
- Cost: ~$1.25 per million writes

**Storage**:
- ~500 bytes per insights record
- Cost: ~$0.25 per GB/month

**Example**: 1000 users, each requesting insights 10x/day
- Cache hit rate: 80% (assuming portfolio changes ~2x/day)
- Reads: 1000 × 10 × 0.8 = 8,000/day = ~240k/month
- Writes: 1000 × 10 × 0.2 = 2,000/day = ~60k/month
- **Monthly cost**: ~$0.06 (reads) + $0.08 (writes) = **~$0.14/month**

**Very cost-effective!**

---

## 🚀 Performance Considerations

### Query Performance

**DynamoDB Query**:
- PK + SK lookup: ~1-5ms (very fast)
- Single item retrieval (no scan needed)

**Comparison**:
- Redis: ~0.1-1ms (faster, but not persistent)
- DynamoDB: ~1-5ms (fast enough, persistent)

**Conclusion**: DynamoDB performance is acceptable for this use case.

---

## 🔧 Implementation Considerations

### 1. Portfolio Hash Stability

**Question**: Should we include price changes in hash?

**Option A**: Include prices (current approach)
- ✅ More accurate change detection
- ❌ Price-only changes trigger new insights (even without trades)

**Option B**: Exclude prices, only include holdings/orders
- ✅ Only triggers on actual portfolio changes
- ❌ Won't detect if user wants insights updated for price movements

**Recommendation**: **Option A** (include prices)
- Users likely want updated insights when prices change significantly
- 24-hour TTL prevents excessive API calls

### 2. TTL Management

**Option A**: DynamoDB TTL (recommended)
- Set `ttl` attribute to Unix timestamp (24 hours from now)
- DynamoDB automatically deletes expired items
- No manual cleanup needed

**Option B**: Application-level TTL check
- Check `generated_at` timestamp in application code
- Keep records longer (for analytics)
- More control, but requires manual cleanup

**Recommendation**: **Option A** (DynamoDB TTL)

### 3. Multiple Portfolio States

**Scenario**: User changes portfolio, then changes back to previous state

**Behavior**:
- First state: `SK=INSIGHTS#hash1` → cached
- Second state: `SK=INSIGHTS#hash2` → cached
- Back to first: `SK=INSIGHTS#hash1` → cache hit (if < 24h) ✅

**Storage**: Multiple records per user (one per portfolio state)
- DynamoDB TTL cleans up old states automatically
- No manual cleanup needed

---

## 📝 Questions to Resolve

1. **Should we include price changes in portfolio hash?**
   - Current thinking: Yes (users want updated insights for price movements)

2. **What if user wants to force refresh?**
   - Could add `?force_refresh=true` query parameter
   - Skips cache check

3. **Should we store historical insights?**
   - Current design: No (TTL deletes after 24h)
   - Alternative: Keep last N insights for analytics

4. **What about empty portfolios?**
   - Current: Return immediately without caching
   - Should we cache empty portfolio insights too?

5. **Error handling if DynamoDB write fails?**
   - Still return insights to user
   - Log error for monitoring
   - Next request will regenerate (acceptable)

---

## ✅ Recommended Implementation Plan

1. **Use DynamoDB `users` table** (single-table pattern)
2. **SK format**: `INSIGHTS#{portfolio_hash}`
3. **Include prices in hash** (for accurate change detection)
4. **Use DynamoDB TTL** (24 hours from generation)
5. **Check timestamp** in application (double-check TTL)
6. **Graceful degradation** (if DynamoDB fails, still call Gemini API)

---

## 🔄 Cache Invalidation Strategy

### Automatic (Hash-based)
- Portfolio changes → hash changes → cache miss → new insights ✅

### Manual (Optional)
- Could add endpoint: `DELETE /api/v1/insights/portfolio` to clear cache
- Or invalidate when orders/balances change (future enhancement)

---

## 📊 Monitoring & Metrics

**Key Metrics to Track**:
1. Cache hit rate (should be high if portfolios don't change frequently)
2. Gemini API call rate (should decrease with caching)
3. Average response time (cache hits vs misses)
4. DynamoDB read/write costs

**Alerts**:
- Cache hit rate < 50% (unexpected)
- DynamoDB errors (connection issues)
- Gemini API rate limit errors (even with caching)

---

## 🎯 Next Steps

1. **Review and approve design** ✅
2. **Create DynamoDB entity model** (InsightsItem)
3. **Implement DAO layer** (InsightsDAO)
4. **Update controller** to use caching
5. **Add tests** for cache hit/miss scenarios
6. **Monitor** cache hit rates and costs
