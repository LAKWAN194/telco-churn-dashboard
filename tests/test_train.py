"""Unit tests for models/train.py and models/evaluate.py."""

import joblib
import numpy as np
import pandas as pd
import pytest

from models.evaluate import evaluate_model
from models.train import (
    BOOLEAN_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    TEST_SIZE,
    build_candidates,
    build_preprocessor,
    choose_threshold,
    save_artifact,
    split_data,
)


class TestFeatures:
    def test_total_charges_is_not_a_feature(self):
        """The EDA notebook drops it for being tenure x monthly_charges restated."""
        assert "total_charges" not in FEATURES

    def test_identifier_and_target_are_not_features(self):
        assert "customer_id" not in FEATURES
        assert TARGET not in FEATURES

    def test_feature_groups_do_not_overlap(self):
        assert len(set(FEATURES)) == len(FEATURES)
        assert set(FEATURES) == set(NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES)


class TestSplitData:
    def test_split_sizes(self, customers_df):
        X_train, X_test, y_train, y_test = split_data(customers_df)

        assert len(X_test) == round(len(customers_df) * TEST_SIZE)
        assert len(X_train) + len(X_test) == len(customers_df)
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)

    def test_only_feature_columns_are_kept(self, customers_df):
        X_train, _, _, _ = split_data(customers_df)

        assert list(X_train.columns) == FEATURES

    def test_churn_rate_is_preserved(self, customers_df):
        _, _, y_train, y_test = split_data(customers_df)

        assert y_train.mean() == pytest.approx(y_test.mean(), abs=0.02)

    def test_split_ignores_row_order(self, customers_df):
        """The database returns rows in no fixed order, so the split must not care."""
        shuffled = customers_df.sample(frac=1, random_state=1)

        _, X_test, _, _ = split_data(customers_df)
        _, X_test_shuffled, _, _ = split_data(shuffled)

        pd.testing.assert_frame_equal(X_test, X_test_shuffled)


class TestPreprocessor:
    def test_output_is_numeric_with_no_missing_values(self, customers_df):
        transformed = build_preprocessor().fit_transform(customers_df[FEATURES])
        dense = transformed.toarray() if hasattr(transformed, "toarray") else transformed

        assert dense.shape[0] == len(customers_df)
        assert not np.isnan(dense.astype(float)).any()

    def test_unseen_category_does_not_raise(self, customers_df):
        preprocessor = build_preprocessor().fit(customers_df[FEATURES])

        new_customer = customers_df[FEATURES].head(1).copy()
        new_customer["payment_method"] = "Cryptocurrency"

        preprocessor.transform(new_customer)


class TestCandidates:
    def test_both_models_are_compared(self, customers_df):
        _, _, y_train, _ = split_data(customers_df)

        assert set(build_candidates(y_train)) == {"logreg", "xgboost"}

    def test_xgboost_is_weighted_for_the_imbalance(self, customers_df):
        _, _, y_train, _ = split_data(customers_df)
        classifier = build_candidates(y_train)["xgboost"].named_steps["classifier"]

        expected = (y_train == 0).sum() / (y_train == 1).sum()
        assert classifier.get_params()["scale_pos_weight"] == pytest.approx(expected)

    def test_logreg_is_weighted_for_the_imbalance(self, customers_df):
        _, _, y_train, _ = split_data(customers_df)
        classifier = build_candidates(y_train)["logreg"].named_steps["classifier"]

        assert classifier.class_weight == "balanced"


class TestChooseThreshold:
    def test_separates_perfectly_separable_scores(self):
        y_true = pd.Series([0, 0, 0, 1, 1, 1])
        probabilities = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])

        threshold = choose_threshold(y_true, probabilities)

        assert 0.3 < threshold <= 0.7

    def test_threshold_is_a_probability(self, artifact):
        assert 0 < artifact["threshold"] < 1


class TestTrain:
    def test_artifact_has_everything_the_backend_reads(self, artifact):
        for key in ("model", "model_name", "model_version", "threshold",
                    "features", "metrics", "trained_at"):
            assert key in artifact

    def test_model_version_fits_the_database_column(self, artifact):
        """predictions.model_version is VARCHAR(20)."""
        assert len(artifact["model_version"]) <= 20

    def test_best_model_is_the_one_with_highest_cv_score(self, artifact):
        scores = artifact["cv_pr_auc"]

        assert artifact["model_name"] == max(scores, key=scores.get)

    def test_model_beats_random_guessing(self, artifact):
        metrics = artifact["metrics"]

        assert metrics["pr_auc"] > metrics["baseline_pr_auc"]

    def test_model_predicts_probabilities_for_new_rows(self, artifact, customers_df):
        probabilities = artifact["model"].predict_proba(customers_df[FEATURES].head(5))[:, 1]

        assert probabilities.shape == (5,)
        assert ((probabilities >= 0) & (probabilities <= 1)).all()

    def test_artifact_survives_a_save_and_load(self, artifact, customers_df, tmp_path):
        model_path = tmp_path / "artifacts" / "churn_model.joblib"

        save_artifact(artifact, model_path)
        loaded = joblib.load(model_path)

        sample = customers_df[FEATURES].head(10)
        np.testing.assert_allclose(
            loaded["model"].predict_proba(sample),
            artifact["model"].predict_proba(sample),
        )
        assert (tmp_path / "artifacts" / "metrics.json").exists()


class TestEvaluateModel:
    def test_confusion_matrix_adds_up(self, artifact, customers_df):
        _, X_test, _, y_test = split_data(customers_df)

        metrics = evaluate_model(artifact["model"], X_test, y_test, artifact["threshold"])

        assert sum(metrics["confusion_matrix"].values()) == len(y_test) == metrics["n_samples"]

    def test_metrics_are_between_zero_and_one(self, artifact, customers_df):
        _, X_test, _, y_test = split_data(customers_df)

        metrics = evaluate_model(artifact["model"], X_test, y_test, artifact["threshold"])

        for name in ("pr_auc", "roc_auc", "recall", "precision", "f1"):
            assert 0 <= metrics[name] <= 1

    def test_lower_threshold_never_lowers_recall(self, artifact, customers_df):
        _, X_test, _, y_test = split_data(customers_df)

        strict = evaluate_model(artifact["model"], X_test, y_test, threshold=0.9)
        lenient = evaluate_model(artifact["model"], X_test, y_test, threshold=0.1)

        assert lenient["recall"] >= strict["recall"]

    def test_baseline_is_the_churn_rate(self, artifact, customers_df):
        _, X_test, _, y_test = split_data(customers_df)

        metrics = evaluate_model(artifact["model"], X_test, y_test, artifact["threshold"])

        assert metrics["baseline_pr_auc"] == pytest.approx(y_test.mean(), abs=1e-4)
