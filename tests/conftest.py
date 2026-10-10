"""Fixtures shared by the model and API tests.

Everything is synthetic, like the fixtures in test_ingest.py, so the suite
needs neither the raw CSV nor a running PostgreSQL.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def make_customers(n_rows=400, seed=0):
    """Synthetic stand-in for cleaned customer data, shaped like clean_data() output.

    Churn is drawn at random but made more likely for short-tenure customers on
    month-to-month contracts, so there is a real pattern for a model to find.
    """
    rng = np.random.default_rng(seed)

    tenure = rng.integers(0, 73, n_rows)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n_rows, p=[0.55, 0.2, 0.25])
    internet = rng.choice(["DSL", "Fiber optic", "No"], n_rows)
    has_internet = internet != "No"
    phone = rng.random(n_rows) < 0.9
    monthly = np.round(rng.uniform(18, 120, n_rows), 2)

    churn_chance = 0.05 + 0.5 * (contract == "Month-to-month") + 0.3 * (tenure < 12)
    churn = rng.random(n_rows) < np.clip(churn_chance, 0, 0.95)

    def internet_addon():
        choice = rng.choice(["Yes", "No"], n_rows)
        return np.where(has_internet, choice, "No internet service")

    return pd.DataFrame({
        "customer_id": [f"{i:04d}-TEST" for i in range(n_rows)],
        "gender": rng.choice(["Female", "Male"], n_rows),
        "senior_citizen": rng.random(n_rows) < 0.16,
        "partner": rng.random(n_rows) < 0.5,
        "dependents": rng.random(n_rows) < 0.3,
        "tenure": tenure,
        "phone_service": phone,
        "multiple_lines": np.where(phone, rng.choice(["Yes", "No"], n_rows), "No phone service"),
        "internet_service": internet,
        "online_security": internet_addon(),
        "online_backup": internet_addon(),
        "device_protection": internet_addon(),
        "tech_support": internet_addon(),
        "streaming_tv": internet_addon(),
        "streaming_movies": internet_addon(),
        "contract_type": contract,
        "paperless_billing": rng.random(n_rows) < 0.6,
        "payment_method": rng.choice(
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
            n_rows,
        ),
        "monthly_charges": monthly,
        "total_charges": np.round(monthly * tenure, 2),
        "churn_label": churn,
    })


@pytest.fixture(scope="session")
def customers_df():
    return make_customers()


@pytest.fixture(scope="session")
def artifact(customers_df):
    """A model trained once on the synthetic customers and reused by every test."""
    from models.train import train

    return train(customers_df, data_source="csv")
