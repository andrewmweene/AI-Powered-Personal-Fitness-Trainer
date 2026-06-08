"""Posture accuracy, rep count, and streak calculation utilities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence


def calculate_posture_accuracy(scores: Sequence[float]) -> float:
    """Calculate average posture accuracy as a percentage."""
    if not scores:
        return 0.0
    return float(sum(scores) / len(scores) * 100)


def count_reps(states: Sequence[str]) -> int:
    """Count completed reps from a sequence of exercise states."""
    return sum(1 for state in states if state == "COMPLETE")


def calculate_streak(correct_reps: int, total_reps: int) -> float:
    """Calculate a correctness streak percentage for exercise form."""
    if total_reps == 0:
        return 0.0
    return float(correct_reps / total_reps * 100)


def calculate_total_sessions(sessions: list[dict]) -> int:
    """Return the total number of exercise sessions."""
    return len(sessions)


def calculate_total_reps(sessions: list[dict]) -> int:
    """Return the sum of total reps across all sessions."""
    return sum(int(session.get("total_reps", 0)) for session in sessions)


def calculate_average_accuracy(sessions: list[dict]) -> float:
    """Return the mean posture accuracy for a session list."""
    if not sessions:
        return 0.0
    accuracies = [float(session.get("posture_accuracy", 0.0)) for session in sessions]
    return float(sum(accuracies) / len(accuracies))


def calculate_sessions_per_week(sessions: list[dict]) -> float:
    """Count sessions in the last 7 days and return the count as a float."""
    if not sessions:
        return 0.0
    cutoff = datetime.utcnow() - timedelta(days=7)
    count = 0
    for session in sessions:
        created_at = session.get("created_at")
        if isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at)
            except ValueError:
                continue
        else:
            continue
        if timestamp >= cutoff:
            count += 1
    return float(count)


def calculate_average_reps_per_session(sessions: list[dict]) -> float:
    """Return average reps per session for the provided sessions."""
    if not sessions:
        return 0.0
    total_reps = calculate_total_reps(sessions)
    return float(total_reps) / len(sessions)


def build_user_metrics_dict(sessions: list[dict]) -> dict[str, float]:
    """Build the metrics dict used by the recommendation rule-based model."""
    return {
        "avg_posture_accuracy": calculate_average_accuracy(sessions),
        "sessions_per_week": calculate_sessions_per_week(sessions),
        "avg_reps_per_session": calculate_average_reps_per_session(sessions),
    }
