# Incident response integration tests

Tests for incident/security features (e.g. **IP block SEC-011**). All integration tests are **external/black-box**: they call only the gateway; they do not access Redis or any internal service.

## IP block (SEC-011)

**What we test from outside:**

1. **Init** – Create a user (register + login + logout) via the gateway.
2. **Step 3** – Same user, wrong password: 5 failed logins, then the **6th** request must get **403** (IP blocked). The gateway records each 401 from POST /auth/login and sets `ip_block:<ip>` in Redis after 5 failures. When the block is set, the failure count is also set to expire with the block so the count is removed when the block expires.
3. **Step 4** – Wait for the block TTL to expire (default 5 min), then login again with the correct password; must get **200** (block expired, count cleared, login works again).

**Run individually:**

```bash
cd integration_tests
python3 incident/test_ip_block.py
```

**Run via test runner:** `./run_all_tests.sh incident` (incident is not included in `./run_all_tests.sh all`).

**Note:** Step 4 uses a 5-minute sleep (default block TTL is 300s), so the incident suite takes at least 5 minutes when run in full.

## Before running user/integration tests (avoid 403 AUTH_004)

The **failure counter** is in Redis as `login_fail:<ip>`. If you only delete `ip_block:*`, the next 401 will set the block again. You must clear **both** `ip_block:*` and `login_fail:*` for **all IPs** (the gateway may see a different client IP than you expect).

**Run these two commands every time right before integration tests** (from the directory where your `docker-compose.yml` is, e.g. `docker/`):

```bash
# Remove all IP block keys
docker compose exec redis redis-cli --scan --pattern "ip_block:*" | xargs -I {} docker compose exec -T redis redis-cli DEL {}

# Remove all login-fail counters (this is the one that re-triggers the block)
docker compose exec redis redis-cli --scan --pattern "login_fail:*" | xargs -I {} docker compose exec -T redis redis-cli DEL {}
```

**Check current state** — inspect both; if only `ip_block:*` is cleared, `login_fail:*` still holds the count and the next 401 can re-block:

```bash
docker compose exec redis redis-cli KEYS "ip_block:*"    # IPs currently blocked (403)
docker compose exec redis redis-cli KEYS "login_fail:*"  # IPs still counting toward block
```

Verify both are empty (both should print `(empty array)`). Then run your tests immediately.

If you use plain `docker` (not compose), replace `docker compose exec redis` with `docker exec <your_redis_container_name>`.

Redeploy does **not** clear Redis unless Redis is recreated with no persistent volume.

## Why other integration tests fail after running IP block tests

The IP block test triggers the gateway to block **your client IP** for 5 min (default). All requests from the same machine get **403** until the block expires.

**What to do:**

1. **Unblock your IP** so other suites can run immediately:
   - If using Docker: get your host IP as seen by the gateway (often `127.0.0.1` or the host’s LAN IP). Then from a shell that can reach Redis:
     ```bash
     docker exec -it <redis_container_name> redis-cli DEL ip_block:127.0.0.1 login_fail:127.0.0.1
     ```
     (Replace `127.0.0.1` with the IP the gateway sees; check gateway logs for `client_ip` if unsure.) Clear **both** keys; otherwise the next 401 will re-block.
   - If Redis is on the host: clear **both** keys so the block does not come back on the next 401: `redis-cli DEL ip_block:<your_ip> login_fail:<your_ip>`.
2. **Wait 5 minutes** for the block TTL to expire, or clear both keys (see above), then run other tests.
3. **Run incident tests last** when you run multiple suites in one session, so the block doesn’t affect other tests.
