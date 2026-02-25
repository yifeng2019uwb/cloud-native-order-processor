# Demo Script — Cloud-Native Order Processor

**~6 min** | 1: Business flow · 2: Repo & deploy · 3: Observability · 4: Standards & docs · 5: Close

---

## Part 1 — Business Flow — ~1.5 min

**Show:** http://localhost:3000 → Log in → Account, deposit (e.g. 1000) → Trading, buy one asset → Portfolio (result).

**Say:** *"Hi everyone. This is the Cloud-Native Order Processor, a distributed trading platform built for scale. First, I'll log in—our Go Gateway validates the JWT and manages the session via Redis; the Auth service behind it issues the token. Next, I'll deposit funds, which updates our balance via the User Service. Finally, I'll place a buy order. Our Inventory Service provides dynamic pricing, and the Order Service coordinates across the stack to execute the trade atomically. You can see the result instantly in the Portfolio—that's a successful end-to-end distributed transaction."*

---

## Part 2 — Repo Structure & Automation — ~1.5 min

**Show:** GitHub repo root (folders) → terminal: `./docker/deploy.sh --help` → (optional) Docker Desktop.

**Say:** *"The project follows a modular, enterprise-standard layout. Gateway: our Go API Gateway for security and routing. Frontend: React UI, all calls through the gateway. Services: five independent FastAPI backends—user, order, inventory, auth, and one more in the stack. Integration_tests: end-to-end and load tests. Docker: orchestration and deploy logic. Docs: design specs and runbooks. At the repo root: BACKLOG and DAILY_WORK_LOG for status and work history."*  
*(After showing deploy.sh help:)* *"Deployment is driven by this script—highly modular. You can deploy the core stack or add the monitoring stack with a second command."*  
*(If showing Docker:)* *"Once deployed, you get this microservice cluster—backends, Gateway, Redis, LocalStack—all as independent containers. Docker is the only requirement to get the whole environment live."*

---

## Part 3 — Observability & Real-Time Testing — ~1.5 min

**Show:** Grafana http://localhost:3001 → **Metrics:** dashboard or Explore → Prometheus (e.g. request rate, latency, error rate) → **Logs:** Explore, Loki: `{service="gateway"} | json` or `{service="order"} | json` (Part 1 traffic) → `{service="audit"} | json`. Then terminal: `cd integration_tests && ./run_all_tests.sh inventory` → back to Loki (new logs, 422s).

**Say:** *"We have both metrics and logs in Grafana. Prometheus gives us request rate, latency, and error rate per service. Loki gives us structured JSON logs with Request IDs—we can trace one user action through every service. Security events like login and token creation are in the audit log, separate from app logs."*  
*(When starting the test:)* *"To see resilience under load, I'm running the integration suite. You'll see metrics and logs update—including 422 validation errors in the logs. Those are expected. This real-time visibility is what makes the system production-ready."*

---

## Part 4 — Engineering Standards & Docs — ~1 min

**Show:** Terminal: run a quick test (e.g. `cd gateway && ./dev.sh test` or `cd integration_tests && ./run_all_tests.sh auth`) so output scrolls. Then GitHub **docs/** folder, or open one doc (e.g. a runbook) so they see real content.

**Say:** *"The real depth is in engineering discipline. Here's our test suite running—unit and integration, all runnable from the repo. We also have load tests and resilience at the gateway: rate limiting, circuit breaker, IP blocking. All of it is documented—runbooks, design docs, backlog."*

---

## Part 5 — Close — ~30 sec

**Say:** *"To wrap up: this is a complete engineering ecosystem—scalable, observable, and easy to deploy. Everything you've seen is in the repo. Thanks for watching!"*
