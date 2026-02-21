# Metrics — Current Plan and State

This doc is the **single source of truth** for our metrics. Review this before changing metrics code.

---

## 1. Plan Summary

- **Gateway: 4 metrics** (see below).
- **Each backend service (inventory, user, order, auth, insights): 3 metrics each** (requests_total, errors_total, request_latency_seconds).

Labels: **`status_code`** = HTTP status string (e.g. `"200"`, `"500"`). **`endpoint`** = request path.  
Rate / per 5m: use `rate(<metric>[5m])` or `increase(<metric>[5m])` in Prometheus.  
We **do not** expose: info metrics, uptime gauges, operation-level counters, or rate-limit gauges.

---

## 2. Gateway — 4 Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| `gateway_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `gateway_errors_total` | Counter | HTTP 4xx+5xx; labels: status_code, endpoint |
| `gateway_proxy_errors_total` | Counter | Proxy/backend failures (e.g. request_failed, 500, 502, 503); labels: target_service, error_type |
| `gateway_request_latency_seconds` | Histogram | Latency; label: endpoint |

---

## 3. Each Backend Service — 3 Metrics

### Inventory

| Metric | Type | Purpose |
|--------|------|---------|
| `inventory_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `inventory_errors_total` | Counter | 4xx+5xx; labels: status_code, endpoint |
| `inventory_request_latency_seconds` | Histogram | Latency; label: endpoint |

### User

| Metric | Type | Purpose |
|--------|------|---------|
| `user_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `user_errors_total` | Counter | 4xx+5xx; labels: status_code, endpoint |
| `user_request_latency_seconds` | Histogram | Latency; label: endpoint |

### Order

| Metric | Type | Purpose |
|--------|------|---------|
| `order_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `order_errors_total` | Counter | 4xx+5xx; labels: status_code, endpoint |
| `order_request_latency_seconds` | Histogram | Latency; label: endpoint |

### Auth

| Metric | Type | Purpose |
|--------|------|---------|
| `auth_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `auth_errors_total` | Counter | 4xx+5xx; labels: status_code, endpoint |
| `auth_request_latency_seconds` | Histogram | Latency; label: endpoint |

### Insights

| Metric | Type | Purpose |
|--------|------|---------|
| `insights_requests_total` | Counter | Rate + count; labels: status_code, endpoint |
| `insights_errors_total` | Counter | 4xx+5xx; labels: status_code, endpoint |
| `insights_request_latency_seconds` | Histogram | Latency; label: endpoint |

*(Insights: no metrics today; add these 3 when adding metrics.)*

---

## 4. `*_created` Metrics

Prometheus clients add a **`<name>_created`** series (Unix timestamp). **Do not graph it** — use the counter with `rate()` or `increase()` instead (e.g. `rate(user_requests_total[5m])`, not `user_requests_created`).

- **Gateway (Go):** We filter out `*_created` at `/metrics` (see `gateway/pkg/metrics/gatherer.go`).
- **Python services:** Ignore `*_created` in Grafana/PromQL.

---

## 5. PromQL Quick Reference

### Counters (request rate, volume, error rate)

Counters are monotonically increasing. Use `rate()` or `increase()`:

| What you want | PromQL |
|---------------|--------|
| Request rate (per sec) | `rate(user_requests_total[5m])` |
| Requests in last 1h | `increase(user_requests_total[1h])` |
| Error rate (4xx+5xx) | `rate(user_errors_total[5m])` |
| Gateway proxy failure rate | `rate(gateway_proxy_errors_total[5m])` |

Same pattern for any service: `gateway_*`, `order_*`, `inventory_*`, `auth_*`, `insights_*`.

### Histograms (latency)

Histograms are exposed as **three** metrics: `*_bucket`, `*_count`, `*_sum`. There is no series named e.g. `user_request_latency_seconds` alone.

| What you want | PromQL |
|---------------|--------|
| Request rate (from histogram) | `rate(user_request_latency_seconds_count[5m])` |
| Average latency | `rate(user_request_latency_seconds_sum[5m]) / rate(user_request_latency_seconds_count[5m])` |
| p95 latency | `histogram_quantile(0.95, rate(user_request_latency_seconds_bucket[5m]))` |
| p99 latency | `histogram_quantile(0.99, rate(user_request_latency_seconds_bucket[5m]))` |

### Label filters

- **status_code:** `user_requests_total{status_code="200"}`, `user_errors_total{status_code=~"5.."}`.
- **endpoint:** `user_request_latency_seconds_count{endpoint="/auth/login"}`.
- **Gateway proxy errors:** labels `target_service`, `error_type` (e.g. `request_failed`, `500`).

---

**Last updated:** Plan = **4 metrics for gateway** (requests, errors, proxy_errors, latency); **3 metrics for each backend service** (requests, errors, latency). Labels: status_code, endpoint.
