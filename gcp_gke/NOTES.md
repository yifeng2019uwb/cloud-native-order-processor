# gcp-gke Notes

Discussion date: 2026-04-22

## What this package is

Deploy cloud-native-order-processor to GKE as an alternative environment alongside the existing Docker VM and EKS setup. Treat it like A/B testing across cloud providers / deployment models. No changes to existing docker/, kubernetes/, or terraform/ packages.

## Decisions

- **IaC tool**: Pulumi (Go) — clean start, separate from existing AWS Terraform
- **GKE mode**: Standard (NOT Autopilot — Autopilot blocks privileged pods, breaks eBPF monitoring)
- **Node OS**: Ubuntu node pool (required for eBPF BTF support)
- **DB**: LocalStack inside the cluster — same as Docker local setup, no cloud DB needed
- **K8s manifests**: reuse/adapt from existing kubernetes/prod/, no changes to originals
- **Image registry**: Artifact Registry (`us-west1-docker.pkg.dev`) NOT GCR (`gcr.io`) — GKE Ubuntu nodes with containerd generate malformed token scopes when pulling from GCR-backed-by-AR, causing 403s regardless of IAM. AR directly works cleanly.
- **Machine type**: `e2-standard-2` — e2-medium (4GB) too tight, Python services OOMKilled; e2-small only ~17m CPU left after GKE system pods
- **IAM + AR repo**: managed by Pulumi (`pulumi_registry.go`) — not manual gcloud commands
- **Multi-region strategy**: single Pulumi stack manages all clusters; clusters defined as a Go slice in `config.go`; one AR registry shared across all regions; `deploy.sh all` reads cluster list from Pulumi outputs and deploys to every cluster automatically

## Design principle: scale easily, implement incrementally

Not everything will be built at once. Each piece should work standalone and extend naturally — adding a region, a service, or an eBPF rule should be a small delta, not a rewrite. Build the first slice correctly; the rest follows the same pattern.

## Multi-region design

Each region gets its own GKE cluster. Services run simultaneously across regions — different network latency profiles, different geo, same workload — giving the eBPF project varied environments to monitor.

### Single-stack, clusters-as-code

One Pulumi stack (`gke-dev`) manages everything: SA, AR registry, and all clusters. Clusters are defined as a Go slice in `config.go` — adding a region is one line of code, not a new stack.

```go
// config.go
var clusters = []ClusterConfig{
    {Name: "order-processor-cluster-us-west1", Region: "us-west1", Zone: "us-west1-a"},
    {Name: "order-processor-cluster-us-east1", Region: "us-east1", Zone: "us-east1-b"},
}
```

`pulumi up` creates all clusters in the list. Pulumi exports `clusterRegions` (string array) plus `clusterName-<region>` and `clusterZone-<region>` per cluster.

**Why single stack over stack-per-region:**
- SA and AR registry are project-level resources — only one should own them; stack-per-region causes 409 conflicts on the second stack
- One `pulumi up` / `pulumi destroy` manages everything consistently
- Simpler: no `pulumi stack select` before every operation

### deploy.sh reads from Pulumi — no hardcoded cluster list

`deploy.sh all` reads `clusterRegions` from Pulumi outputs and iterates:
```bash
regions=$(pulumi stack output clusterRegions --json | jq -r '.[]')
for region in $regions; do
    cluster=$(pulumi stack output "clusterName-${region}")
    zone=$(pulumi stack output "clusterZone-${region}")
    gcloud container clusters get-credentials "$cluster" --zone "$zone"
    # deploy infra + app to this cluster
done
```

Adding a new region: update `clusters` in `config.go` → `pulumi up` → `deploy.sh all` picks it up automatically.

Each cluster gets its own eBPF DaemonSet — `deploy.sh daemonset` similarly loops over all clusters. DaemonSet manifest uses `$REGION` env var so `WorkloadMeta.Region` is tagged correctly per cluster.

## Approach

Start small — get Pulumi to create a GKE cluster in one region and deploy one service successfully before adding more complexity. The Kustomize vs flat-copy question for manifests deferred until after first deploy.

## Open items (check after first GKE node is up)

- `kubectl describe node <node> | grep "Kernel Version"` — for eBPF compatibility
- `ls /sys/kernel/btf/vmlinux` on the node — for CO-RE support

## Setup & Deploy Steps

### Step 1 — One-time per machine (run once, not per region)

```bash
cd gcp_gke/
./setup.sh all          # gcloud auth + enable GCP APIs + pulumi login
```

Or individual steps if needed:
```bash
./setup.sh tools        # check required tools (gcloud, pulumi, kubectl, docker, go)
./setup.sh gcp          # gcloud auth + set project + enable APIs
./setup.sh pulumi       # go mod tidy + pulumi login
```

### Step 2 — Build and push Docker images (once, or when service code changes)

Images are shared across all regions — only one registry (`us-west1-docker.pkg.dev`).

```bash
cd gcp_gke/
./deploy.sh build       # builds all 5 service images and pushes to Artifact Registry
```

