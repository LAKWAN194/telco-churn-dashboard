# Test strategy

## Layers

| Layer | What it proves | Tools | Runs |
| --- | --- | --- | --- |
| Existing Python tests | Pipeline, model and API | pytest | `pytest` |
| USSD kernel | Every screen and transition of the menu | JUnit 5 | `cd ussd-gateway && ./mvnw test` |
| Architecture | The menu stays free of framework code | ArchUnit (`KernelIsolationTest`) | same |
| Gateway integration | Sessions, OTP and billing against real Redis | Spring Boot test, Testcontainers | `./mvnw verify` |
| Events and scoring | Events become the right features and scores | pytest, Redpanda in Testcontainers or compose | Week 3 |
| Offer engine | Holdout assignment is random and recorded | pytest | Week 4 |
| Uplift analysis | The report computes uplift and its interval correctly | pytest on data with a known answer | Week 4 |
| App | ViewModels and screens | JUnit, Compose UI tests | `./gradlew testDebugUnitTest`, `connectedDebugAndroidTest` |
| Chart | The Helm chart is valid and renders | `helm lint`, `helm template` | CI |
| Load | USSD reply latency under load | k6 or Gatling | Week 5 |

## Invariants

| Invariant | Week | Test |
| --- | --- | --- |
| The menu kernel has no framework dependencies | 0 | `KernelIsolationTest` |
| Every input on every screen has a defined outcome | 2 | |
| An idle session expires and cannot be resumed | 2 | |
| OTP limits hold: attempts, lifetime, requests per number | 2 | |
| A charge with a reused `externalTrxId` never debits twice | 4 | |
| Holdout assignment does not depend on the churn score | 4 | |
| A holdout subscriber never receives an offer | 4 | |
| Retraining data excludes the offers' own effect, per ADR-011 | 4 | |
| A known population shift raises the drift alert; noise does not | 5 | |

## Failure drills

| Drill | Week | How |
| --- | --- | --- |
| Redis restarts mid-session | 2 | `docker compose restart redis` during a scripted session |
| The subscriber goes silent | 2 | Stop sending input and check the session expires |
| A debit times out, then is retried | 4 | Mock charging that times out once |
| The scoring consumer falls behind | 3 | Pause it, publish a burst, resume, and watch consumer lag |
| The population drifts | 5 | Change the generator's settings and watch the alert |

Write each up in [postmortems/](postmortems/).
