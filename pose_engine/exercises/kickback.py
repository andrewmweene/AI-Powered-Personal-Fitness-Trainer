"""Dumbbell kickback exercise logic for extension and posture quality."""

from __future__ import annotations

from .base_exercise import BaseExercise


class Kickback(BaseExercise):
    """Exercise implementation for dumbbell kickbacks."""

    def get_required_landmarks(self) -> list[int]:
        """Return the landmarks required to evaluate a kickback."""
        return [11, 13, 15, 23, 25, 27]

    def get_angle_landmarks(self) -> list[int]:
        """Use shoulder-elbow-wrist for the kickback elbow angle."""
        return [11, 13, 15]

    def get_angle_thresholds(self) -> dict[str, float]:
        """Return thresholds for kickback motion phases."""
        return {
            "rest_min": 145.0,
            "rest_max": 180.0,
            "transition_min": 90.0,
            "transition_max": 144.0,
            "complete_min": 35.0,
            "complete_max": 89.0,
        }

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate feedback tailored to the kickback movement."""
        if state == "COMPLETE" and angle < 35:
            return "Excellent! Full extension with triceps engaged."
        if state == "TRANSITION" and angle > 144:
            return "Extend your arm further back for full contraction."
        if state == "REST" and angle < 145:
            return "Return your arm to the starting position with control."
        return ""

    def requires_side_view(self) -> bool:
        """Return whether kickback evaluation benefits from side view."""
        return True
