"""Tests for recommendation engine stubs and difficulty prediction."""

from recommendation.rule_based import predict_difficulty


def test_predict_difficulty_returns_string_label() -> None:
    label = predict_difficulty({"avg_accuracy": 0.8, "sessions_per_week": 3.0, "avg_reps": 12.0})
    assert label in {"beginner", "intermediate", "advanced"}
