"""Push-up exercise logic for angle thresholds and corrective feedback."""

from __future__ import annotations

from .base_exercise import BaseExercise


class PushUp(BaseExercise):
    """Exercise implementation for push-ups."""

    def get_required_landmarks(self) -> list[int]:
        """Return the landmarks required to evaluate a push-up."""
        return [11, 13, 15, 12, 14, 16, 23, 24]

    def get_angle_thresholds(self) -> dict[str, float]:
        """Return thresholds for push-up motion phases."""
        return {
            "rest_min": 150.0,
            "rest_max": 180.0,
            "transition_min": 90.0,
            "transition_max": 149.0,
            "complete_min": 60.0,
            "complete_max": 89.0,
        }

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate push-up specific feedback."""
        if state == "COMPLETE" and angle < 60:
            return "Good depth! Push back up with control."
        if state == "TRANSITION" and angle > 149:
            return "Lower deeper — aim for 75-90 degrees at the bottom."
        if state == "REST" and angle < 150:
            return "Fully extend your arms at the top."
        return ""

    def requires_side_view(self) -> bool:
        """Return whether push-up assessment is best from the side."""
        return True
