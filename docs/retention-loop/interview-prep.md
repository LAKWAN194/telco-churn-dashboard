# Interview preparation

## Decisions you must defend

From the project plan, plus the questions a telco or ML interviewer is likely to ask.

1. Why XGBoost over logistic regression for this data?
2. Why this threshold, and what would change it?
3. How do you stop the offer engine from training on its own interventions?
4. What happens to a USSD session when the gateway restarts?
5. Why PR-AUC and not accuracy?
6. How do you know the offers work, rather than that the targeted customers would have stayed anyway?
7. How big must the holdout be, and what does it cost the business?
8. What is PSI, and why those alert thresholds?
9. Why Kafka between the gateway and the scorer, instead of a direct call?
10. What does Kubernetes give you here that Docker Compose does not, and what does it cost?

## Decision log

| Date | Question | My answer | ADR |
| --- | --- | --- | --- |
| | | | |

## Five-minute walkthrough

1. **The problem** (30 s): predicting churn is not enough; you must act and measure.
2. **The model** (1 min): metric, imbalance, threshold, leakage. The model card.
3. **The loop** (1.5 min): USSD, events, score, offer, holdout. Draw it.
4. **The proof** (1 min): uplift with its confidence interval.
5. **Running it** (1 min): Kubernetes, dashboards, the drift alert firing on purpose.

## Whiteboard sketch

- [ ] The USSD menu state machine
- [ ] One USSD exchange: `mo-init`, `mt-cont`, `mo-cont`, `mt-fin`
- [ ] The loop from usage event to offer, with the holdout split
- [ ] The PSI formula and what each term means
