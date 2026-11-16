# Week 1: make the churn project interview-proof

This is the part of the plan that runs **now**, alongside exams (to 15 November
2026). Dialog's interviews probe "one project" in depth, and this is your strongest,
so it gets interrogated first. Work through each section, tick what is true, and fix
what is not. Record the answers you would give aloud in the decision log in
[interview-prep.md](interview-prep.md).

## Tests

- [ ] `pytest` passes from a fresh clone, following only the README
- [ ] Every API route has at least one test, including an error case (unknown customer, bad input)
- [ ] The training code has a test that would fail if the train/test split leaked
- [ ] You can say what the tests cover, and name the riskiest code that has no test

## Docker

- [ ] The API and the dashboard build as images (`backend/Dockerfile`, `frontend/Dockerfile`, added on this branch)
- [ ] `docker compose --profile apps up` runs the database, API and dashboard together
- [ ] The model file is inside the API image, or mounted, and you can say why you chose that
- [ ] You can explain each line of both Dockerfiles

## CI

- [ ] CI runs on every pull request and is green
- [ ] CI covers the Python tests, the dashboard lint and build, and (on this branch) the USSD gateway, the Android app and the Helm chart
- [ ] You know what CI does not check, and say so in the README

## Model card

Write [model-card.md](model-card.md). These are the questions an AI/ML interviewer at
Dialog is likely to ask, and the card is where your answers live:

- [ ] **Metric choice:** why PR-AUC and not accuracy or ROC-AUC, in one sentence
- [ ] **Class imbalance:** how much there is (about a quarter churn) and how training handles it
- [ ] **Threshold:** why 0.597, how it was chosen (F1 on out-of-fold predictions), and what changes if the business values recall over precision
- [ ] **Leakage checks:** why `total_charges` is excluded, how the test set stays untouched, and any other feature that could leak the label
- [ ] **What the numbers mean in customers:** 262 of 374 churners caught, 196 false alarms
- [ ] **Limits:** what the dataset is (IBM's sample, not Sri Lankan data), and what the model cannot know

## The repository as a whole

- [ ] README states what the project is, and is honest about what it is not
- [ ] No secrets in the history (`git log -p | grep -iE "password|secret|key"` turns up nothing real)
- [ ] The iris classification repo is archived or made private, and off your CV (the research report's advice: it is tutorial-level)

## Done when

You can give a five-minute walkthrough of the churn project, answer every model card
question without notes, and the branch's CI is green.
