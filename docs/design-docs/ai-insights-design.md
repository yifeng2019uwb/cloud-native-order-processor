# AI Insights Feature Design (FEATURE-002)

> **Status**: Draft
> **Author**: Yifeng & Cursoe
> **Last Updated**: January 31, 2026

## 1. Overview

### Goal
Add an endpoint that aggregates user portfolio, orders, and price data, calls Google Gemini API (free tier), and returns a short text analysis for display in the UI.

### Scope (Option 1 - Lightweight)
- **New `insights_service`** - dedicated microservice for AI analysis
- Aggregates data from existing DAOs via shared `common` package (no HTTP service calls)
- Calls external LLM API with bounded prompt
- Returns structured JSON response
- Frontend displays the analysis text

### Out of Scope
- Caching LLM responses (can add later)
- Streaming responses
- Multiple LLM providers (pick one)
- Complex prompt engineering / RAG

---

## 2. Architecture

### Data Flow

```
┌─────────────┐     ┌─────────────────────────────────────────────────────────┐
│   Frontend  │────▶│  Gateway (/api/v1/insights)                              │
└─────────────┘     └─────────────────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │  Insights Service (NEW - port 8004)                      │
                    │  1. Authenticate user (JWT via common package)           │
                    │  2. Fetch data from DAOs (common package):               │
                    │     - UserDAO → user profile                             │
                    │     - BalanceDAO → USD balance                           │
                    │     - AssetBalanceDAO → asset holdings                   │
                    │     - AssetDAO → current prices                          │
                    │     - OrderDAO → recent orders                           │
                    │  3. Build prompt payload                                 │
                    │  4. Call Google Gemini API                               │
                    │  5. Parse and return response                            │
                    └─────────────────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │  Google Gemini API                                       │
                    └─────────────────────────────────────────────────────────┘
```

### Why Separate Insights Service?
- **Single responsibility**: Dedicated to AI/LLM functionality
- **Clean architecture**: Follows microservices pattern (better for demo)
- **Same DAO pattern**: Uses shared `common` package like all other services
- **No HTTP service calls**: Direct DynamoDB access via DAOs
- **Future-ready**: Additional AI features can be added here
- **Isolation**: LLM latency doesn't affect other services

### Gateway Configuration Required

**Gateway changes needed:**
1. Add `InsightsService` constant
2. Add `INSIGHTS_SERVICE_URL` env var (default: `http://insights_service:8004`)
3. Add route config: `/api/v1/insights/*` → Insights Service
4. Add circuit breaker for Insights Service
5. Route requires authentication (JWT)

---

## 3. API Contract

### Endpoint

```
GET /api/v1/insights/portfolio
```

### Request
- **Headers**: `Authorization: Bearer <JWT>` (user extracted from token)
- No path parameters needed - user is derived from JWT token

### Response (200 OK)

