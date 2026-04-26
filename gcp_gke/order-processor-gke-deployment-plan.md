# GKE Deployment Plan — cloud-native-order-processor

> Status: **Complete** — all services deployed, all integration tests passing.
> Discussion date: 2026-04-22 | Completed: 2026-04-24
> Related: `ebpf-edr-demo/gke-expansion-design.md`

---

## Goal

Deploy cloud-native-order-processor on GKE Standard as a second workload environment
alongside the existing Docker VM. Primary motivations:

1. Practice K8s-based deployment with HPA (auto-scaling simulation)
2. Provide a K8s workload for the eBPF EDR agent to monitor (hybrid demo)
3. Run integration tests from local laptop against GKE gateway to simulate external traffic

---

## Why This Project (not healthcare-ai)

- K8s manifests already exist (`kubernetes/prod/`) — not starting from scratch
- Integration tests are stable and cover all 8 services
- Existing detection rules in the eBPF agent are tuned for these services
- healthcare-ai is in active development — GKE complexity deferred until it stabilizes

---

## Target Architecture

```
GKE Standard cluster (single node, Ubuntu node pool)
  namespace: order-processor

  Deployments (multiple replicas each, HPA-managed):
    gateway           ← exposed externally (LoadBalancer or NodePort)
    auth_service
    user_service
    inventory_service
    order_service
    insights_service
    redis

  Deployment (single replica, ephemeral for dev):
    localstack        ← DynamoDB emulation, port 4566

  eBPF DaemonSet (privileged):
    edr-monitor       ← monitors all pods on this node
```

---

## Existing K8s Manifests: What Needs Adapting

The existing `kubernetes/prod/` manifests are AWS/EKS-oriented. Changes needed for GKE:

| Item | Current (EKS) | GKE target |
|------|--------------|------------|
| Image registry | ECR (`imagePullSecrets: ecr-registry-secret`) | GCR or Artifact Registry |
| DynamoDB backend | Real AWS DynamoDB | LocalStack (same as Docker local) |
| Load balancer annotations | `aws-load-balancer-type: nlb` | Remove or replace with GCP annotations |
| IAM / credentials | IRSA (`AWS_WEB_IDENTITY_TOKEN_FILE`) | `ENVIRONMENT=local` + dummy creds |
| Secrets | AWS Secrets Manager references | K8s Secrets or GCP Secret Manager |
| Storage class | EBS (implied) | GCP standard PD (if needed) |

No application code changes required — all differences are in manifest env vars and infra config.

---

## Database Connection: No Code Change Required

The `DynamoDBManager` in `services/common/src/data/database/dynamodb_connection.py`
already has a 3-way branch:

```python
if ENVIRONMENT == "local":
    # dummy creds + AWS_ENDPOINT_URL → LocalStack
elif AWS_WEB_IDENTITY_TOKEN_FILE:
    # IRSA (EKS native)
elif AWS_ROLE_ARN:
    # STS assume_role
```

For GKE dev deployment, use the `local` branch:
- `ENVIRONMENT=local`
- `AWS_ENDPOINT_URL=http://localstack:4566`
- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`

In K8s, `http://localstack:4566` resolves via the K8s Service named `localstack`
within the same namespace — identical to Docker Compose hostname resolution.

---

## LocalStack in K8s

LocalStack runs as a standard Deployment (ephemeral, data resets on pod restart).
This matches the Docker Compose local behavior — integration tests re-seed data on each run.

Required K8s resources:
- `Deployment`: `localstack/localstack:3.8.1`, port 4566 (same image as Docker Compose)
- `Service`: ClusterIP, named `localstack`, port 4566
- Health check: `GET http://localhost:4566/_localstack/health`

No StatefulSet or PersistentVolumeClaim needed for dev/demo environment.

---

## Scaling

CPU-based HPA is deployed for all 5 services (`kubernetes/hpa.yaml`). Integration tests drive real CPU load to trigger scale-up.

