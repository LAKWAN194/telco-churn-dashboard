# Uplift and holdout groups

The churn model says who is likely to leave. It does not say whether an offer will
make them stay. Those are different questions, and confusing them is the most common
mistake in retention projects.

## Why a control group

Suppose you send a discount to the 1,000 customers with the highest churn score, and
800 of them are still here next month. Did the offer work? You cannot tell: perhaps
800 would have stayed anyway. To know, you need customers who were eligible for the
offer but, chosen **at random**, did not get it. That is the **holdout** (or control)
group.

```
uplift = retention rate (offered group) − retention rate (holdout group)
```

Only randomisation makes the two groups comparable. If you choose who goes into
the holdout by hand, or by any rule related to churn risk, the comparison is
biased.

## Design questions

| Question | Why it matters |
| --- | --- |
| What is randomised: the customer, or each offer? | Customers who get several offers complicate the comparison |
| How big is the holdout? | Too small and the uplift estimate is noise; too big and you give up retention |
| How long until you measure? | Churn takes time to show; an offer's effect may fade |
| What is the outcome: churned or not within N days, revenue kept, offers accepted? | Each tells a different story |
| What does an offer cost? | Uplift that costs more than the revenue it keeps is a loss |

These are ADR-010 (holdout design) and ADR-009 (offer policy).

## The feedback loop

Once offers are live, future training data contains customers who stayed **because
of the offer**. A model retrained on that data learns that high-risk profiles do not
churn, so it scores them lower and they stop getting offers. Guard against it on
purpose: for example, train only on the holdout group and untreated customers, or
record treatment as a feature and handle it explicitly. This is ADR-011, and it is
the question from the plan: "How do you stop the offer engine from training on its
own interventions?"

## Small numbers

In a simulation you control how many customers there are. Run enough that the
uplift's confidence interval is narrower than the effect you claim, and report the
interval, not only the point estimate.
