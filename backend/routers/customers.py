import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.schemas.customer import AtRiskCustomer, CustomerOut, CustomerPage
from backend.services.db import Customer, get_db
from backend.services.model import ChurnModel, get_model, risk_level

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerPage)
def list_customers(
    search: str | None = Query(default=None, description="Part of a customer id"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """A page of customers, optionally filtered by customer id."""
    query = select(Customer)
    if search:
        query = query.where(Customer.customer_id.ilike(f"%{search.strip()}%"))

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    customers = db.execute(
        query.order_by(Customer.customer_id).limit(limit).offset(offset)
    ).scalars().all()

    return CustomerPage(total=total, items=customers)


# Declared before /{customer_id} so "at-risk" is not read as a customer id.
@router.get("/at-risk", response_model=list[AtRiskCustomer])
def at_risk_customers(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    model: ChurnModel = Depends(get_model),
):
    """
    Current customers the model thinks are most likely to leave.

    Customers who have already churned are left out: there is nobody left to
    win back.
    """
    customers = db.execute(
        select(Customer).where(Customer.churn_label.is_(False))
    ).scalars().all()

    if not customers:
        return []

    columns = ["customer_id"] + model.features
    frame = pd.DataFrame(
        [{column: getattr(customer, column) for column in columns} for customer in customers]
    )
    frame["churn_probability"] = model.score(frame)

    riskiest = frame.sort_values("churn_probability", ascending=False).head(limit)

    return [
        AtRiskCustomer(
            customer_id=row.customer_id,
            churn_probability=round(float(row.churn_probability), 4),
            risk_level=risk_level(row.churn_probability, model.threshold),
            tenure=row.tenure,
            contract_type=row.contract_type,
            internet_service=row.internet_service,
            monthly_charges=row.monthly_charges,
        )
        for row in riskiest.itertuples()
    ]


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """One customer by id."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    return customer
