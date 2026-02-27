# Demo Script — Cloud-Native Order Processor

**~6 min** | 1: Business flow · 2: Repo & deploy · 3: Observability · 4: Standards & docs · 5: Close

---

## Part 1 — Business Flow — ~1.5 min

**Show:** http://localhost:3000 → Log in → Account, deposit (e.g. 1000) → Trading, buy one asset → Portfolio (result).

**Say:** *"Hi everyone. This is the Cloud-Native Order Processor, a distributed trading platform built for scale. First, I'll log in—our Go Gateway validates the JWT and manages the session via Redis; the Auth service behind it issues the token. Next, I'll deposit funds, which updates our balance via the User Service. Finally, I'll place a buy order. Our Inventory Service provides dynamic pricing, and the Order Service coordinates across the stack to execute the trade atomically. You can see the result instantly in the Portfolio—that's a successful end-to-end distributed transaction."*

---

## Part 2 — Repo Structure & Automation — ~1.5 min

**Show:** GitHub repo root (folders) → terminal: `./docker/deploy.sh --help` → (optional) Docker Desktop.

**Say:** *"The project follows a modular, enterprise-standard layout. At the repo root—in alpha order as you see it:  Docker: orchestration and deploy logic. Docs: design specs and runbooks. Frontend: React UI, all calls through the gateway. Gateway: our Go API Gateway for security and routing. Integration_tests: end-to-end and load tests. Services: five independent FastAPI backends—user, order, inventory, auth, and one more in the stack. At the bottom of the repo: BACKLOG and DAILY_WORK_LOG for status and work history."*

*(After showing deploy.sh help:)* *"Deployment is driven by this script—highly modular. You can deploy the core stack with a single command or add the monitoring stack with a second command."*
*(If showing Docker:)* *"Once deployed, you get this microservice cluster—backends, Gateway, Redis, LocalStack—all as independent containers. Docker is the only requirement to get the whole environment live."*

**Transition to Part 3:** *"With the stack running, the next question is: how do we see what’s happening inside it? That’s where observability comes in."*

---

## Part 3 — Observability & Real-Time Testing — ~1.5 min

**Show:** Grafana http://localhost:3001 → **Metrics:** dashboard or Explore → Prometheus (e.g. request rate, latency, error rate) → **Logs:** Explore, Loki: `{service="gateway"} | json` or `{service="order"} | json` (Part 1 traffic) → `{service="audit"} | json`. Then terminal: `cd integration_tests && ./run_all_tests.sh inventory` → back to Loki (new logs, 422s).

**Say:** *"We have both metrics and logs in Grafana. Prometheus gives us request rate, latency, and error rate per service. Loki gives us structured JSON logs with Request IDs—we can trace one user action through every service. Security events like login and token creation are in the audit log, separate from app logs."*
*(When starting the test:)* *"To see resilience under load, I'm running the integration suite. You'll see metrics and logs update—including 422 validation errors in the logs. Those are expected. This real-time visibility is what makes the system production-ready."*

---

## Part 4 — Engineering Standards & Docs — ~1 min

**Show:** (1) **Terminal** — User Service unit test run: scroll to the coverage report (e.g. 218 passed, ~96%) so they see the details; or (2) **GitHub/IDE** — **docs/** folder (runbooks, design docs). *(Optional:)* Run `cd services/user_service && pytest --cov=src` live if you prefer; otherwise use an existing run or just **docs/**.

**Say:** *"Engineering discipline is core to this project. Here are the User Service unit tests and coverage—all runnable from the repo. At the architectural level, I've implemented Rate Limiting, Circuit Breakers, and IP Blocking at the Gateway to ensure system resilience. Runbooks and design docs are in docs/."*

---

## Part 5 — Close — ~30 sec

**Show:** **Repo root** (GitHub or IDE) or the **app** (e.g. localhost:3000)—so they end on “everything you’ve seen is in the repo” with the repo or the product on screen.

**Say:** *"To wrap up: this is a complete engineering ecosystem—scalable, observable, and easy to deploy. Everything you've seen is in the repo. Thanks for watching!"*
