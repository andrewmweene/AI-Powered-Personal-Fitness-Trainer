"""Dumbbell fly exercise logic for posture monitoring and thresholds."""

from __future__ import annotations

from .base_exercise import BaseExercise


class DumbbellFly(BaseExercise):
    """Exercise implementation for dumbbell fly movement."""

    def get_required_landmarks(self) -> list[int]:
        """Return the landmarks required to evaluate dumbbell fly."""
        return [11, 13, 15, 12, 14, 16]

    def get_angle_landmarks(self) -> list[int]:
        """Use shoulder-elbow-wrist for the fly angle."""
        return [11, 13, 15]

    def get_angle_thresholds(self) -> dict[str, float]:
        """Return thresholds for dumbbell fly transitions."""
        return {
            "rest_min": 150.0,
            "rest_max": 180.0,
            "transition_min": 110.0,
            "transition_max": 149.0,
            "complete_min": 70.0,
            "complete_max": 109.0,
        }

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate corrective feedback for dumbbell fly."""
        if state == "COMPLETE" and angle < 70:
            return "Great contraction! Squeeze and hold briefly."
        if state == "TRANSITION" and angle > 149:
            return "Open your arms wider — aim for fuller range of motion."
        if state == "REST" and angle < 150:
            return "Return to the starting position with control."
        return ""

    def requires_side_view(self) -> bool:
        """Return whether dumbbell fly requires a side orientation."""
        return True
