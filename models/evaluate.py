import json
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv()

DEFAULT_MODEL_PATH = "./models/artifacts/churn_model.joblib"


def evaluate_model(model, X: pd.DataFrame, y: pd.Series, threshold: float) -> dict:
    """
    Score a fitted model on labelled data.

    Accuracy is deliberately left out: 73.5% of customers do not churn, so a
    model that never predicts churn would still look good on it. PR-AUC and
    recall on the churn class are the numbers that matter here (see the EDA
    notebook).

    Args:
        model: A fitted classifier with a predict_proba method.
        X (pd.DataFrame): Feature columns.
        y (pd.Series): True churn labels.
        threshold (float): Probability at or above which a customer is
            predicted to churn.

    Returns:
        dict: PR-AUC, ROC-AUC, recall, precision, F1 and the confusion matrix.
    """
    y_true = y.astype(int)
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()

    return {
        "pr_auc": round(float(average_precision_score(y_true, probabilities)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "threshold": round(float(threshold), 4),
        # The PR-AUC of a model that guesses at random is the churn rate itself.
        "baseline_pr_auc": round(float(y_true.mean()), 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "n_samples": int(len(y_true)),
    }


def print_metrics(metrics: dict) -> None:
    """
    Print the metrics from evaluate_model in a readable layout.

    Args:
        metrics (dict): The dictionary returned by evaluate_model.
    """
    matrix = metrics["confusion_matrix"]

    print(f"Samples:    {metrics['n_samples']}")
    print(f"Threshold:  {metrics['threshold']}")
    print(f"PR-AUC:     {metrics['pr_auc']}  (random guessing: {metrics['baseline_pr_auc']})")
    print(f"ROC-AUC:    {metrics['roc_auc']}")
    print(f"Recall:     {metrics['recall']}")
    print(f"Precision:  {metrics['precision']}")
    print(f"F1:         {metrics['f1']}")
    print()
    print("Confusion matrix:")
    print("                   predicted stay   predicted churn")
    print(f"  actually stayed  {matrix['true_negatives']:>14}   {matrix['false_positives']:>15}")
    print(f"  actually churned {matrix['false_negatives']:>14}   {matrix['true_positives']:>15}")


def save_metrics(metrics: dict, path: Path) -> None:
    """
    Write metrics to a JSON file next to the model artifact.

    Args:
        metrics (dict): The dictionary returned by evaluate_model.
        path (Path): The JSON file to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2))


if __name__ == "__main__":

    from models.train import load_training_data, split_data

    model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    artifact = joblib.load(model_path)
    print(f"Loaded model {artifact['model_version']} from {model_path}")

    source = sys.argv[1] if len(sys.argv) > 1 else artifact["data_source"]
    df = load_training_data(source)

    # Same split as train.py, so this is the test set the model never saw.
    _, X_test, _, y_test = split_data(df)

    metrics = evaluate_model(artifact["model"], X_test, y_test, artifact["threshold"])
    print_metrics(metrics)

    metrics_path = model_path.with_name("metrics.json")
    save_metrics(metrics, metrics_path)
    print(f"\nSaved metrics to {metrics_path}")
