"""Analytics package for posture accuracy, progress, and chart generation."""

from .metrics import calculate_posture_accuracy, count_reps, calculate_streak
from .progress import analyze_trends

__all__ = [
    "calculate_posture_accuracy",
    "count_reps",
    "calculate_streak",
    "analyze_trends",
]
