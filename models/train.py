import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.evaluate import evaluate_model, print_metrics, save_metrics
from pipeline.ingest import clean_data, load_raw_data

load_dotenv()

RAW_DATA_PATH = "data/raw/telco_churn.csv"
DEFAULT_MODEL_PATH = "./models/artifacts/churn_model.joblib"

TARGET = "churn_label"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# total_charges is left out on purpose: the EDA notebook shows it is roughly
# tenure x monthly_charges, so it adds collinearity without adding signal.
NUMERIC_FEATURES = ["tenure", "monthly_charges"]

BOOLEAN_FEATURES = [
    "senior_citizen",
    "partner",
    "dependents",
    "phone_service",
    "paperless_billing",
]

CATEGORICAL_FEATURES = [
    "gender",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract_type",
    "payment_method",
]

FEATURES = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES


def load_training_data(source: str = "db") -> pd.DataFrame:
    """
    Load the cleaned customer data used for training.

    Args:
        source (str): "db" reads the customers table that pipeline/ingest.py
            loaded. "csv" cleans the raw CSV directly, which needs no database.

    Returns:
        pd.DataFrame: One row per customer, with snake_case columns.
    """
    if source == "csv":
        return clean_data(load_raw_data(RAW_DATA_PATH))

    if source == "db":
        from sqlalchemy import create_engine

        DATABASE_URL = (
            f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:"
            f"{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}")

        engine = create_engine(DATABASE_URL)
        df = pd.read_sql("SELECT * FROM customers", engine)

        # DECIMAL columns come back from PostgreSQL as Decimal objects
        df["monthly_charges"] = df["monthly_charges"].astype(float)
        df["total_charges"] = df["total_charges"].astype(float)

        return df

    raise ValueError(f"Unknown data source '{source}'. Use 'db' or 'csv'.")


def split_data(df: pd.DataFrame):
    """
    Split customers into train and test sets, keeping the churn rate the same
    in both.

    Args:
        df (pd.DataFrame): The cleaned customer data.

    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    # Sort first so the split does not depend on the order rows arrive in
    # (the database does not guarantee one).
    df = df.sort_values("customer_id").reset_index(drop=True)

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )


def build_preprocessor() -> ColumnTransformer:
    """
    Build the preprocessing step shared by every candidate model.

    Returns:
        ColumnTransformer: Scales the numeric columns, one-hot encodes the
        categorical ones and passes the boolean ones through as 0/1.
    """
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("boolean", "passthrough", BOOLEAN_FEATURES),
        ]
    )


def build_candidates(y_train: pd.Series) -> dict:
    """
    Build the models to compare. Both are told about the class imbalance,
    since only about a quarter of customers churn.

    Args:
        y_train (pd.Series): Training labels, used to weight the churn class.

    Returns:
        dict: Model name mapped to an unfitted pipeline.
    """
    negatives = int((y_train == 0).sum())
    positives = int((y_train == 1).sum())

    return {
        "logreg": Pipeline([
            ("preprocess", build_preprocessor()),
            ("classifier", LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=RANDOM_STATE,
            )),
        ]),
        "xgboost": Pipeline([
            ("preprocess", build_preprocessor()),
            ("classifier", XGBClassifier(
                n_estimators=300,
                learning_rate=0.03,
                max_depth=3,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=negatives / positives,
                eval_metric="aucpr",
                random_state=RANDOM_STATE,
            )),
        ]),
    }


def choose_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    """
    Pick the probability cut-off with the best F1 score.

    Args:
        y_true (pd.Series): True churn labels.
        probabilities (np.ndarray): Predicted churn probabilities for the same rows.

    Returns:
        float: The threshold at or above which a customer counts as churning.
    """
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)

    # precision and recall have one more entry than thresholds
    precision, recall = precision[:-1], recall[:-1]
    f1 = 2 * precision * recall / np.maximum(precision + recall, 1e-12)

    return float(thresholds[np.argmax(f1)])


def train(df: pd.DataFrame, data_source: str = "csv") -> dict:
    """
    Compare the candidate models, keep the best one and score it on the test set.

    Candidates are compared on cross-validated PR-AUC using the training data
    only. The threshold is chosen from those same out-of-fold predictions, so
    the test set is used exactly once, for the final metrics.

    Args:
        df (pd.DataFrame): The cleaned customer data.
        data_source (str): Where df came from, recorded in the artifact.

    Returns:
        dict: The artifact to save, holding the fitted model and its metadata.
    """
    X_train, X_test, y_train, y_test = split_data(df)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    cv_scores = {}
    out_of_fold = {}

    for name, candidate in build_candidates(y_train).items():
        probabilities = cross_val_predict(
            candidate, X_train, y_train, cv=folds, method="predict_proba"
        )[:, 1]

        out_of_fold[name] = probabilities
        cv_scores[name] = round(float(average_precision_score(y_train, probabilities)), 4)
        print(f"  {name}: cross-validated PR-AUC = {cv_scores[name]}")

    best_name = max(cv_scores, key=cv_scores.get)
    print(f"Best model: {best_name}")

    threshold = choose_threshold(y_train, out_of_fold[best_name])

    model = build_candidates(y_train)[best_name]
    model.fit(X_train, y_train)

    metrics = evaluate_model(model, X_test, y_test, threshold)
    trained_at = datetime.now(timezone.utc)

    return {
        "model": model,
        "model_name": best_name,
        # fits the VARCHAR(20) model_version column in the predictions table
        "model_version": f"{best_name}-{trained_at:%Y%m%d}",
        "threshold": threshold,
        "features": FEATURES,
        "metrics": metrics,
        "cv_pr_auc": cv_scores,
        "trained_at": trained_at.isoformat(),
        "data_source": data_source,
        "n_train": int(len(X_train)),
    }


def save_artifact(artifact: dict, model_path: Path) -> None:
    """
    Save the model artifact, plus its test metrics as JSON beside it.

    Args:
        artifact (dict): The dictionary returned by train.
        model_path (Path): Where to write the .joblib file.
    """
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)
    save_metrics(artifact["metrics"], model_path.with_name("metrics.json"))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Train the churn model.")
    parser.add_argument(
        "--source",
        choices=["db", "csv"],
        default="db",
        help="read customers from the database (default) or straight from the raw CSV",
    )
    args = parser.parse_args()

    print(f"Loading training data from {args.source}...")
    df = load_training_data(args.source)
    print(f"Loaded {len(df)} customers.")

    print("Training candidate models...")
    artifact = train(df, data_source=args.source)

    print("\nTest set results:")
    print_metrics(artifact["metrics"])

    model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    save_artifact(artifact, model_path)
    print(f"\nSaved model {artifact['model_version']} to {model_path}")
