"""Squat exercise logic for joint angle thresholds and feedback."""

from __future__ import annotations

from .base_exercise import BaseExercise


class Squat(BaseExercise):
    """Exercise implementation for squat posture and rep tracking."""

    def get_required_landmarks(self) -> list[int]:
        """Return the landmarks required to evaluate a squat."""
        return [23, 25, 27, 11, 0]

    def get_angle_thresholds(self) -> dict[str, float]:
        """Return squat-specific thresholds for state transitions."""
        return {
            "rest_min": 160.0,
            "rest_max": 180.0,
            "transition_min": 110.0,
            "transition_max": 159.0,
            "complete_min": 70.0,
            "complete_max": 109.0,
        }

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate squat-specific feedback based on angle and state."""
        if state == "COMPLETE" and angle < 70:
            return "Good depth! Drive through heels"
        if state == "TRANSITION" and angle > 100:
            return "Go lower — aim for 90 degrees"
        if state == "REST" and angle < 155:
            return "Fully extend knees at the top"
        return ""

    def requires_side_view(self) -> bool:
        """Return whether squat evaluation is best in a side view."""
        return True
