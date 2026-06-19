# Telco Customer Churn Dashboard

An end-to-end ML system that predicts customer churn using the IBM Telco dataset.

## Stack
- Python, pandas, scikit-learn, XGBoost
- FastAPI + PostgreSQL
- React (frontend, in progress)

## Project Structure
- `pipeline/` — data ingestion and preprocessing
- `models/` — training scripts and serialized artifacts
- `backend/` — FastAPI REST API
- `frontend/` — React dashboard
- `db/` — PostgreSQL schema

# Setup

## Database Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Configure environment variables
```bash
cp .env.example .env
```

### 2. Start the database
```bash
docker compose up -d
```

To view startup logs:
```bash
docker compose logs db
```

### 3. Verify it's running
```bash
docker compose ps
docker compose exec db psql -U postgres -d telco_churn -c "\dt"
```
You should see the `customers` and `predictions` tables listed.

### 4. Stop or reset
```bash
docker compose stop        # stop, keep data
docker compose down        # stop and remove container, keep data
docker compose down -v     # full reset — deletes all data
```