```json
{
  "data": {
    "summary": "Your portfolio is well-diversified with 60% in BTC and 30% in ETH. Recent market volatility has increased your holdings value by 5% this week. Consider reviewing your ETH position given the upcoming network upgrade.",
    "generated_at": "2026-01-31T10:30:00Z",
    "model": "gemini-1.5-flash"
  }
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | 2-4 sentence analysis from LLM |
| `generated_at` | ISO datetime | When the analysis was generated |
| `model` | string | LLM model used (for transparency) |

### Error Responses

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Unauthorized | Missing or invalid JWT |
| 404 | Not Found | User not found |
| 500 | Internal Error | LLM API failure |
| 503 | Service Unavailable | GOOGLE_GEMINI_API_KEY not configured |

---

## 4. Data Aggregation

### Data Sources (via DAOs)

| DAO | Data | Used For |
|-----|------|----------|
| `UserDAO` | username, email, created_at | User context |
| `BalanceDAO` | USD balance | Cash position |
| `AssetBalanceDAO` | asset holdings (quantity per asset) | Portfolio composition |
| `AssetDAO` | current prices, 24h change, market cap | Market context |
| `OrderDAO` | recent orders (last 10) | Trading activity |

### Aggregated Payload for LLM

```json
{
  "user": {
    "username": "alice",
    "account_age_days": 45
  },
  "portfolio": {
    "usd_balance": 5000.00,
    "total_value_usd": 15000.00,
    "assets": [
      {
        "asset_id": "BTC",
        "quantity": 0.15,
        "current_price": 45000.00,
        "value_usd": 6750.00,
        "allocation_pct": 45.0,
        "price_change_24h_pct": 2.5
      },
      {
        "asset_id": "ETH",
        "quantity": 2.5,
        "current_price": 2500.00,
        "value_usd": 6250.00,
        "allocation_pct": 41.7,
        "price_change_24h_pct": -1.2
      }
    ]
  },
  "recent_orders": [
    {
      "order_type": "MARKET_BUY",
      "asset_id": "BTC",
      "quantity": 0.05,
      "price": 44000.00,
      "created_at": "2026-01-30T14:00:00Z"
    }
  ]
}
```

---

## 5. LLM Integration

### Requirements

- **Cost**: Free tier only (personal project)
- **Purpose**: Generate 2–4 sentence portfolio analysis from aggregated user data
- **Traffic**: 10–50 requests/hour at peak time
- **Input**: ~200–400 tokens (structured JSON with portfolio, holdings, orders)
- **Output**: ~40–80 tokens (short text summary)
- **Quality**: Good enough for demo; doesn't need state-of-the-art reasoning

### Provider Comparison

| Provider | Model | Free Tier | SDK | Pros | Cons |
|----------|-------|-----------|-----|------|------|
| Google Gemini | gemini-1.5-flash | 60 req/min, 1M tokens/day | google-generativeai | Simple SDK, stable API, generous free tier | Google account required |
| Groq | llama-3.1-8b | ~30 req/min | groq | Very fast inference | Smaller model, less capable |
| Ollama | llama3.2 | Unlimited | HTTP API (local) | No API key, fully local | Requires running local process or Docker |
| Hugging Face | mistral-7b | Rate limited | huggingface_hub | Many model options | API can be slow, inconsistent availability |

### Decision: **Google Gemini**

- **Model**: `gemini-1.5-flash`
- **SDK**: `google-generativeai`

**Why Gemini over others?**
- **vs Groq**: Gemini has higher quality output for text generation; Groq is faster but uses smaller open-source models
- **vs Ollama**: Gemini requires no local infra; Ollama needs a running local process which complicates Docker deployment
- **vs Hugging Face**: Gemini has more consistent availability and simpler SDK; HF inference API can be slow or rate-limited unpredictably

**Trade-off accepted**: Requires Google account and API key, but setup is straightforward and free tier is sufficient.

### Code Setup

**1. Install SDK:**
```bash
pip install google-generativeai
```

**2. Get API Key:**
- Go to https://aistudio.google.com/apikey
- Create API key (free)
- **Security**: Store in environment variable or secrets file (never commit to GitHub)
  - Local: `.env` file (add to `.gitignore`)
  - Docker: `docker-compose.yml` env var or Docker secrets
  - Production: AWS Secrets Manager or similar

**3. Basic Usage:**
```python
import google.generativeai as genai
import os

# Configure
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate content
response = model.generate_content(
    system_instruction="You are a helpful financial assistant...",
    contents="Analyze this portfolio: ..."
)

summary = response.text
```

**4. In Insights Service:**
```python
# services/insights_service/src/services/llm_service.py
class LLMService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not configured")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_insights(self, portfolio_context: PortfolioContext) -> str:
        """Generate insights - sync call (Gemini SDK is sync)"""
        prompt = self._build_prompt(portfolio_context)
        response = self.model.generate_content(
            system_instruction=self.SYSTEM_PROMPT,
            contents=prompt,
            generation_config={
                "max_output_tokens": 150,
                "temperature": 0.7,
            }
        )
        return response.text
```

### Prompt Strategy

**System Prompt** (fixed):
```
You are a helpful financial assistant analyzing a cryptocurrency portfolio.
Provide a brief, actionable summary (2-4 sentences) based on the user's
portfolio composition, recent trading activity, and current market conditions.
Be concise and avoid financial advice disclaimers.
```

**User Prompt** (dynamic, from aggregated data):
```
Analyze this portfolio:
- USD Balance: $5,000
- Total Portfolio Value: $15,000
- Holdings: BTC (45%, +2.5% 24h), ETH (41.7%, -1.2% 24h)
- Recent Activity: Bought 0.05 BTC yesterday at $44,000

