# Runbook

## Prerequisites

| Tool | Version | For |
| --- | --- | --- |
| Python 3.12, Node 22, Docker | as before | The existing project |
| JDK | 21 | The USSD gateway (`./mvnw` downloads Maven itself) |
| Android Studio, or the Android SDK with platform 36 | recent | The self-care app |
| kind, kubectl, Helm | recent | Week 5 deployment ([deploy/README.md](../../deploy/README.md)) |

## Ports

The existing defaults are unchanged: the database on 5432, the API on 8000 and the
dashboard on 5173 when run by hand. Everything new uses 82xx, so it can run next to
the other portfolio projects.

| Service | Port | Started by |
| --- | --- | --- |
| USSD gateway | 8280 | `--profile retention`, or `./mvnw spring-boot:run` |
| API in Docker | 8281 | `--profile apps` |
| Dashboard in Docker | 8284 | `--profile apps` |
| MLflow | 8285 | `--profile mlops` |
| Prometheus | 8286 | `--profile monitoring` |
| Grafana | 8287 | `--profile monitoring` |
| Redis | 6382 | `--profile retention` |
| Kafka API (Redpanda) | 19281 | `--profile retention` |

## Commands

```bash
docker compose up -d                                   # the database only, as before
docker compose --profile apps up -d --build            # plus the API and dashboard
docker compose --profile retention up -d --build       # Redis, Redpanda, USSD gateway
docker compose --profile mlops --profile monitoring up -d

cd ussd-gateway && ./mvnw verify                       # gateway tests (needs Docker)
cd selfcare-app && ./gradlew assembleDebug testDebugUnitTest lintDebug
helm lint deploy/helm/telco-retention
```

## Checking it works

```bash
curl localhost:8280/actuator/health          # USSD gateway, including Redis
curl localhost:8280/actuator/prometheus      # its metrics, as Prometheus sees them
curl localhost:8281/health                   # the API in Docker
open http://localhost:8287                   # Grafana (anonymous viewer, admin/admin to edit)
```
