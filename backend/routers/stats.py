from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.schemas.customer import ChurnGroup, Summary
from backend.services.db import Customer, get_db

router = APIRouter(prefix="/stats", tags=["stats"])

# 1 for a churned customer, 0 otherwise, so SUM() counts the churners
CHURNED = case((Customer.churn_label.is_(True), 1), else_=0)

TENURE_BAND = case(
    (Customer.tenure <= 12, "0-12 months"),
    (Customer.tenure <= 24, "13-24 months"),
    (Customer.tenure <= 48, "25-48 months"),
    else_="49+ months",
)

# The ways the dashboard can break churn down, mapped to what to group by
DIMENSIONS = {
    "contract_type": Customer.contract_type,
    "internet_service": Customer.internet_service,
    "payment_method": Customer.payment_method,
    "tech_support": Customer.tech_support,
    "tenure_band": TENURE_BAND,
}


@router.get("/summary", response_model=Summary)
def summary(db: Session = Depends(get_db)):
    """Headline numbers for the top of the dashboard."""
    row = db.execute(
        select(
            func.count(Customer.customer_id),
            func.coalesce(func.sum(CHURNED), 0),
            func.coalesce(func.avg(Customer.monthly_charges), 0),
            func.coalesce(func.avg(Customer.tenure), 0),
            func.coalesce(func.sum(Customer.monthly_charges * CHURNED), 0),
        )
    ).one()

    total, churned, average_charges, average_tenure, revenue_lost = row

    return Summary(
        total_customers=total,
        churned_customers=churned,
        churn_rate=round(churned / total, 4) if total else 0.0,
        average_monthly_charges=round(float(average_charges), 2),
        average_tenure=round(float(average_tenure), 1),
        monthly_revenue_lost=round(float(revenue_lost), 2),
    )


@router.get("/churn-by/{dimension}", response_model=list[ChurnGroup])
def churn_by(dimension: str, db: Session = Depends(get_db)):
    """Churn rate for each value of one customer attribute."""
    if dimension not in DIMENSIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dimension '{dimension}'. Choose from: {', '.join(DIMENSIONS)}",
        )

    group = DIMENSIONS[dimension].label("label")
    rows = db.execute(
        select(group, func.count().label("customers"), func.sum(CHURNED).label("churned"))
        .group_by(group)
        .order_by(group)
    ).all()

    return [
        ChurnGroup(
            label=row.label,
            customers=row.customers,
            churned=row.churned,
            churn_rate=round(row.churned / row.customers, 4),
        )
        for row in rows
    ]
