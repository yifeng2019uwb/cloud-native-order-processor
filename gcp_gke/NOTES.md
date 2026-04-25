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
- **Machine type**: `e2-medium` — e2-small has only ~17m CPU left after GKE system pods; LocalStack needs >256MB RAM
- **IAM + AR repo**: managed by Pulumi (`pulumi_registry.go`) — not manual gcloud commands

## Design principle: scale easily, implement incrementally

Not everything will be built at once. Each piece should work standalone and extend naturally — adding a region, a service, or an eBPF rule should be a small delta, not a rewrite. Build the first slice correctly; the rest follows the same pattern.

## Multi-region goal

Design the Pulumi program to support deploying to multiple GCP regions. Each region gets its own GKE cluster. Services can run in different regions simultaneously — this gives the eBPF project more varied environments to monitor (different network latency profiles, different geo, same workload).

Start with one region first. Region should be a Pulumi config variable so adding a second region is just a config change, not a code change.

Each cluster gets its own eBPF DaemonSet — one agent per node, region-tagged alerts.

## Approach

Start small — get Pulumi to create a GKE cluster in one region and deploy one service successfully before adding more complexity. The Kustomize vs flat-copy question for manifests deferred until after first deploy.

## Open items (check after first GKE node is up)

- `kubectl describe node <node> | grep "Kernel Version"` — for eBPF compatibility
- `ls /sys/kernel/btf/vmlinux` on the node — for CO-RE support

## Setup & Deploy Steps

### One-time setup (new machine or new GCP project)

```bash
cd gcp_gke/
./setup.sh all          # gcloud auth + enable APIs + pulumi login + stack init
```

Or run individual steps:
```bash
./setup.sh tools        # check required tools (gcloud, pulumi, kubectl, docker, go)
./setup.sh gcp          # set GCP project + enable APIs
./setup.sh pulumi       # go mod tidy + pulumi login + stack init + config
./setup.sh kubectl      # connect kubectl to existing cluster
```

### Provision GKE cluster (Pulumi)

```bash
cd gcp_gke/
pulumi up               # create cluster + node pool + service account
```

After cluster is up, connect kubectl:
```bash
./setup.sh kubectl
```

### Build and push Docker images to Artifact Registry

```bash
cd gcp_gke/
./deploy.sh build       # builds all 5 service images and pushes to us-west1-docker.pkg.dev
```

### Deploy services to GKE

```bash
cd gcp_gke/
./deploy.sh all         # namespace + secret + configmap + localstack + redis + services + deployments
```

Or deploy in stages:
```bash
./deploy.sh infra       # namespace + secret + configmap only
./deploy.sh app         # localstack + redis + services + deployments
./deploy.sh status      # check pod/service status
```

### Teardown

```bash
cd gcp_gke/
./cleanup.sh            # delete namespace + all resources inside it
pulumi destroy          # destroy GKE cluster + node pool + AR repo + IAM
```

## Troubleshooting

### Pulumi state out of sync (409 Already Exists)

Happens when a `pulumi up` or `pulumi destroy` was interrupted, leaving GCP resources that Pulumi no longer tracks.

```bash
pulumi refresh --yes    # sync state; clears pending operations

# If resources still exist in GCP but not in Pulumi state, import them:
pulumi import "gcp:container/cluster:Cluster" "order-processor-cluster" \
    "projects/ebpfagent/locations/us-west1-a/clusters/order-processor-cluster" --yes

pulumi import "gcp:artifactregistry/repository:Repository" "order-processor-registry" \
    "projects/ebpfagent/locations/us-west1/repositories/order-processor" --yes

pulumi up --yes
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
