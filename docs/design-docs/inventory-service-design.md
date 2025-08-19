# 📦 Inventory Service Design

## 🎯 **Purpose**
Document design decisions, options considered, and rationale for the Inventory Service to prevent re-designing and maintain consistency.

---

## 📋 **Component Design: Inventory Service**
**Date**: 2025-08-20
**Author**: System Design Team
**Status**: Completed

#### **🎯 Problem Statement**
- **Problem**: Need digital asset catalog and pricing data for trading platform
- **Requirements**: Asset listing, real-time pricing, metadata management, public access
- **Constraints**: External API integration, data freshness, cost efficiency, scalability

#### **🔍 Options Considered**

- **Option A: Static Asset Database**
  - ✅ Pros: Simple, fast, no external dependencies
  - ❌ Cons: Outdated prices, manual updates, limited assets
  - 💰 Cost: Low cost, low accuracy
  - ⏱️ Complexity: Low complexity, low functionality

- **Option B: Real-time API Integration (Chosen)**
  - ✅ Pros: Live prices, comprehensive asset coverage, automatic updates
  - ❌ Cons: External dependency, API rate limits, network latency
  - 💰 Cost: Medium cost, high accuracy
  - ⏱️ Complexity: Medium complexity, high functionality

- **Option C: Hybrid Approach**
  - ✅ Pros: Best of both worlds, fallback options, cost optimization
  - ❌ Cons: Complex implementation, multiple data sources, sync challenges
  - 💰 Cost: Medium cost, high accuracy
  - ⏱️ Complexity: High complexity, high functionality

#### **🏗️ Final Decision**
- **Chosen Option**: Real-time API integration with CoinGecko for live pricing
- **Rationale**: Best user experience with live data, comprehensive asset coverage
- **Trade-offs Accepted**: External dependency for superior data quality

#### **🔧 Implementation Details**

**Key Components**:
- **Asset Controller**: Asset listing, search, and details
- **Health Controller**: Service health and external API status
- **CoinGecko Integration**: Real-time cryptocurrency data
- **Data Management**: Asset initialization, caching, and updates

**Data Structures**:
- **Asset Entity**: asset_id, symbol, name, current_price, market_cap, volume_24h
- **Asset Status**: Active, Inactive, Suspended
- **Price Data**: Real-time pricing from CoinGecko API
- **Metadata**: Asset descriptions, categories, and additional information

**Configuration**:
- **External API**: CoinGecko API endpoints and rate limiting
- **Data Refresh**: Pricing update intervals and caching strategies
- **Asset Categories**: Major, altcoin, stablecoin classifications
- **Public Access**: No authentication required for asset browsing

#### **🧪 Testing Strategy**
- **Unit Tests**: Asset logic, validation, business rules
- **Integration Tests**: External API integration, database operations
- **API Tests**: Endpoint functionality, error handling, response validation
- **Performance Tests**: Response times, concurrent requests, caching efficiency

#### **📝 Notes & Future Considerations**
- **Known Limitations**: External API dependency, rate limiting constraints
- **Future Improvements**: WebSocket price updates, advanced filtering, analytics

---

## 📝 **Quick Decision Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Data Source | CoinGecko over static DB | Live prices, comprehensive coverage | High | ✅ Done |
| 8/17 | Access Control | Public over authenticated | User experience, discovery | Medium | ✅ Done |
| 8/17 | Asset Coverage | 98+ assets over limited | Trading flexibility | High | ✅ Done |
| 8/17 | Price Updates | Real-time over batch | User experience, accuracy | Medium | ✅ Done |

**Status Indicators:**
- ✅ **Done** - Decision implemented and working
- 🔄 **In Progress** - Decision made, implementation ongoing
- 📋 **Planned** - Decision made, not yet started
- ❌ **Rejected** - Decision was made but later rejected
- 🔍 **Under Review** - Decision being reconsidered

---

## 🏗️ **Simple Architecture Diagrams**

### **Inventory Service Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │ Inventory Service│    │   Common        │
│   (No Auth)     │◄──►│   (FastAPI)     │◄──►│   Package       │
│                 │    │   - Controllers │    │   - Entities    │
│                 │    │   - Validation  │    │   - DAOs        │
│                 │    │   - External    │    │   - Security    │
│                 │    │   API Integration│   │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   - Assets      │
                       │   - Metadata    │
                       │   - Categories  │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   CoinGecko     │
                       │   API          │
                       │   - Live Prices │
                       │   - Market Data │
                       └─────────────────┘
```

### **Data Flow**
```
1. Asset Initialization (Startup)
2. CoinGecko API Integration
3. Real-time Price Updates
4. Asset Data Storage
5. Public API Access
6. Asset Discovery & Search
7. Portfolio Integration
```

---

## 🔐 **API Design & Models**

### **Asset Management Endpoints**

#### **List All Assets**
```python
# Request Model
class AssetListRequest(BaseModel):
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)
    category: Optional[AssetCategory] = None
    active_only: Optional[bool] = Field(True)
    sort_by: Optional[AssetSortField] = Field(AssetSortField.MARKET_CAP)
    sort_order: Optional[SortOrder] = Field(SortOrder.DESC)

# Response Model
class AssetListResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetListData]
    timestamp: datetime

class AssetListData(BaseModel):
    assets: List[AssetData]
    total_count: int
    has_more: bool
    pagination: PaginationInfo

