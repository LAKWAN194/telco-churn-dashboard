# MLOps primer

The churn model today is a file (`models/artifacts/churn_model.joblib`) produced by
a script. "Production MLOps" means you can answer, at any time: which model is
serving, how it was trained, whether the data it sees has changed, and how a new
model replaces it safely.

## MLflow: tracking and the registry

- **Tracking** records each training run: parameters, metrics, and artifacts (the
  model file, plots, the threshold). Runs are grouped into experiments, so you can
  compare a new run with the one serving now.
- The **model registry** gives each registered model numbered versions. An
  **alias** such as `champion` points at the version that should serve. Promoting a
  model means moving the alias, and rolling back means moving it back.
- The serving code loads "the version with alias `champion`", not a file path.

`docker compose --profile mlops up` starts a local MLflow server (UI at
<http://localhost:8285>). What gets logged, and what makes a new version good
enough to promote, is ADR-007.

## Drift

A model learns from a snapshot of the past. When the customers it scores start to
look different (new price plans, a competitor's promotion), its scores become less
trustworthy, often before anyone notices the accuracy drop.

The **population stability index (PSI)** compares a feature's distribution now with
its distribution in the training data:

```
PSI = Σ over bins (actual% − expected%) × ln(actual% / expected%)
```

`expected%` is each bin's share in the reference data and `actual%` its share now.
A common rule of thumb reads below 0.1 as stable, 0.1–0.25 as worth watching, and
above 0.25 as a significant shift. These are conventions, not laws; justify the
thresholds you pick. Decisions to make (ADR-008): which features, how to bin (for
example deciles of the reference data), what to do with empty bins, how often to
compute it, and what an alert triggers.

## Monitoring

- **Prometheus** scrapes numbers from each service's metrics endpoint every few
  seconds and stores them as time series. The USSD gateway already exposes
  `/actuator/prometheus`.
- **Grafana** draws dashboards and raises alerts from those series.
- `docker compose --profile monitoring up` starts both (Prometheus at
  <http://localhost:8286>, Grafana at <http://localhost:8287>).

Worth a panel each: request latency (p95), error rate, score distribution over time,
PSI per feature, offers sent and accepted, and holdout versus offered retention.

## Kubernetes on a laptop: kind and Helm

- **kind** ("Kubernetes in Docker") runs a real cluster as Docker containers.
- **Helm** packages the deployment as a **chart**: templates for each Kubernetes
  object, plus a `values.yaml` of settings. The skeleton's chart is in
  `deploy/helm/telco-retention/`.
- `helm lint` checks a chart; `helm template` renders it to plain YAML, so you can
  read exactly what would be applied.

The point is not that a churn model needs Kubernetes. Telco platform teams
(Axiata Digital Labs, Sysco LABS SRE) run on it, and being able to explain a
Deployment, a Service and a readiness probe is the skill being shown.
