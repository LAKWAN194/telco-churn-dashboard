# Model card: churn classifier

Fill this in during week 1 ([week-1-audit.md](week-1-audit.md)). The numbers are in
`models/artifacts/metrics.json`, and the reasoning behind them in `models/train.py`
and the main README. Write it in your own words: this is the page you will be
questioned on.

## Model details

| | |
| --- | --- |
| Model | |
| Version and date | |
| Trained by | `models/train.py` |
| Serving | `backend/services/model.py` |

## Intended use

<!-- Who uses the score, for what decision, and what it must not be used for. -->

## Data

<!-- The IBM Telco dataset: rows, features, label definition, time period (if known),
     and why it is not Sri Lankan data. How the train/test split was made. -->

## Metrics

| Metric | Value | What it means for a retention team |
| --- | --- | --- |
| PR-AUC | | |
| ROC-AUC | | |
| Recall at the threshold | | |
| Precision at the threshold | | |
| Baseline PR-AUC (random) | | |

## Decision threshold

<!-- The value, how it was chosen, and what moving it up or down would cost. -->

## Class imbalance

<!-- The churn rate, and how training accounts for it. -->

## Leakage checks

<!-- Each feature you considered dropping, and why. How you know the test set
     never influenced a choice. -->

## Known limits

<!-- What the model cannot see, groups it may score badly, and when it should be retrained. -->

## Changes

| Date | Version | Change |
| --- | --- | --- |
| | | |
