# Prometheus Stack Deployment

This guide explains how to deploy the Prometheus monitoring stack (Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics) in your Kubernetes cluster using Helm.

## Prerequisites
- [Helm](https://helm.sh/docs/intro/install/) installed
- `kubectl` configured for your cluster

## 1. Add the Prometheus Community Helm Repo
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

## 2. Install the kube-prometheus-stack
Create a dedicated namespace and install the stack:
```bash
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```
This will deploy:
- Prometheus (metrics collection)
- Alertmanager (alert routing)
- Grafana (dashboards)
- node-exporter (node metrics)
- kube-state-metrics (K8s resource metrics)

## 3. Access Grafana Dashboard
Port-forward Grafana to your local machine:
```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```
Then open [http://localhost:3000](http://localhost:3000) in your browser.

**Default login:**
- User: `admin`
- Password: (get with)
  ```bash
  kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
  ```

## 4. Access Prometheus UI
```bash
kubectl port-forward svc/monitoring-kube-prometheus-stack-prometheus -n monitoring 9090:9090
```
Then open [http://localhost:9090](http://localhost:9090).

## 5. Next Steps
- Explore built-in dashboards in Grafana.
- Add custom dashboards or alerts as needed.
- (Optional) Configure persistent storage, external access, or custom scrape configs in `monitoring/prometheus/values.yaml`.