Provide a 2-4 sentence summary.
```

### Constraints
- **Max tokens**: 150 (output limit)
- **Timeout**: 30 seconds
- **Temperature**: 0.7 (balanced creativity)

---

## 6. Data Models

### Input: PortfolioContext (for LLM prompt)

```python
class PortfolioContext(BaseModel):
    """Aggregated data sent to LLM"""
    username: str
    account_age_days: int
    usd_balance: Decimal
    total_portfolio_value: Decimal
    holdings: list[HoldingData]
    recent_orders: list[OrderData]


class HoldingData(BaseModel):
    """User's asset holding with market data"""
    asset_id: str
    quantity: Decimal
    current_price: Decimal
    price_change_24h_pct: Decimal
    value_usd: Decimal                 # Computed: quantity * current_price
    allocation_pct: Decimal            # Computed: value_usd / total * 100


class OrderData(BaseModel):
    """Recent order summary"""
    order_type: str
    asset_id: str
    quantity: Decimal
    price: Decimal
    created_at: datetime
```

**Note**: All data available from existing DAOs. No changes to common package needed.

### Output: Insights Response (returned to frontend)

```python
class InsightsData(BaseModel):
    """The insights content returned to frontend"""
    summary: str                     # 2-4 sentence analysis from LLM
    generated_at: datetime           # When analysis was generated
    model: str                       # LLM model used (e.g., "gemini-1.5-flash")


class GetInsightsResponse(BaseModel):
    """API response - follows existing service patterns"""
    data: InsightsData
```

**Example Response:**
```json
{
    "data": {
        "summary": "Your portfolio is well-diversified with 45% in BTC and 42% in ETH. BTC is up 2.5% today while ETH is down slightly. Your recent BTC purchase at $44,000 is now showing a small gain.",
        "generated_at": "2026-01-31T10:30:00Z",
        "model": "gemini-1.5-flash"
    }
}
```

### Error Response

Uses existing error pattern from `common` package.

```json
{
    "error": "AI insights not configured",
    "detail": "GOOGLE_GEMINI_API_KEY environment variable is not set"
}
```

---

## 7. Error Handling

| Scenario | Handling | Response |
|----------|----------|----------|
| No API key configured | Check on startup, return 503 | `{"error": "AI insights not configured"}` |
| LLM API timeout | 30s timeout, return 500 | `{"error": "Analysis timed out"}` |
| LLM API error | Catch exception, log, return 500 | `{"error": "Unable to generate analysis"}` |
| Empty portfolio | Return helpful message (no LLM call) | `{"summary": "Your portfolio is empty. Deposit funds to get started!"}` |
| No orders | Still call LLM (orders optional) | Normal analysis without recent activity |
| Rate limited by LLM | Return 429 | `{"error": "Too many requests, try again later"}` |

---

## 8. Security Considerations

- **API Key Management** (Public GitHub Repo):
  - Never commit API keys to code or config files
  - Use environment variables: `GOOGLE_GEMINI_API_KEY` from `.env` file
  - `.env` file must be in `.gitignore`
  - Docker: Use `docker-compose.yml` env vars (not committed) or Docker secrets
  - Production: Use AWS Secrets Manager or similar secret management
  - Code implementation: Read from `os.getenv()` only, never hardcode
- **User Data**: Only user's own data is sent to LLM (authenticated endpoint)
- **PII**: Avoid sending email/password to LLM (only username, balances, orders)
- **Prompt Injection**: User data is structured (JSON), not free-form text

---

## 9. Cost Estimate

**Google Gemini** free tier. Personal project, minimal traffic — no cost.

---

## 10. Future Enhancements (Out of Scope)

- Cache responses (Redis, 5-minute TTL)
- Streaming responses for real-time UI
- Multiple LLM providers with fallback
- User preference for analysis style
- Historical trend analysis
- Alerts based on AI analysis

---

## 11. Acceptance Criteria Checklist

- [ ] New `insights_service` created and running on port 8004
- [ ] `GET /api/v1/insights/portfolio` endpoint works
- [ ] Aggregates portfolio, orders, and price data via common DAOs
- [ ] Calls Google Gemini API with bounded prompt
- [ ] Returns structured JSON with summary
- [ ] API key from environment (not hardcoded)
- [ ] Gateway routes to insights service correctly (route config, circuit breaker, service URL)
- [ ] Frontend displays the analysis
- [ ] Errors return clear HTTP/JSON responses
- [ ] Unit tests for LLM service
- [ ] Integration test for endpoint
- [ ] Docker deployment works (docker-compose)
