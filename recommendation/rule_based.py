"""Rule-based recommendation model for workout difficulty prediction."""

from __future__ import annotations

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

_model_cache: Pipeline | None = None


def build_and_train_model() -> Pipeline:
    """Build and train a decision tree pipeline on synthetic recommendation data."""
    np.random.seed(42)
    samples_per_class = 150

    beginner_accuracy = np.random.normal(loc=50.0, scale=6.0, size=samples_per_class)
    beginner_sessions = np.random.normal(loc=1.4, scale=0.3, size=samples_per_class)
    beginner_reps = np.random.normal(loc=6.0, scale=1.2, size=samples_per_class)

    intermediate_accuracy = np.random.normal(loc=70.0, scale=5.0, size=samples_per_class)
    intermediate_sessions = np.random.normal(loc=3.0, scale=0.4, size=samples_per_class)
    intermediate_reps = np.random.normal(loc=11.0, scale=1.8, size=samples_per_class)

    advanced_accuracy = np.random.normal(loc=90.0, scale=4.0, size=samples_per_class)
    advanced_sessions = np.random.normal(loc=5.5, scale=0.6, size=samples_per_class)
    advanced_reps = np.random.normal(loc=18.0, scale=2.0, size=samples_per_class)

    beginner = np.vstack(
        [
            np.clip(beginner_accuracy, 0.0, 100.0),
            np.clip(beginner_sessions, 0.0, 7.0),
            np.clip(beginner_reps, 0.0, 30.0),
        ]
    ).T
    intermediate = np.vstack(
        [
            np.clip(intermediate_accuracy, 0.0, 100.0),
            np.clip(intermediate_sessions, 0.0, 7.0),
            np.clip(intermediate_reps, 0.0, 30.0),
        ]
    ).T
    advanced = np.vstack(
        [
            np.clip(advanced_accuracy, 0.0, 100.0),
            np.clip(advanced_sessions, 0.0, 7.0),
            np.clip(advanced_reps, 0.0, 30.0),
        ]
    ).T

    features = np.vstack([beginner, intermediate, advanced])
    labels = np.concatenate(
        [
            np.zeros(samples_per_class, dtype=int),
            np.ones(samples_per_class, dtype=int),
            np.full(samples_per_class, 2, dtype=int),
        ]
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("classifier", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ]
    )
    pipeline.fit(features, labels)
    return pipeline


def predict_difficulty(user_metrics: dict[str, object]) -> str:
    """Predict a difficulty tier from aggregated user metrics."""
    global _model_cache
    if _model_cache is None:
        _model_cache = build_and_train_model()

    avg_posture_accuracy = float(user_metrics.get("avg_posture_accuracy", 0.0))
    sessions_per_week = float(user_metrics.get("sessions_per_week", 0.0))
    avg_reps_per_session = float(user_metrics.get("avg_reps_per_session", 0.0))

    prediction = int(
        _model_cache.predict(
            [[avg_posture_accuracy, sessions_per_week, avg_reps_per_session]]
        )[0]
    )
    mapping = {0: "beginner", 1: "intermediate", 2: "advanced"}
    return mapping.get(prediction, "beginner")
