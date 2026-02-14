"""
In-memory cache for Gemini insights - 24h TTL, keyed by (username, portfolio_hash)
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from api_models.insights.portfolio_context import PortfolioContext

CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Simple in-memory cache: {(username, portfolio_hash): (summary, generated_at, model)}
_cache: dict[tuple[str, str], tuple[str, datetime, str]] = {}


def compute_portfolio_hash(context: PortfolioContext) -> str:
    """Compute hash for portfolio state - changes when holdings/orders/values change"""
    data = {
        "total_portfolio_value": str(context.total_portfolio_value),
        "usd_balance": str(context.usd_balance),
        "holdings": [
            {"asset_id": h.asset_id, "quantity": str(h.quantity), "allocation_pct": str(h.allocation_pct)}
            for h in context.holdings[:10]
        ],
        "orders": [
            {"asset_id": o.asset_id, "order_type": o.order_type, "quantity": str(o.quantity), "created_at": o.created_at.isoformat()}
            for o in context.recent_orders[:10]
        ],
    }
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def get_cached(username: str, portfolio_hash: str) -> Optional[tuple[str, datetime, str]]:
    """Return (summary, generated_at, model) if cache hit and not expired, else None"""
    key = (username, portfolio_hash)
    if key not in _cache:
        return None
    summary, generated_at, model = _cache[key]
    age = (datetime.now(timezone.utc) - generated_at).total_seconds()
    if age > CACHE_TTL_SECONDS:
        del _cache[key]
        return None
    return (summary, generated_at, model)


def save_cached(username: str, portfolio_hash: str, summary: str, model: str) -> None:
    """Store result in cache"""
    _cache[(username, portfolio_hash)] = (summary, datetime.now(timezone.utc), model)


def clear_cache() -> None:
    """Clear cache (for testing)"""
    _cache.clear()
