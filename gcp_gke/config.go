package main

// GCP project
const (
	projectID        = "ebpfagent"
	serviceAccountID = "order-processor-sa"
)

// Cluster
const (
	clusterName = "order-processor-cluster"
	namespace   = "order-processor"
)

// ClusterConfig holds per-region deployment parameters.
type ClusterConfig struct {
	Name   string // e.g. "order-processor-cluster-us-west1"
	Region string // e.g. "us-west1"
	Zone   string // e.g. "us-west1-a"
}

// clusters is the list of GKE clusters to deploy.
// Add a new entry here to deploy to a new region — pulumi up + deploy.sh all handle the rest.
var clusters = []ClusterConfig{
	{Name: "order-processor-cluster-us-west1", Region: "us-west1", Zone: "us-west1-a"},
	{Name: "order-processor-cluster-us-east1", Region: "us-east1", Zone: "us-east1-b"},
	// {Name: "order-processor-cluster-europe-west1",    Region: "europe-west1",    Zone: "europe-west1-b"},
	// {Name: "order-processor-cluster-asia-northeast1", Region: "asia-northeast1", Zone: "asia-northeast1-a"},
}

// Node pool
const (
	machineType = "e2-standard-2" // 8GB RAM; e2-medium (4GB) too tight — Python services OOMKilled at 128Mi limit
	// NOTE: set to UBUNTU_CONTAINERD as a simplification for this project since the goal is eBPF monitoring.
	// In production, deployment config should not be changed to accommodate the eBPF agent — the agent should adapt to the environment instead.
	// COS_CONTAINERD (GKE default) requires manual kernel header mounting for BTF; may revisit if agent gains COS support later.
	imageType  = "UBUNTU_CONTAINERD"
	oauthScope = "https://www.googleapis.com/auth/cloud-platform"
)

// Service names
const (
	svcGateway    = "gateway"
	svcAuth       = "auth-service"
	svcUser       = "user-service"
	svcInventory  = "inventory-service"
	svcOrder      = "order-service"
	svcRedis      = "redis"
	svcLocalstack = "localstack"
)

// Service ports — must match kubernetes/deployment.yaml
const (
	portGateway    = 8080
	portAuth       = 8003
	portUser       = 8000
	portInventory  = 8001
	portOrder      = 8002
	portRedis      = 6379
	portLocalstack = 4566
)

// Artifact Registry
const (
	arRegion     = "us-west1"
	arRepository = "order-processor"
	arEbpfRepo   = "ebpf-edr"
)

// Container images — Artifact Registry (us-west1) avoids GCR→AR routing issues on GKE Ubuntu nodes
const (
	imagePrefix     = "us-west1-docker.pkg.dev/" + projectID + "/order-processor/"
	imageGateway    = imagePrefix + "gateway:latest"
	imageAuth       = imagePrefix + "auth-service:latest"
	imageUser       = imagePrefix + "user-service:latest"
	imageInventory  = imagePrefix + "inventory-service:latest"
	imageOrder      = imagePrefix + "order-service:latest"
	imageRedis      = "redis:7-alpine"
	imageLocalstack = "localstack/localstack:3.8.1"
	imageEbpfEdr    = "us-west1-docker.pkg.dev/" + projectID + "/" + arEbpfRepo + "/ebpf-edr:latest"
)
