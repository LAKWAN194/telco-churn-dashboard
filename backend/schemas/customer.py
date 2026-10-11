from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# The option lists below are the exact values found in the Telco dataset.
YesNoPhone = Literal["Yes", "No", "No phone service"]
YesNoInternet = Literal["Yes", "No", "No internet service"]


class CustomerFeatures(BaseModel):
    """Everything the model needs to score one customer."""

    gender: Literal["Female", "Male"]
    senior_citizen: bool
    partner: bool
    dependents: bool
    tenure: int = Field(ge=0, le=120, description="Months as a customer")
    phone_service: bool
    multiple_lines: YesNoPhone
    internet_service: Literal["DSL", "Fiber optic", "No"]
    online_security: YesNoInternet
    online_backup: YesNoInternet
    device_protection: YesNoInternet
    tech_support: YesNoInternet
    streaming_tv: YesNoInternet
    streaming_movies: YesNoInternet
    contract_type: Literal["Month-to-month", "One year", "Two year"]
    paperless_billing: bool
    payment_method: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    monthly_charges: float = Field(ge=0, le=1000)


class CustomerOut(CustomerFeatures):
    """A customer as stored in the customers table."""

    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    total_charges: float | None = None
    churn_label: bool | None = None


class CustomerPage(BaseModel):
    total: int
    items: list[CustomerOut]


class AtRiskCustomer(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: Literal["low", "medium", "high"]
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float


class PredictionOut(BaseModel):
    prediction_id: int
    customer_id: str | None
    churn_probability: float
    churn_prediction: bool
    risk_level: Literal["low", "medium", "high"]
    model_version: str
    threshold_used: float
    predicted_at: datetime


class ModelInfo(BaseModel):
    model_name: str
    model_version: str
    threshold: float
    trained_at: str
    features: list[str]
    metrics: dict


class Summary(BaseModel):
    total_customers: int
    churned_customers: int
    churn_rate: float
    average_monthly_charges: float
    average_tenure: float
    # monthly charges of the customers who left
    monthly_revenue_lost: float


class ChurnGroup(BaseModel):
    label: str
    customers: int
    churned: int
    churn_rate: float
