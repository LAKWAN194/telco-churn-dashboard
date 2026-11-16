# Roadmap

Five weeks. **Week 1 runs now**, alongside exams, until 15 November 2026: it makes
the existing project interview-proof. The research plan puts weeks 2–5 after the
Kapruka agent, "if time allows", so they have no fixed dates. Fit them in where the
plan leaves room, and do not let them delay the payment switch or the agent.

ADR numbers refer to [adr/README.md](adr/README.md).

## Week 0: skeleton (done, on branch `p2/retention-loop`)

- [x] `ussd-gateway/`: Spring Boot 4.1 WebFlux with reactive Redis, Prometheus metrics, a Testcontainers test, and an ArchUnit rule keeping the menu kernel pure
- [x] `selfcare-app/`: Jetpack Compose app that builds, with a unit test
- [x] Dockerfiles for the API and dashboard; Compose profiles for the apps, the retention loop, MLflow and monitoring
- [x] Helm chart and kind cluster config in `deploy/`
- [x] CI jobs for the new parts
- [x] Notes on telco APIs, uplift and holdouts, and MLOps; design templates; ADR backlog

## Week 1 (now – 15 Nov 2026): audit the existing project

- [ ] Work through [week-1-audit.md](week-1-audit.md)
- [ ] Write [model-card.md](model-card.md)
- [ ] Start the decision log in [interview-prep.md](interview-prep.md)
- [ ] Archive the iris classification repository

**Done when:** you can defend the current model without notes, and CI on this branch is green.

## Week 2: the USSD kernel and OTP

Decisions due: ADR-001 (service boundaries), ADR-002 (menu), ADR-003 (sessions), ADR-004 (OTP).

- [ ] Draw the menu in [design/ussd-menu.md](design/ussd-menu.md): every screen, input and transition, and what ends a session
- [ ] Write the state machine by hand in `ussd-gateway/.../menu`, test first
- [ ] Sessions in Redis with a time-to-live; a test that an idle session expires
- [ ] The simulated platform: `mo-init`/`mo-cont` in, `mt-cont`/`mt-fin` out, shaped like Ideamart ([domain/telco-apis.md](domain/telco-apis.md))
- [ ] SMS OTP with rate limits, and tests for the limits

**Done when:** a scripted subscriber can dial, navigate, time out and log in with an OTP, all in tests.

## Week 3: events, scoring, MLflow, reasons

Decisions due: ADR-005 (events), ADR-006 (features), ADR-007 (registry and promotion).

- [ ] Usage-event contracts in [design/events.md](design/events.md); a generator that publishes them to Redpanda
- [ ] A consumer that turns events into features and a churn score
- [ ] Training logs to MLflow; serving loads the `champion` alias, not a file path
- [ ] SHAP reasons per subscriber, shown in the dashboard

**Done when:** a burst of simulated events changes a subscriber's score, and the dashboard shows why.

## Week 4: offers, holdout, carrier billing, Compose app

Decisions due: ADR-009 (offer policy), ADR-010 (holdout), ADR-011 (feedback loop), ADR-012 (billing), ADR-015 (app).

- [ ] Offer engine with a randomised holdout ([design/offer-engine.md](design/offer-engine.md))
- [ ] Offers delivered by SMS and USSD through the gateway
- [ ] Bundle purchase through mock charging, idempotent on `externalTrxId`
- [ ] Compose app: balance, bundles, offer inbox, offline cache ([design/selfcare-app.md](design/selfcare-app.md))
- [ ] Uplift report: offered against holdout, with a confidence interval

**Done when:** the uplift report runs end to end on simulated subscribers.

## Week 5: deploy, monitor, load test, write up

Decisions due: ADR-008 (drift), ADR-013 (deployment), ADR-014 (observability).

- [ ] PSI drift job and an alert; a drill that shifts the population and fires it
- [ ] Grafana dashboards: USSD latency, score distribution, drift, offers and uplift
- [ ] `helm install` on kind ([deploy/README.md](../../deploy/README.md))
- [ ] Load test the USSD gateway; record p95
- [ ] README: the loop, the numbers, a demo

**Done when:** the whole loop runs on kind from the README, and you can walk through it in five minutes.