| Service | minReplicas | maxReplicas | threshold |
|---------|------------|-------------|-----------|
| user-service | 1 | 3 | 70% |
| inventory-service | 1 | 3 | 70% |
| order-service | 1 | 2 | 70% |
| auth-service | 1 | 2 | 70% |
| gateway | 1 | 2 | 70% |

Cluster autoscaler: node pool min 1 / max 3 (Pulumi `NodePoolAutoscalingArgs`). Triggered by Pending pods, not CPU%.

**HPA tuning note:** inventory-service CPU request raised to 100m (limit 200m) — the CoinGecko sync peaks at ~77m, which was 102% of the original 75m request, causing false HPA scale-ups with no real traffic.

To manually trigger scale-up for eBPF validation:
```bash
for svc in auth-service user-service inventory-service order-service; do
  kubectl scale deployment $svc --replicas=3 -n order-processor
done
# observe eBPF alerts, then scale back
for svc in auth-service user-service inventory-service order-service; do
  kubectl scale deployment $svc --replicas=1 -n order-processor
done
```

---

## Integration Test Validation from Local Laptop

With gateway exposed via GKE LoadBalancer, integration tests run from the local laptop
against the GKE IP — same tests, different target URL.

```bash
GATEWAY_URL=http://<gke-external-ip>:8080 ./integration_tests/run-it.sh all
```

This exercises:
- Normal service traffic (should produce zero CRITICAL/HIGH eBPF alerts)
- External traffic → gateway → internal services (validates lsm-connect rules)
- The `inventory_service` → CoinGecko path (should produce LOW audit log only)

Same validation methodology as the Docker VM — reuse existing test suite.

---

## Open Research Items

| # | Question | How to answer | Status |
|---|----------|---------------|--------|
| R1 | GKE Ubuntu node kernel version | `kubectl describe node \| grep "Kernel Version"` | Pending — check before eBPF work |
| R2 | BTF available on GKE Ubuntu node | SSH to node: `ls /sys/kernel/btf/vmlinux` | Pending — check before eBPF work |

---

## Scope Breakdown

| Item | Description | Status |
|------|-------------|--------|
| GKE cluster | GKE Standard, Ubuntu node pool, e2-medium | Done |
| Image registry | Artifact Registry `us-west1-docker.pkg.dev/ebpfagent/order-processor` | Done |
| Base manifests | Adapted from `kubernetes/prod/` — new `gcp_gke/kubernetes/` dir | Done |
| LocalStack manifest | Deployment + ClusterIP Service, init hook for DynamoDB table creation | Done |
| ConfigMap | `ENVIRONMENT=local`, `AWS_ENDPOINT_URL`, `REDIS_HOST`, table names | Done |
| Secrets | JWT secret (32+ chars) via `kubectl create secret` | Done |
| HPA | CPU-based autoscaling for all 5 services | Done |
| Cluster autoscaler | Node pool min 1 / max 3 via Pulumi | Done |
| Gateway exposure | LoadBalancer Service, external IP: `136.109.215.94:8080` | Done |
| Integration test target | `GATEWAY_HOST=136.109.215.94` in `config/constants.py` | Done |
| All integration tests | auth ✓, inventory ✓, order ✓, user ✓ | Done |
| Multi-region Pulumi refactor | Reusable `deployCluster()` function, region as config var, `REGION` env var in DaemonSet | Planned |

---

## Decisions Made

- **Machine type**: `e2-medium` — e2-small insufficient for LocalStack + GKE system pods
- **Image registry**: Artifact Registry (not GCR) — GKE Ubuntu containerd generates malformed token scopes for GCR causing 403s
- **Manifests**: separate `gcp_gke/kubernetes/` directory (not overlays) — simpler for a standalone demo environment
- **Multi-region**: each GCP region = separate Pulumi stack (`pulumi stack init us-east1`), same Go code, different config. DaemonSet injects `REGION` env var per cluster so eBPF `WorkloadIdentity.Region` is tagged correctly.
