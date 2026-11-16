# Architecture decision records

One file per decision. Copy [0000-template.md](0000-template.md) to
`NNNN-short-title.md`, start it as **Proposed**, get it critiqued, then mark it
**Accepted**. Never rewrite an accepted ADR; supersede it with a new one.

## Backlog

None of these is decided. Each lists the main options and what to weigh.

| ADR | Decision | Due | Status |
| --- | --- | --- | --- |
| 001 | Service boundaries | Week 2 | Open |
| 002 | USSD menu design | Week 2 | Open |
| 003 | Session store | Week 2 | Open |
| 004 | OTP rules | Week 2 | Open |
| 005 | Usage events and topics | Week 3 | Open |
| 006 | Feature computation | Week 3 | Open |
| 007 | Model registry and promotion | Week 3 | Open |
| 008 | Drift metric and alerting | Week 5 | Open |
| 009 | Offer policy | Week 4 | Open |
| 010 | Holdout design | Week 4 | Open |
| 011 | The feedback loop | Week 4 | Open |
| 012 | Carrier billing semantics | Week 4 | Open |
| 013 | Deployment | Week 5 | Open |
| 014 | Observability | Week 5 | Open |
| 015 | Self-care app architecture | Week 4 | Open |

### 001: Service boundaries

Where each part of the loop lives: the event generator, the scoring consumer and
the offer engine could extend the existing FastAPI service, or be new services. The
USSD gateway currently holds both the simulated platform and the menu. Weigh: what
you can deploy and explain, transactions that cross boundaries, and how much each
split costs in Helm templates and CI jobs.

### 002: USSD menu design

The screens, the inputs on each, back and home conventions, and how invalid input
and timeouts are handled. Also how the state machine is represented: an enum with a
transition table, a sealed interface per state, or a table loaded from data. Fill in
[design/ussd-menu.md](../design/ussd-menu.md).

### 003: Session store

What a session record holds, its Redis key, and its time-to-live. Weigh: the
platform's own session timeout (sessions last tens of seconds), memory, and what
happens if Redis restarts mid-session.

### 004: OTP rules

Code length, lifetime, attempts before lock-out, the rate limit per number and per
IP, and how codes are stored (hashed). Weigh: security against the cost of each SMS,
and the user who mistypes once.

### 005: Usage events and topics

Which events (calls, data sessions, top-ups, complaints, USSD visits), their fields,
topics, partition keys and versioning. Fill in [design/events.md](../design/events.md).

### 006: Feature computation

Streaming (update features as each event arrives) or micro-batch (recompute every
few minutes). Window lengths. How features match the ones the model was trained on.

### 007: Model registry and promotion

What each training run logs to MLflow, what a new version must beat to take the
`champion` alias, who or what promotes it, and how serving picks up the change.
Read [domain/mlops-primer.md](../domain/mlops-primer.md).

### 008: Drift metric and alerting

Which features PSI covers, the binning, the thresholds, how often it runs, and what
an alert does (page someone, trigger retraining, or only record it).

### 009: Offer policy

Who is eligible, which offer, through which channel, how often, and within what
budget. Fill in [design/offer-engine.md](../design/offer-engine.md).

### 010: Holdout design

What is randomised, the holdout share, the measurement window and the outcome.
Read [domain/uplift-and-holdouts.md](../domain/uplift-and-holdouts.md).

### 011: The feedback loop

How retraining avoids learning from the offers' own effect: train on the holdout and
untreated customers only, add treatment as a feature, or something else.

### 012: Carrier billing semantics

How the simulated direct debit behaves: idempotency on `externalTrxId`, timeouts,
and reconciliation. Read [domain/telco-apis.md](../domain/telco-apis.md#charging-as-a-service-carrier-billing).

### 013: Deployment

What runs in the cluster and what stays outside it, how the model reaches the API
pod, how secrets are handled, and an Ingress or port-forwarding. Read
[deploy/README.md](../../../deploy/README.md).

### 014: Observability

Which metrics each service exposes, the dashboards, the alerts, and any service
level objectives (for example "95% of USSD replies within ____ ms").

### 015: Self-care app architecture

State management (ViewModel and a single state object per screen), networking, the
offline cache (Room), and how the OTP login keeps a session. Fill in
[design/selfcare-app.md](../design/selfcare-app.md).
