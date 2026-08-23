"""Abstract base class for exercises implemented in the pose engine."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pose_engine.angle_utils import calculate_offset_angle, get_landmark_coords


class BaseExercise(ABC):
    """Defines the interface required for all pose-based exercises."""

    @abstractmethod
    def get_required_landmarks(self) -> list[int]:
        """Return the MediaPipe landmark IDs required for this exercise."""
        raise NotImplementedError

    def get_angle_landmarks(self) -> list[int]:
        """Return the three landmark IDs used to compute the exercise angle.

        Default behavior is the first three required landmarks, but exercise
        implementations can override this to ensure the angle is measured at the
        actual joint being tracked (for example, shoulder-elbow-wrist for curls).
        """
        required = self.get_required_landmarks()
        return required[:3]

    def is_valid_pose(self, landmarks, frame_shape: tuple[int, int, int]) -> tuple[bool, str]:
        """Reject frames that are badly angled or poorly aligned before counting reps."""
        if not landmarks:
            return False, "No person detected"

        required = self.get_required_landmarks()
        if any(idx >= len(landmarks) for idx in required):
            return False, "Insufficient landmarks"

        shoulder_ids = (11, 12)
        hip_ids = (23, 24)

        try:
            shoulder_points = [get_landmark_coords(landmarks, idx, frame_shape) for idx in shoulder_ids]
            hip_points = [get_landmark_coords(landmarks, idx, frame_shape) for idx in hip_ids]
        except Exception:
            return False, "Insufficient landmarks"

        shoulder_center = (
            sum(p[0] for p in shoulder_points) / len(shoulder_points),
            sum(p[1] for p in shoulder_points) / len(shoulder_points),
        )
        hip_center = (
            sum(p[0] for p in hip_points) / len(hip_points),
            sum(p[1] for p in hip_points) / len(hip_points),
        )

        shoulder_span = abs(shoulder_points[0][0] - shoulder_points[1][0])
        hip_span = abs(hip_points[0][0] - hip_points[1][0])
        if shoulder_span < 25 or hip_span < 25:
            return False, "Keep your shoulders and hips visible"

        if self.requires_side_view():
            torso_x_offset = abs(shoulder_center[0] - hip_center[0])
            if torso_x_offset > frame_shape[1] * 0.18:
                return False, "Turn your body to the side for this exercise"
            if shoulder_span > frame_shape[1] * 0.40 or hip_span > frame_shape[1] * 0.40:
                return False, "Turn your body to the side for this exercise"
        else:
            torso_x_offset = abs(shoulder_center[0] - hip_center[0])
            if torso_x_offset > frame_shape[1] * 0.22:
                return False, "Keep your torso centered in the camera"

        torso_drop = abs(shoulder_center[1] - hip_center[1])
        if torso_drop > frame_shape[0] * 0.30:
            return False, "Keep your torso upright"

        return True, ""

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
