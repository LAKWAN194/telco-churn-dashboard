"""Unit tests for pipeline/ingest.py.

All fixtures are synthetic: nothing here touches data/raw/telco_churn.csv,
so the suite runs on a clean clone where the raw data is gitignored.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.ingest import clean_data, load_raw_data

# Column names exactly as they appear in the IBM Telco churn CSV.
RAW_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

EXPECTED_CLEAN_COLUMNS = [
    "customer_id",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract_type",
    "paperless_billing",
    "payment_method",
    "monthly_charges",
    "total_charges",
    "churn_label",
]

BOOLEAN_YES_NO_COLUMNS = [
    "partner",
    "dependents",
    "phone_service",
    "paperless_billing",
    "churn_label",
]


def make_raw_row(index, total_charges=None):
    """Build one raw-CSV-shaped record. Values alternate so the frame is varied."""
    flip = index % 2 == 0
    monthly = 20.0 + (index % 100)
    return {
        "customerID": f"{index:04d}-ABCDE",
        "gender": "Female" if flip else "Male",
        "SeniorCitizen": 1 if flip else 0,
        "Partner": "Yes" if flip else "No",
        "Dependents": "No" if flip else "Yes",
        "tenure": index % 72,
        "PhoneService": "Yes" if flip else "No",
        "MultipleLines": "No" if flip else "No phone service",
        "InternetService": "DSL" if flip else "Fiber optic",
        "OnlineSecurity": "Yes" if flip else "No",
        "OnlineBackup": "No" if flip else "Yes",
        "DeviceProtection": "Yes" if flip else "No",
        "TechSupport": "No" if flip else "Yes",
        "StreamingTV": "Yes" if flip else "No",
        "StreamingMovies": "No" if flip else "Yes",
        "Contract": "Month-to-month" if flip else "Two year",
        "PaperlessBilling": "Yes" if flip else "No",
        "PaymentMethod": "Electronic check" if flip else "Mailed check",
        "MonthlyCharges": monthly,
        # The real CSV stores TotalCharges as text, blanks included.
        "TotalCharges": f"{monthly * 2:.2f}" if total_charges is None else total_charges,
        "Churn": "Yes" if flip else "No",
    }


def make_raw_df(n_rows=10, n_blank_total_charges=0):
    """Synthetic stand-in for the raw CSV, with optional blank TotalCharges rows."""
    rows = [
        make_raw_row(i, total_charges=" " if i < n_blank_total_charges else None)
        for i in range(n_rows)
    ]
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


@pytest.fixture
def raw_df():
    return make_raw_df(n_rows=10)


@pytest.fixture
def clean_df(raw_df):
    return clean_data(raw_df)


class TestLoadRawData:
    def test_returns_dataframe(self, tmp_path, raw_df):
        csv_path = tmp_path / "telco_churn.csv"
        raw_df.to_csv(csv_path, index=False)

        result = load_raw_data(str(csv_path))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(raw_df)

    def test_has_expected_raw_columns(self, tmp_path, raw_df):
        csv_path = tmp_path / "telco_churn.csv"
        raw_df.to_csv(csv_path, index=False)

        result = load_raw_data(str(csv_path))

        assert list(result.columns) == RAW_COLUMNS
        for column in ("customerID", "SeniorCitizen", "TotalCharges", "Churn"):
            assert column in result.columns


class TestCleanDataColumns:
    def test_columns_are_snake_case(self, clean_df):
        assert list(clean_df.columns) == EXPECTED_CLEAN_COLUMNS

    def test_camel_case_names_are_gone(self, clean_df):
        for column in ("customerID", "SeniorCitizen", "TotalCharges", "Churn"):
            assert column not in clean_df.columns


class TestCleanDataDtypes:
    def test_senior_citizen_is_boolean(self, clean_df):
        assert clean_df["senior_citizen"].dtype == bool

    def test_senior_citizen_values_map_from_zero_one(self):
        df = clean_data(make_raw_df(n_rows=2))
        # Row 0 has SeniorCitizen=1, row 1 has SeniorCitizen=0.
        assert clean_df_values(df, "senior_citizen") == [True, False]

    @pytest.mark.parametrize("column", BOOLEAN_YES_NO_COLUMNS)
    def test_yes_no_columns_are_boolean(self, clean_df, column):
        assert clean_df[column].dtype == bool

    def test_yes_no_values_map_correctly(self):
        df = clean_data(make_raw_df(n_rows=2))
        # Row 0 is Partner=Yes/Churn=Yes, row 1 is Partner=No/Churn=No.
        assert clean_df_values(df, "partner") == [True, False]
        assert clean_df_values(df, "churn_label") == [True, False]

    def test_total_charges_is_numeric(self, clean_df):
        assert pd.api.types.is_numeric_dtype(clean_df["total_charges"])
        assert pd.api.types.is_float_dtype(clean_df["total_charges"])


class TestCleanDataRowFiltering:
    def test_blank_total_charges_rows_are_dropped(self):
        """Mirrors the real CSV: 7043 rows in, 11 blank TotalCharges, 7032 out."""
        raw = make_raw_df(n_rows=7043, n_blank_total_charges=11)
        assert len(raw) == 7043

        result = clean_data(raw)

        assert len(result) == 7032
        assert result["total_charges"].notna().all()

    def test_duplicate_rows_are_dropped(self):
        raw = make_raw_df(n_rows=5)
        raw_with_dupes = pd.concat([raw, raw], ignore_index=True)

        result = clean_data(raw_with_dupes)

        assert len(result) == 5
        assert not result.duplicated().any()

    def test_output_has_no_duplicates(self, clean_df):
        assert not clean_df.duplicated().any()

    def test_input_frame_is_not_mutated(self, raw_df):
        before = raw_df.copy()

        clean_data(raw_df)

        pd.testing.assert_frame_equal(raw_df, before)


def clean_df_values(df, column):
    return df[column].tolist()
