# Demo Runbook — Cloud-Native Order Processor

**Purpose:** Presentation script and runbook for the 5-minute demo. **Everything is already deployed**; you will show the running system and explain how to use `deploy.sh` for deployment.

**Total time:** ~5 minutes

| Part | Content | Time |
|------|---------|------|
| 1 | Business flow (live UI) | ~1.5 min |
| 2 | Architecture quick tour + how to use deploy.sh | ~1 min |
| 3 | Metrics & logs (Grafana) | ~1 min |
| 4 | Engineering quality (tests, coverage, docs) | ~1 min |
| 5 | Close | ~30 sec |

---

## Part 1 — Business flow (live UI) — ~1.5 min

**What you do:** Walk through the app as a user. Use the **exact wording** below or adapt in your own words.

---

**Open the app**
- Open the browser to **http://localhost:3000**.
- Say: *"This is the Cloud-Native Order Processor — a trading-style demo. The UI is React; every API call goes through our API gateway. I'll walk through the main user flow."*

**Register and log in**
- Click **Register** (or use a pre-created account and say: *"I'll use an existing account."*).
- If registering: enter username and password, then submit. Then log in.
- Say: *"We just registered and logged in. The backend issues a JWT; the frontend stores it and sends it on every request. From here on, all actions are authenticated."*

**Deposit**
- Go to **Account** (or **Manage Balance**).
- Say: *"I'll add some balance so we can place an order."*
- Enter an amount (e.g. 1000), submit deposit.
- Say: *"Balance is updated. This goes through the gateway to the user service; the backend handles the transaction and locking."*

**Browse and place an order**
- Go to **Trading** (or **Trade assets**).
- Say: *"Here we can see available assets and prices from the inventory service."*
- Select an asset (e.g. BTC or USDC), choose **Buy**, enter a quantity, click through to submit.
- Show the order confirmation and success message.
- Say: *"Order is placed. The gateway validated the JWT, then routed to the order service; the order service coordinates with user and inventory for balance and execution."*

**Check balance / portfolio**
- Go to **Portfolio** (or **Account** for balance).
- Say: *"Portfolio shows total value, assets we own, and recent orders. We can see the order we just placed and the updated balances. That’s the full business flow: register, deposit, trade, and check results — all through a single gateway."*

---

## Part 2 — Architecture quick tour + how to use deploy.sh — ~1 min

**What you do:** Show the project structure **on GitHub** (repo in the browser), then show the deploy script usage and main commands. **You are not running deploy during the demo** — you are showing how someone would use it.

---

**Project structure via GitHub (30 sec)**
- Open your **GitHub repository** in the browser (e.g. `https://github.com/<your-org>/cloud-native-order-processor`).
- Say: *"I’ll show the layout on GitHub so you see exactly what’s in the repo."*
- On the repo root, point to the main folders:
  - **`frontend/`** — *"React UI; all API calls go through the gateway."*
  - **`gateway/`** — *"Go API gateway — single entry point, rate limiting, circuit breaker."*
  - **`services/`** — *"Five FastAPI backends: user, order, inventory, auth, insights. Auth validates JWTs; the gateway enforces that before forwarding."*
  - **`docker/`** — *"Compose files and the deploy script we use to run everything locally or with AWS."*
  - **`docs/`** — *"Design docs, runbooks, deployment guide."*
  - **`integration_tests/`** — *"Black-box tests against the gateway."*
  - Optionally: **`terraform/`** — *"Infrastructure as code for cloud or Kubernetes when we need it."*
- Say: *"So: Go gateway, five FastAPI services, React frontend, internal auth layer — and Terraform in the repo for infra. For local runs we use Docker and one deploy script."*

**How to use deploy.sh (30 sec)**
- Open `docker/deploy.sh` or a terminal where you can show the help.
- Run: `./docker/deploy.sh` (no args) to show the usage, or just point at the script and read from it.
- Say: *"Deployment is driven by this script. From the repo root you run it like this."*
- Then say (and optionally show the commands on a slide or in the runbook, without running them):
  - *"**Local full stack, no AWS:** `./docker/deploy.sh local deploy` — that brings up LocalStack for DynamoDB, Redis, and all services. You don’t need an AWS account."*
  - *"**Tear down:** `./docker/deploy.sh local destroy` — that stops and removes everything."*
  - *"**Monitoring stack:** `./docker/deploy.sh monitoring deploy` — that starts Grafana, Prometheus, Loki, and Promtail so we can look at metrics and logs. What I showed you earlier is from that stack."*
  - *"You can also deploy a single service, rebuild the frontend only, or check status — the script’s usage lists all options. Everything is documented in the repo’s README and the docker README."*

---

## Part 3 — Metrics & logs — ~1 min

**What you do:** Run **one integration test** (a validation test) so fresh log lines and errors appear. Then open Grafana and show metrics plus those logs — including validation/error entries — and explain audit vs normal logs.

---

**Run one integration test suite first (so we see traffic and errors in logs)**
- In a terminal, from the **repo root**:
  ```bash
  cd integration_tests && ./run_all_tests.sh inventory
  ```
  The inventory suite includes validation tests (e.g. invalid asset IDs → **422**). It generates gateway and inventory service logs (validation failures).
- **Alternative (auth/401):** To show auth-related logs instead:
  ```bash
  cd integration_tests && ./run_all_tests.sh auth
  ```
