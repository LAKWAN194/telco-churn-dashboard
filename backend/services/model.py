from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import HTTPException

from backend.config import settings


def risk_level(probability: float, threshold: float) -> str:
    """
    Turn a probability into the label shown on the dashboard.

    Args:
        probability (float): Predicted churn probability.
        threshold (float): The cut-off the prediction was made with.

    Returns:
        str: "high" at or above the threshold, "medium" from half the
        threshold up, otherwise "low".
    """
    if probability >= threshold:
        return "high"
    if probability >= threshold / 2:
        return "medium"
    return "low"


class ChurnModel:
    """Wraps the artifact saved by models/train.py."""

    def __init__(self, artifact: dict):
        self.model = artifact["model"]
        self.features: list[str] = artifact["features"]
        self.threshold: float = artifact["threshold"]
        self.version: str = artifact["model_version"]
        self.name: str = artifact["model_name"]
        self.metrics: dict = artifact["metrics"]
        self.trained_at: str = artifact["trained_at"]

    @classmethod
    def load(cls, path: str) -> "ChurnModel":
        return cls(joblib.load(path))

    def score(self, customers: pd.DataFrame) -> np.ndarray:
        """
        Predict the churn probability for each row.

        Args:
            customers (pd.DataFrame): Must contain every column in self.features.

        Returns:
            np.ndarray: One probability between 0 and 1 per row.
        """
        return self.model.predict_proba(customers[self.features])[:, 1]

    def predict_one(self, customer: dict) -> tuple[float, bool]:
        """
        Predict churn for a single customer.

        Args:
            customer (dict): Feature name mapped to value.

        Returns:
            tuple[float, bool]: The churn probability and whether it is at or
            above the model's threshold.
        """
        probability = float(self.score(pd.DataFrame([customer]))[0])
        return probability, probability >= self.threshold


_model: ChurnModel | None = None


def get_model() -> ChurnModel:
    """
    FastAPI dependency that returns the trained model, loading it from disk
    the first time it is needed.

    Raises:
        HTTPException: 503 if models/train.py has not been run yet.
    """
    global _model

    if _model is None:
        if not Path(settings.model_path).exists():
            raise HTTPException(
                status_code=503,
                detail="Model has not been trained yet. Run: python models/train.py",
            )
        _model = ChurnModel.load(settings.model_path)

    return _model
