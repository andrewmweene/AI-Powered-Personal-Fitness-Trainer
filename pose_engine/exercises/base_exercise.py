"""Abstract base class for exercises implemented in the pose engine."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseExercise(ABC):
    """Defines the interface required for all pose-based exercises."""

    @abstractmethod
    def get_required_landmarks(self) -> list[int]:
        """Return the MediaPipe landmark IDs required for this exercise."""
        raise NotImplementedError

    @abstractmethod
    def get_angle_thresholds(self) -> dict[str, float]:
        """Return the thresholds used for state transitions and rep counting."""
        raise NotImplementedError

    @abstractmethod
    def get_feedback(self, angle: float, state: str) -> str:
        """Return a feedback message based on the current angle and phase."""
        raise NotImplementedError

    @abstractmethod
    def requires_side_view(self) -> bool:
        """Return whether the exercise requires a side camera view."""
        raise NotImplementedError

    def get_display_name(self) -> str:
        """Return a human-friendly display name for the exercise."""
        return self.__class__.__name__
