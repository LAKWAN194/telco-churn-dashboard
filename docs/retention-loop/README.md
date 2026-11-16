# Retention loop (project 2)

Turning the churn model into a closed loop over USSD and SMS, with a measured holdout,
MLflow, drift alerts and Kubernetes. Work happens on the `p2/retention-loop` branch.

| Document | What it covers |
| --- | --- |
| [brief.md](brief.md) | The problem, scope, non-goals, success criteria, target employers |
| [roadmap.md](roadmap.md) | Week 1 now (the audit), weeks 2–5 later |
| [week-1-audit.md](week-1-audit.md) | Making the existing project interview-proof |
| [model-card.md](model-card.md) | The churn model's card, to fill in |
| [domain/telco-apis.md](domain/telco-apis.md) | USSD, SMS and carrier billing, modelled on Ideamart |
| [domain/uplift-and-holdouts.md](domain/uplift-and-holdouts.md) | Measuring whether offers work, and the feedback loop |
| [domain/mlops-primer.md](domain/mlops-primer.md) | MLflow, drift (PSI), Prometheus and Grafana, kind and Helm |
| [design/](design/) | Your designs: the USSD menu kernel, events, offers, the app |
| [adr/](adr/) | Decision records and the backlog |
| [testing.md](testing.md) | Test layers, invariants and failure drills |
| [security.md](security.md) | The security checklist |
| [interview-prep.md](interview-prep.md) | Questions to defend, decision log, walkthrough |
| [postmortems/](postmortems/) | One write-up per failure drill |
| [runbook.md](runbook.md) | Ports, profiles and commands |
| [references.md](references.md) | Links |