### Step 3 — Add a region (edit code, then deploy)

To add a new region, add one entry to `clusters` in `config.go`:
```go
var clusters = []ClusterConfig{
    {Name: "order-processor-cluster-us-west1", Region: "us-west1", Zone: "us-west1-a"},
    {Name: "order-processor-cluster-us-east1", Region: "us-east1", Zone: "us-east1-b"}, // new
}
```

Then:
```bash
cd gcp_gke/
pulumi up               # creates the new cluster (existing clusters unchanged)
./deploy.sh all         # auto-reads cluster list from Pulumi, deploys to every cluster
```

### Step 4 — Deploy eBPF DaemonSet to all clusters

```bash
# First build and push the EDR image (from ebpf-edr-demo/):
make docker-push

# Then deploy DaemonSet to all clusters:
cd gcp_gke/
./deploy.sh daemonset   # loops over all clusters, skips gracefully if image not found
```

### Teardown

```bash
cd gcp_gke/
./cleanup.sh            # deletes K8s namespace + resources in currently connected cluster
pulumi destroy          # destroys all clusters + SA + AR repo
```

## Troubleshooting

### Pulumi state out of sync (409 Already Exists)

Happens when a `pulumi up` or `pulumi destroy` was interrupted, leaving GCP resources that Pulumi no longer tracks.

```bash
pulumi refresh --yes    # sync state; clears pending operations

# If resources still exist in GCP but not in Pulumi state, import them:
pulumi import "gcp:container/cluster:Cluster" "order-processor-cluster-us-west1" \
    "projects/ebpfagent/locations/us-west1-a/clusters/order-processor-cluster-us-west1" --yes

pulumi import "gcp:container/cluster:Cluster" "order-processor-cluster-us-east1" \
    "projects/ebpfagent/locations/us-east1-b/clusters/order-processor-cluster-us-east1" --yes

pulumi import "gcp:artifactregistry/repository:Repository" "order-processor-registry" \
    "projects/ebpfagent/locations/us-west1/repositories/order-processor" --yes

pulumi up --yes
```

### Stale stack from old stack-per-region approach

If a stale `gke-us-east1` or `gke-us-west1` stack exists from a previous approach, destroy and remove it:

```bash
pulumi stack select gke-us-east1
pulumi destroy --yes
pulumi stack rm gke-us-east1
```

### ImagePullBackOff 403 on GCR images

Do NOT use `gcr.io` images on GKE Ubuntu nodes — containerd generates malformed token scopes causing 403s.
Use Artifact Registry (`us-west1-docker.pkg.dev/ebpfagent/order-processor/...`) instead.
IAM role `roles/artifactregistry.reader` is granted to the node SA by Pulumi.

### ErrImagePull: no match for platform in manifest

Building on Apple Silicon (arm64) produces arm64 images. GKE nodes are amd64.
`deploy.sh build` uses `--platform linux/amd64` to cross-compile correctly.

### LocalStack OOMKilled

LocalStack needs >256MB RAM. e2-small cannot fit it alongside GKE system pods (~1.4GB overhead).
Use `e2-medium` (set in `config.go` → `machineType`).

### CPU scheduling failures (Insufficient cpu)

e2-medium allocates only ~940m CPU; GKE system pods consume ~850m leaving ~90m for workloads.
All service CPU requests are set low (10-15m) intentionally — no real traffic in this demo setup.

### HPA oscillation on background-sync services

Symptom: HPA oscillates (e.g. 3→1→3) with no external traffic; avg CPU shows low (3%) but replicas won't stabilize at 1.

Root cause: CPU request is too low relative to the sync spike. HPA measures utilization as `actual / request`. If request=75m and sync peaks at 77m, utilization = 102% > 70% threshold → scale-up. After scale-up to 3, avg drops → scales back to 1 → sync hits 102% again → repeat.

The default scale-down stabilization window is 5 minutes. If the sync interval ≈ stabilization window, HPA can never scale down — every sync spike resets the window.

Fix: raise CPU request so the peak stays below the HPA threshold.
```
Formula: cpu request ≥ peak_usage / hpa_threshold
Example: peak=77m, threshold=70% → request ≥ 77/0.70 = 110m
inventory-service: raised cpu request 75m → 100m, limit 150m → 200m
```

### Gateway Redis shows degraded / `"redis": false`

The Go gateway reads `REDIS_HOST`, but the configmap only sets `REDIS_ENDPOINT` (used by Python services).
Add `REDIS_HOST: "redis"` to `kubernetes/configmap.yaml`, then apply:

```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl rollout restart deployment/gateway -n order-processor
kubectl rollout status deployment/gateway -n order-processor --timeout=60s
```

### Apply deployment changes (without full redeploy)

To apply resource/config changes to a specific deployment without restarting unchanged services:

```bash
kubectl apply -f gcp_gke/kubernetes/deployment.yaml
```

All deployments are evaluated; only those with actual changes will rolling-update. Unchanged ones show `unchanged` and do not restart.


## Related

- eBPF expansion design: `ebpf-edr-demo/gke-expansion-design.md`
