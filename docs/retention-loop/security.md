# Security checklist

Work through this in week 5, and design with it from week 2.

## USSD and SMS

- [ ] A session ID from the platform cannot be guessed or reused to act as another subscriber
- [ ] Menu input is validated: length, allowed characters, unexpected values
- [ ] Callback endpoints authenticate the platform (in the simulator, a shared secret; Ideamart uses an application ID and password)

## OTP and login

- [ ] Codes are random from a secure source, short-lived, and stored hashed
- [ ] Attempts are limited and lock-outs expire
- [ ] Requests are rate-limited per number and per IP, so the SMS budget cannot be drained
- [ ] Responses do not reveal whether a number is registered

## Carrier billing

- [ ] A debit needs an authenticated, confirmed user action (rule 4 in [domain/telco-apis.md](domain/telco-apis.md))
- [ ] Every debit is logged with who, what, when, how much and its `externalTrxId`
- [ ] Retries reuse the same `externalTrxId`

## Data

- [ ] Phone numbers are masked in logs and dashboards
- [ ] Simulated data only; no real subscriber data anywhere in the repository
- [ ] Secrets (database password, Grafana password) come from `.env` locally and Kubernetes Secrets in the cluster, never from the repository

## Cluster

- [ ] Containers run as non-root users (the Dockerfiles create one)
- [ ] Resource limits are set for every container (see `values.yaml`)
- [ ] The default Postgres password in `values.yaml` is replaced for anything beyond a laptop

## Findings

| Date | Finding | Severity | Fix | Test |
| --- | --- | --- | --- | --- |
| | | | | |
