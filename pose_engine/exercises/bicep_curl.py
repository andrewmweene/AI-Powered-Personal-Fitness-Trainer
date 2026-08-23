"""Bicep curl exercise logic for joint angle thresholds and feedback."""

from __future__ import annotations

from .base_exercise import BaseExercise


class BicepCurl(BaseExercise):
    """Exercise implementation for bicep curls."""

    def get_required_landmarks(self) -> list[int]:
        """Return the landmarks required to evaluate a bicep curl."""
        return [11, 13, 15, 12, 14, 16]

    def get_angle_landmarks(self) -> list[int]:
        """Use shoulder-elbow-wrist for the curl angle."""
        return [11, 13, 15]

    def get_angle_thresholds(self) -> dict[str, float]:
        """Return bicep curl thresholds for state detection."""
        return {
            "rest_min": 145.0,
            "rest_max": 200.0,
            "transition_min": 85.0,
            "transition_max": 144.0,
            "complete_min": 35.0,
            "complete_max": 84.0,
        }

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate feedback for the current curl angle and state."""
        if state == "COMPLETE" and angle < 35:
            return "Perfect contraction! Pause and control the lowering phase."
        if state == "TRANSITION" and angle > 144:
            return "Curl higher — aim for the full range of motion."
        if state == "REST" and angle < 145:
            return "Fully extend your arms at the rest position."
        return ""

    def requires_side_view(self) -> bool:
        """Return whether bicep curl evaluation prefers side view."""
        return True
