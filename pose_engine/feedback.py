"""Feedback generation for exercise posture and rep quality."""

from __future__ import annotations

import cv2
import numpy as np


class FeedbackGenerator:
    """Produces guidance messages for live exercise correction."""

    def get_feedback(self, angle: float, state: str) -> str:
        """Generate a feedback message based on current angle and state.

        Args:
            angle: The current measured joint angle.
            state: The current phase state from the exercise state machine.

        Returns:
            A string message to guide the user.
        """
        if state == "REST":
            return "Start the movement slowly and keep joints aligned."
        if state == "TRANSITION":
            return "Move through the transition with control and maintain posture."
        if state == "COMPLETE":
            return "Hold the bottom position briefly and keep your core engaged."
        return "Keep breathing and focus on controlled movement."


def draw_feedback_overlay(
    frame: np.ndarray,
    rep_count: int,
    accuracy_pct: float,
    feedback_text: str,
    state: str,
) -> np.ndarray:
    """Draw feedback overlays on the captured pose frame."""
    overlay = frame.copy()
    height, width = frame.shape[:2]

    top_bar_height = 80
    bottom_bar_height = 100
    alpha = 0.6

    cv2.rectangle(overlay, (0, 0), (width, top_bar_height), (0, 0, 0), -1)
    cv2.rectangle(
        overlay,
        (0, height - bottom_bar_height),
        (width, height),
        (0, 0, 0),
        -1,
    )
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    font = cv2.FONT_HERSHEY_SIMPLEX
    white = (255, 255, 255)
    yellow = (0, 255, 255)
    cyan = (255, 255, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)

    accuracy_color = green if accuracy_pct >= 80.0 else red
    rep_text = f"Reps: {rep_count}"
    accuracy_text = f"Accuracy: {accuracy_pct:.0f}%"
    state_text = state if state in {"REST", "MOVING", "COMPLETE"} else state

    cv2.putText(frame, rep_text, (20, 45), font, 1.5, white, 3, cv2.LINE_AA)
    accuracy_size = cv2.getTextSize(accuracy_text, font, 1.5, 3)[0]
    accuracy_x = width - accuracy_size[0] - 20
    cv2.putText(frame, accuracy_text, (accuracy_x, 45), font, 1.5, accuracy_color, 3, cv2.LINE_AA)

    if feedback_text:
        feedback_size = cv2.getTextSize(feedback_text, font, 1.0, 2)[0]
        feedback_x = (width - feedback_size[0]) // 2
        feedback_y = height - 30
        cv2.putText(frame, feedback_text, (feedback_x, feedback_y), font, 1.0, yellow, 2, cv2.LINE_AA)

    state_text = state_text if state_text != "TRANSITION" else "MOVING"
    cv2.putText(frame, state_text, (20, height - 30), font, 1.0, cyan, 2, cv2.LINE_AA)

    return frame