class AssetData(BaseModel):
    asset_id: str
    symbol: str
    name: str
    current_price: Decimal
    market_cap: Optional[Decimal]
    volume_24h: Optional[Decimal]
    price_change_24h: Optional[Decimal]
    price_change_percentage_24h: Optional[Decimal]
    status: AssetStatus
    category: AssetCategory
    created_at: datetime
    updated_at: datetime
```

#### **Get Asset Details**
```python
# Response Model
class AssetDetailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetDetailData]
    timestamp: datetime

class AssetDetailData(BaseModel):
    asset_id: str
    symbol: str
    name: str
    description: Optional[str]
    current_price: Decimal
    market_cap: Optional[Decimal]
    volume_24h: Optional[Decimal]
    price_change_24h: Optional[Decimal]
    price_change_percentage_24h: Optional[Decimal]
    all_time_high: Optional[Decimal]
    all_time_low: Optional[Decimal]
    status: AssetStatus
    category: AssetCategory
    website: Optional[str]
    whitepaper: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_price_update: datetime
```

#### **Search Assets**
```python
# Request Model
class AssetSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)
    category: Optional[AssetCategory] = None
    active_only: Optional[bool] = Field(True)
    include_inactive: Optional[bool] = Field(False)

# Response Model
class AssetSearchResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetSearchData]
    timestamp: datetime

class AssetSearchData(BaseModel):
    query: str
    assets: List[AssetData]
    total_count: int
    has_more: bool
    pagination: PaginationInfo
    search_metadata: SearchMetadata

class SearchMetadata(BaseModel):
    search_time_ms: float
    total_assets_searched: int
    search_algorithm: str
    relevance_scores: Optional[Dict[str, float]]
```

### **Asset Categories Endpoints**

#### **Get Asset Categories**
```python
# Response Model
class AssetCategoriesResponse(BaseModel):
    success: bool
    message: str
    data: Optional[AssetCategoriesData]
    timestamp: datetime

class AssetCategoriesData(BaseModel):
    categories: List[AssetCategoryData]
    total_count: int

class AssetCategoryData(BaseModel):
    category: AssetCategory
    name: str
    description: str
    asset_count: int
    total_market_cap: Decimal
    percentage_of_total: Decimal
```

#### **Get Assets by Category**
```python
# Request Model
class CategoryAssetsRequest(BaseModel):
    category: AssetCategory = Field(...)
    limit: Optional[int] = Field(100, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)
    sort_by: Optional[AssetSortField] = Field(AssetSortField.MARKET_CAP)
    sort_order: Optional[SortOrder] = Field(SortOrder.DESC)

# Response Model
class CategoryAssetsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[CategoryAssetsData]
    timestamp: datetime

class CategoryAssetsData(BaseModel):
    category: AssetCategory
    assets: List[AssetData]
    total_count: int
    has_more: bool
    category_stats: CategoryStats

class CategoryStats(BaseModel):
    total_market_cap: Decimal
    total_volume_24h: Decimal
    average_price_change_24h: Decimal
    top_performer: AssetData
    worst_performer: AssetData
```

### **Market Data Endpoints**

#### **Get Market Overview**
```python
# Response Model
class MarketOverviewResponse(BaseModel):
    success: bool
    message: str
    data: Optional[MarketOverviewData]
    timestamp: datetime

class MarketOverviewData(BaseModel):
    total_market_cap: Decimal
    total_volume_24h: Decimal
    market_dominance: Dict[str, Decimal]
    top_gainers: List[AssetData]
    top_losers: List[AssetData]
    most_traded: List[AssetData]
    market_sentiment: MarketSentiment
    last_updated: datetime
```

#### **Get Price History**
```python
# Request Model
class PriceHistoryRequest(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=10)
    days: Optional[int] = Field(7, ge=1, le=365)
    interval: Optional[PriceInterval] = Field(PriceInterval.DAILY)

# Response Model
class PriceHistoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[PriceHistoryData]
    timestamp: datetime

class PriceHistoryData(BaseModel):
    asset_id: str
    symbol: str
    prices: List[PricePoint]
    interval: PriceInterval
    days: int
    price_change: Decimal
    price_change_percentage: Decimal

class PricePoint(BaseModel):
    timestamp: datetime
    price: Decimal
    volume: Optional[Decimal]
    market_cap: Optional[Decimal]
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
    external_apis: Dict[str, str]
```

#### **Health Detailed**
```python
# Response Model
class HealthDetailedResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
    uptime: float
    database: str
    external_apis: Dict[str, ExternalAPIStatus]
    asset_count: int
    last_price_update: datetime
    cache_status: CacheStatus

class ExternalAPIStatus(BaseModel):
    status: str
    response_time_ms: float
    last_check: datetime
    error_count: int
    rate_limit_remaining: Optional[int]

class CacheStatus(BaseModel):
    status: str
    hit_rate: float
    size: int
    last_cleanup: datetime
```

#### **Metrics**
```python
# Response Model
class MetricsResponse(BaseModel):
    request_count: int
    error_count: int
    average_response_time: float
    asset_count: int
    external_api_calls: int
    cache_hit_rate: float
    database_operations: int
    timestamp: datetime
```

---

## 🔗 **Related Documentation**

- **[Services Design](./services-design.md)**: Overall services architecture
- **[Order Service Design](./order-service-design.md)**: Asset data integration
- **[Common Package Design](./common-package-design.md)**: Shared components design
- **[Inventory Service README](../services/inventory_service/README.md)**: Implementation and usage guide

---

**🎯 This inventory service design provides comprehensive digital asset management with real-time pricing, search capabilities, and public access for asset discovery.**