- Say: *"I’m running our integration test script — the **inventory** suite, which includes **validation** tests that trigger 422 responses. That way we’ll see real log lines and errors in the monitoring stack."*
- Wait for the test to finish (a few seconds). Then go to Grafana.

**Grafana and metrics (20 sec)**
- Open **http://localhost:3001** (Grafana). Log in (e.g. admin / admin123).
- Say: *"We run Prometheus for metrics, Loki for logs, and Grafana to view both."*
- Open a dashboard with **request rate, latency, or error rate** — or **Explore → Prometheus** and run one simple query.
- Say: *"Here we see request rate, latency, and errors. Each service exposes metrics; we use this for health and alerting."*

**Logs: show the test’s traffic and errors, then audit vs normal (40 sec)**
- In Grafana go to **Explore** and choose the **Loki** data source.
- Run: **`{service="inventory"} | json`** (or **`{service="gateway"} | json`** if you prefer).
  - Say: *"These are the **application logs** from the test we just ran. You see the requests and the **validation errors** — 422 responses for invalid asset IDs. So we can trace exactly what the gateway and services logged for each call."*
- Then run: **`{service="audit"} | json`**
  - Say: *"This is the **audit log** — separate from app logs. We keep security events here: login success and failure, logout, token creation. So we have a clear split: **audit for security**, and **service logs for validation and errors**."*
- Optionally run **`{service="order"} | json`** or **`{service="user"} | json`** and say: *"Same pattern for order or user service — validation and business errors show up here for debugging and traceability."*

---

## Part 4 — Engineering quality — ~1 min

**What you do:** Run a test script and show coverage (or test output). Then briefly mention integration tests, load tests, and docs.

---

**Run tests and show coverage**
- In a terminal, from the repo root or a service directory, run one of:
  - `cd gateway && ./dev.sh test`
  - `cd services/user_service && ./dev.sh test`
  - Or any single service you prefer.
- Say: *"We have unit tests across the gateway and all backend services. I’m running the test suite for [gateway / user service]."*
- When it finishes, point to the output: *"You see the test count and pass/fail. We also track **coverage** — the report is in the service’s htmlcov or coverage output. We use this to keep quality high and to refactor safely."*

**Integration tests, load tests, docs**
- Say: *"Beyond unit tests we have **integration tests** that hit the gateway and services end-to-end — they’re in `integration_tests/`. We have **load tests** in `integration_tests/load_tests/` for performance and rate limiting. And the repo has **full documentation**: architecture docs, API references, runbooks, a **backlog** and **daily work log** so the project’s status and decisions are visible. So: unit tests and coverage, integration and load tests, and docs — all in the repo."*

---

## Part 5 — Close — ~30 sec

**What you do:** One short closing message.

---

- Say: *"So in five minutes you’ve seen: the **business flow** in the UI, the **architecture** and how we **deploy** with the deploy script, **metrics and logs** in Grafana with a clear split between audit and app logs, and our **engineering practice** — tests, coverage, and docs. Everything — architecture, API references, design decisions, and how to run and deploy — is in **GitHub**. The README and the `docs/` folder are the entry points. Thanks."*

---

## Reference: GitHub repo (for Part 2)

Open this in the browser to show project structure:
- **Replace with your actual repo URL**, e.g. `https://github.com/<your-username-or-org>/cloud-native-order-processor`
- Stay on the **root** of the default branch (e.g. `main`) so the top-level folders are visible.

---

## Reference: deploy.sh commands (for your slides or notes)

**Assume you are at the repo root.**

| What | Command |
|------|---------|
| Local full stack (no AWS) | `./docker/deploy.sh local deploy` |
| Stop and remove local stack | `./docker/deploy.sh local destroy` |
| Deploy monitoring (Grafana, Prometheus, Loki) | `./docker/deploy.sh monitoring deploy` |
| Stop monitoring | `./docker/deploy.sh monitoring stop` |
| Rebuild frontend only | `./docker/deploy.sh local frontend rebuild` |
| Status of all services | `./docker/deploy.sh all status` |
| Help | `./docker/deploy.sh` (no arguments) |

**Note:** For AWS-backed deploy (real DynamoDB, etc.), the script supports service names like `auth`, `user`, `frontend` with action `deploy` — see `./docker/deploy.sh` and `docker/README.md`.

---

## Reference: URLs

| What | URL |
|------|-----|
| Frontend | http://localhost:3000 |
| API Gateway | http://localhost:8080 |
| Grafana | http://localhost:3001 (admin / admin123) |
| Prometheus | http://localhost:9090 |

**Loki (in Grafana):** Explore → Loki. Example queries: `{service="audit"} | json`, `{service="order"} | json`.

---

## 5-minute checklist (presenter)

- [ ] **Part 1:** Open frontend → Register or login → Deposit → Trading → Place one order → Portfolio/Account (show result).
- [ ] **Part 2:** Open **GitHub repo** in browser → show project structure (frontend, gateway, services, docker, docs, integration_tests); show deploy.sh and explain: local deploy, local destroy, monitoring deploy.
- [ ] **Part 3:** Grafana → dashboard or Prometheus query (rate/latency/errors) → Explore → Loki: audit log then order/user log; say “audit vs app logs.”
- [ ] **Part 4:** Run one test script (e.g. gateway or user_service), show output/coverage; mention integration tests, load tests, backlog, daily log, docs.
- [ ] **Part 5:** Closing line: everything is in GitHub — architecture, APIs, deploy, docs.
