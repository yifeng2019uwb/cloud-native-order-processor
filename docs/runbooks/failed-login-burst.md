# Incident Response Runbook: Failed-Login Burst (SEC-010)

**Scenario**: Burst of failed login attempts from a single IP (potential brute-force or credential stuffing).

**Trigger**: **5 failed logins from the same IP in 1 day** (configured window; see SEC-011). When the gateway sees 5× 401 from POST /auth/login for the same IP within that window, it auto-sets the block.

**Prerequisites**: SEC-011 (IP block) is implemented: gateway checks Redis `ip_block:<ip>` and returns 403 for blocked IPs; gateway also records failed logins and can auto-set the block after 5 failures in a 1-day window. See [Gateway README](../../gateway/README.md) and [integration_tests/incident/README.md](../../integration_tests/incident/README.md).

---

## 1. Verify and identify

**Goal**: Confirm the trigger and identify the client IP.

| Step | Action | Where / How |
|------|--------|--------------|
| 1.1 | Check audit logs for failed auth events from the same IP. | **Loki**: `{service="audit"} \| json \| action="auth_failed"` — filter by time range and look for repeated `client_ip` or similar. See [threat model](../design-docs/threat-model.md) and [logging standards](../design-docs/logging-standards.md). |
| 1.2 | Optionally check gateway logs for "RecordFailedLogin" or "Request from blocked IP". | Gateway logs (stdout/JSON); search for `client_ip` and `auth_failed` or block-related messages. |
| 1.3 | Record the **client IP** and **time window** of the burst. | Note for containment and evidence. |

**Trigger confirmed when**: You observe 5+ failed logins from the same IP within the 1-day window (or audit/logs show the IP was blocked or is hitting 403).

---

## 2. Containment

**Goal**: Ensure the IP cannot continue to attempt logins (gateway may have already auto-blocked).

| Step | Action | Notes |
|------|--------|--------|
| 2.1 | **Check if the IP is already blocked.** | Gateway (SEC-011) auto-sets `ip_block:<ip>` in Redis after 5 failed logins in the 1-day window. If the burst just happened, the next request from that IP may already get 403. |
| 2.2 | **If Redis is available and you need to block immediately** (e.g. before 5 failures, or to extend block): | From a host that can reach Redis (e.g. exec into gateway pod or bastion): |
| | Block the IP with TTL: | `redis-cli SET ip_block:<client_ip> 1 EX 300` (5 min, gateway default) or `EX 86400` (24h production). Failure count expires with the block. Key prefix: `ip_block:`. |
| 2.3 | **Verify block**: From that IP, a request to the gateway (e.g. POST /api/v1/auth/login or GET /health) should receive **403**. | Integration test flow: `integration_tests/incident/test_ip_block.py` (run `./run_all_tests.sh incident` from `integration_tests`). |

**Containment achieved when**: Requests from that IP to the gateway return 403 (block enforced by gateway auth middleware).

---

## 3. Evidence and documentation

**Goal**: Record what happened and what was done for later review.

| Step | Action |
|------|--------|
| 3.1 | Record **date/time (UTC)**, **client IP**, **trigger** (e.g. "5 failed logins in 1 day"), and **action** (e.g. "auto-block applied" or "manual block via redis-cli SET ip_block:<ip> 1 EX 300"). |
| 3.2 | Save or export relevant log excerpts (audit logs, gateway logs) for the time window. |
| 3.3 | If manual block was applied, note **TTL** and **when the block expires** (or that it was removed manually). |

---

## 4. Follow-up and review

**Goal**: Decide on communication, unblock policy, and post-incident review.

| Step | Action |
|------|--------|
| 4.1 | **Unblock**: Block expires automatically when the Redis key TTL ends. To unblock earlier you must clear **both** keys or the next 401 will re-block: `redis-cli DEL ip_block:<client_ip> login_fail:<client_ip>`. |
| 4.2 | **Communication**: If this is a production or shared environment, inform stakeholders per your policy (e.g. "IP &lt;x&gt; blocked due to failed-login burst; block expires at &lt;time&gt;"). |
| 4.3 | **Review**: After the incident, review whether the trigger threshold or block duration should change; check for patterns (same user targeted, bot behaviour). Update this runbook if procedures change. |

---

## 5. Run integration tests after unblock

**Goal**: So that user/auth integration tests do not hit 403 AUTH_004, clear **all** IP-block and login-fail keys in Redis before running tests. The gateway may see a different client IP (e.g. Docker bridge); clearing all keys avoids guessing.

| Step | Action |
|------|--------|
| 5.1 | **Check current state** (from directory where `docker-compose.yml` runs, e.g. `docker/`): `docker compose exec redis redis-cli KEYS "ip_block:*"` (IPs currently blocked → 403), `docker compose exec redis redis-cli KEYS "login_fail:*"` (IPs with failure count; next 401 can re-block). Redis on host: `redis-cli KEYS "ip_block:*"` and `redis-cli KEYS "login_fail:*"`. |
| 5.2 | **Clear both** key families. Docker Compose: `docker compose exec redis redis-cli --scan --pattern "ip_block:*" \| xargs -I {} docker compose exec -T redis redis-cli DEL {}` and `docker compose exec redis redis-cli --scan --pattern "login_fail:*" \| xargs -I {} docker compose exec -T redis redis-cli DEL {}`. Plain Docker: use `docker exec <redis_container_name>`. Redis on host: KEYS then DEL each. |
| 5.3 | Verify: run the two KEYS commands again; both return `(empty array)`. |
| 5.4 | Run integration tests (e.g. `cd integration_tests && ./run_all_tests.sh user`). |

See [integration_tests/README.md](../../integration_tests/README.md) and [integration_tests/incident/README.md](../../integration_tests/incident/README.md#before-running-userintegration-tests-avoid-403-auth_004).

---

## References

- **SEC-011 (IP block)**: [Gateway README](../../gateway/README.md) — IP block behaviour, Redis keys, tracing in gateway logs.
- **Integration test**: [integration_tests/incident/README.md](../../integration_tests/incident/README.md) — Full flow (init → 5 wrong logins → 403 → wait 5 min → login works again).
- **Audit logging**: [Threat model](../design-docs/threat-model.md) — Loki query for `action="auth_failed"`; [Logging standards](../design-docs/logging-standards.md).
- **Security audit**: [docs/design-docs/security-audit.md](../design-docs/security-audit.md) §11 — IP block / brute-force protection.
