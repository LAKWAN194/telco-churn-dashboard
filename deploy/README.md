# Deploying to a local Kubernetes cluster

Runs the API, dashboard, USSD gateway, Redis and PostgreSQL on
[kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker) with the Helm chart in
`helm/telco-retention/`. Week 5 of the retention-loop roadmap adds the rest of the loop.

## Prerequisites

`docker`, `kind`, `kubectl` and `helm` (version 3 or 4).

## Steps

```bash
# 1. Create the cluster
kind create cluster --name telco --config deploy/kind/cluster.yaml

# 2. Build the images and load them into the cluster (kind cannot see your local images)
docker build -f backend/Dockerfile -t telco/api:dev .
docker build --build-arg VITE_API_URL=http://localhost:8281 -t telco/dashboard:dev frontend
docker build -t telco/ussd-gateway:dev ussd-gateway
kind load docker-image telco/api:dev telco/dashboard:dev telco/ussd-gateway:dev --name telco

# 3. Install
helm install telco deploy/helm/telco-retention
kubectl get pods --watch

# 4. Reach it
kubectl port-forward svc/telco-dashboard 8284:80
```

## Checking the chart without a cluster

```bash
helm lint deploy/helm/telco-retention
helm template telco deploy/helm/telco-retention | less     # the exact YAML Helm would apply
```

## Clean up

```bash
helm uninstall telco
kind delete cluster --name telco
```

## Not done yet (week 5)

- How the trained model reaches the API pod (MLflow registry, a volume, or an init container)
- Loading the database (a Job that runs `pipeline/ingest.py`)
- Redpanda, MLflow, Prometheus and Grafana in the cluster
- An Ingress instead of port-forwarding
