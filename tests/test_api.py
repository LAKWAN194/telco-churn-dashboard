"""Tests for the FastAPI backend.

The app is pointed at an in-memory SQLite database and a model trained on
synthetic customers, so nothing here needs PostgreSQL or a saved artifact.
"""

import os

# Must be set before the backend is imported, because the engine is created
# at import time from this URL.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.services.db import Base, Customer, get_db
from backend.services.model import ChurnModel, get_model, risk_level

VALID_CUSTOMER = {
    "gender": "Female",
    "senior_citizen": False,
    "partner": True,
    "dependents": False,
    "tenure": 3,
    "phone_service": True,
    "multiple_lines": "No",
    "internet_service": "Fiber optic",
    "online_security": "No",
    "online_backup": "No",
    "device_protection": "No",
    "tech_support": "No",
    "streaming_tv": "Yes",
    "streaming_movies": "Yes",
    "contract_type": "Month-to-month",
    "paperless_billing": True,
    "payment_method": "Electronic check",
    "monthly_charges": 95.5,
}


@pytest.fixture
def session_factory(customers_df):
    """A fresh in-memory database for each test, loaded with the synthetic customers."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with factory() as db:
        db.add_all(Customer(**row) for row in customers_df.to_dict(orient="records"))
        db.commit()

    return factory


@pytest.fixture
def client(session_factory, artifact):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_model] = lambda: ChurnModel(artifact)

    yield TestClient(app)

    app.dependency_overrides.clear()


class TestHealth:
    def test_reports_database_ok(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["database"] == "ok"


class TestModelInfo:
    def test_describes_the_serving_model(self, client, artifact):
        body = client.get("/model").json()

        assert body["model_version"] == artifact["model_version"]
        assert body["features"] == artifact["features"]
        assert "pr_auc" in body["metrics"]

    def test_503_when_model_has_not_been_trained(self, client, monkeypatch, tmp_path):
        from backend.services import model as model_service

        del app.dependency_overrides[get_model]
        monkeypatch.setattr(model_service, "_model", None)
        monkeypatch.setattr(
            model_service, "settings",
            type("Settings", (), {"model_path": str(tmp_path / "missing.joblib")})(),
        )

        response = client.get("/model")

        assert response.status_code == 503
        assert "train.py" in response.json()["detail"]


class TestPredict:
    def test_returns_probability_and_decision(self, client, artifact):
        response = client.post("/predict", json=VALID_CUSTOMER)
        body = response.json()

        assert response.status_code == 200
        assert 0 <= body["churn_probability"] <= 1
        assert body["churn_prediction"] == (body["churn_probability"] >= body["threshold_used"])
        assert body["model_version"] == artifact["model_version"]
        assert body["customer_id"] is None

    def test_risky_profile_scores_higher_than_safe_one(self, client):
        safe = {**VALID_CUSTOMER, "tenure": 70, "contract_type": "Two year"}

        risky_score = client.post("/predict", json=VALID_CUSTOMER).json()["churn_probability"]
        safe_score = client.post("/predict", json=safe).json()["churn_probability"]

        assert risky_score > safe_score

    def test_prediction_is_saved(self, client):
        saved = client.post("/predict", json=VALID_CUSTOMER).json()

        recent = client.get("/predictions").json()

        assert recent[0]["prediction_id"] == saved["prediction_id"]

    @pytest.mark.parametrize(
        "field, value",
        [
            ("contract_type", "Weekly"),
            ("tenure", -1),
            ("monthly_charges", -5),
            ("gender", ""),
        ],
    )
    def test_rejects_invalid_values(self, client, field, value):
        response = client.post("/predict", json={**VALID_CUSTOMER, field: value})

        assert response.status_code == 422

    def test_rejects_missing_field(self, client):
        incomplete = {k: v for k, v in VALID_CUSTOMER.items() if k != "tenure"}

        assert client.post("/predict", json=incomplete).status_code == 422


class TestPredictForCustomer:
    def test_scores_a_stored_customer(self, client):
        response = client.post("/predict/0000-TEST")
        body = response.json()

        assert response.status_code == 200
        assert body["customer_id"] == "0000-TEST"
        assert 0 <= body["churn_probability"] <= 1

    def test_unknown_customer_is_404(self, client):
        assert client.post("/predict/does-not-exist").status_code == 404


class TestRecentPredictions:
    def test_empty_before_any_prediction(self, client):
        assert client.get("/predictions").json() == []

    def test_newest_first_and_limited(self, client):
        ids = [client.post("/predict", json=VALID_CUSTOMER).json()["prediction_id"] for _ in range(3)]

        recent = client.get("/predictions", params={"limit": 2}).json()

        assert [p["prediction_id"] for p in recent] == ids[::-1][:2]


class TestCustomers:
    def test_lists_a_page(self, client, customers_df):
        body = client.get("/customers", params={"limit": 5}).json()

        assert body["total"] == len(customers_df)
        assert len(body["items"]) == 5

    def test_pages_do_not_overlap(self, client):
        first = client.get("/customers", params={"limit": 5, "offset": 0}).json()["items"]
        second = client.get("/customers", params={"limit": 5, "offset": 5}).json()["items"]

        first_ids = {c["customer_id"] for c in first}
        second_ids = {c["customer_id"] for c in second}
        assert first_ids.isdisjoint(second_ids)

    def test_search_filters_by_id(self, client):
        body = client.get("/customers", params={"search": "0042"}).json()

        assert body["total"] == 1
        assert body["items"][0]["customer_id"] == "0042-TEST"

    def test_get_one_customer(self, client):
        body = client.get("/customers/0007-TEST").json()

        assert body["customer_id"] == "0007-TEST"
        assert "contract_type" in body

    def test_unknown_customer_is_404(self, client):
        assert client.get("/customers/does-not-exist").status_code == 404


class TestAtRiskCustomers:
    def test_sorted_by_risk_and_limited(self, client):
        body = client.get("/customers/at-risk", params={"limit": 8}).json()
        probabilities = [c["churn_probability"] for c in body]

        assert len(body) == 8
        assert probabilities == sorted(probabilities, reverse=True)

    def test_leaves_out_customers_who_already_churned(self, client, customers_df):
        churned_ids = set(customers_df.loc[customers_df["churn_label"], "customer_id"])

        body = client.get("/customers/at-risk", params={"limit": 100}).json()

        assert churned_ids.isdisjoint(c["customer_id"] for c in body)

    def test_empty_database_gives_empty_list(self, client, session_factory):
        with session_factory() as db:
            db.query(Customer).delete()
            db.commit()

        assert client.get("/customers/at-risk").json() == []


class TestStats:
    def test_summary_matches_the_data(self, client, customers_df):
        body = client.get("/stats/summary").json()

        assert body["total_customers"] == len(customers_df)
        assert body["churned_customers"] == int(customers_df["churn_label"].sum())
        assert body["churn_rate"] == pytest.approx(customers_df["churn_label"].mean(), abs=1e-4)
        assert body["average_tenure"] == pytest.approx(customers_df["tenure"].mean(), abs=0.05)
        assert body["monthly_revenue_lost"] == pytest.approx(
            customers_df.loc[customers_df["churn_label"], "monthly_charges"].sum(), abs=0.01
        )

    def test_summary_of_empty_database(self, client, session_factory):
        with session_factory() as db:
            db.query(Customer).delete()
            db.commit()

        body = client.get("/stats/summary").json()

        assert body["total_customers"] == 0
        assert body["churn_rate"] == 0

    def test_churn_by_contract_matches_the_data(self, client, customers_df):
        body = client.get("/stats/churn-by/contract_type").json()
        expected = customers_df.groupby("contract_type")["churn_label"].agg(["size", "sum"])

        assert {g["label"] for g in body} == set(expected.index)
        for group in body:
            assert group["customers"] == expected.loc[group["label"], "size"]
            assert group["churned"] == expected.loc[group["label"], "sum"]

    def test_groups_cover_every_customer(self, client, customers_df):
        for dimension in ("contract_type", "internet_service", "payment_method",
                          "tech_support", "tenure_band"):
            body = client.get(f"/stats/churn-by/{dimension}").json()

            assert sum(g["customers"] for g in body) == len(customers_df)

    def test_tenure_bands_have_the_right_edges(self, client, customers_df):
        body = {g["label"]: g["customers"] for g in client.get("/stats/churn-by/tenure_band").json()}

        assert body["0-12 months"] == int((customers_df["tenure"] <= 12).sum())
        assert body["49+ months"] == int((customers_df["tenure"] > 48).sum())

    def test_unknown_dimension_is_404(self, client):
        assert client.get("/stats/churn-by/shoe_size").status_code == 404


class TestRiskLevel:
    @pytest.mark.parametrize(
        "probability, expected",
        [(0.9, "high"), (0.6, "high"), (0.59, "medium"), (0.3, "medium"), (0.29, "low"), (0.0, "low")],
    )
    def test_levels_follow_the_threshold(self, probability, expected):
        assert risk_level(probability, threshold=0.6) == expected
