# STRIDE Threat Model

This document maps STRIDE threats to components, mitigations, and test coverage for the Cloud-Native Order Processor. **Test coverage below is integration tests only** — only these prove the feature end-to-end.

## STRIDE Threat Model

| Threat | Component | Mitigation | Integration test (proof) |
|--------|-----------|------------|---------------------------|
| **Spoofing** (JWT) | Auth Service, TokenManager | JWT signature validation (HS256), expiry check; secret only in Auth Service | `integration_tests/auth/test_gateway_auth.py` — invalid token → 401 on protected endpoints. Tampered token (wrong secret) not covered by integration test. |
| **Tampering** | Gateway, backends | TLS in production; server-side validation and sanitization; no trust of client-supplied identity | None. |
| **Repudiation** | All services (mutations) | Audit log on auth events (login/logout/register, failures); AuditLogger to Loki | None (manual Loki e.g. `{service="audit"} \| json \| action="auth_failed"`). |
| **Information disclosure** | Order / User services | Owner check; wrong-owner → 404; no secrets in logs | None. |
| **Denial of service** | Gateway | Redis-based rate limiting per IP; circuit breakers on backend calls | `integration_tests/load_tests/k6/rate-limiting.js` |
| **Brute-force / credential stuffing** | Gateway (auth) | **IP block (SEC-011):** After 5 failed logins (401) per IP in a 1-day window, gateway sets `ip_block:<ip>` in Redis; subsequent requests from that IP get 403 until TTL expires. | `integration_tests/incident/test_ip_block.py` — init, 5 wrong logins → 6th 403, wait 5 min → login works again |
| **Elevation of privilege** | All services | Single user role; no RBAC; protected = any valid JWT | N/A — no role-based endpoints |

## IDOR (Insecure Direct Object Reference)

| Scenario | Component | Mitigation | Integration test (proof) |
|----------|-----------|------------|---------------------------|
| User A → User B's order | Order Service | **Implemented:** Identity from JWT only (not request body). `get_order` loads order then checks `order.username == current_user.username`; mismatch → 404 so User A cannot get User B's order. | `integration_tests/order_service/orders/get_order_tests.py` — `test_get_order_idor_user_b_cannot_get_user_a_order()` |

## Out of Scope

- **mTLS between services** — Single developer / internal network; TLS at edge sufficient for project scope.
- **RBAC** — Single user role by design; all authenticated users have same permissions (trading, portfolio, account). No admin-only customer-facing APIs.
- **Token refresh** — Access tokens expire (e.g. 1h); no refresh flow in current scope.
- **E2E tampered-token test** — Unit test covers wrong-secret in TokenManager; gateway E2E with JWT signed by wrong secret not yet in suite.

## References

- Authentication: `docs/design-docs/gateway-design.md`, `docs/centralized-authentication-architecture.md`
- Security audit: `docs/design-docs/security-audit.md`
- Rate limiting: `integration_tests/load_tests/k6/README.md`, `gateway/pkg/utils/rate_limit.go`
- IP block (SEC-011): `gateway/README.md`, `integration_tests/incident/README.md`, `docs/design-docs/security-audit.md` (§11)
- Audit logging: `services/common/src/auth/security/audit_logger.py`; query audit logs: `{service="audit"} \| json \| action="auth_failed"` (Loki)
