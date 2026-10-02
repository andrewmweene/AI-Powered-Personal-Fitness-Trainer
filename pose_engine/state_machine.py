"""Exercise state machine for rep detection and posture phase tracking."""

from __future__ import annotations

import time


class ExerciseStateMachine:
    """Tracks exercise phases and counts reps in a structured sequence."""

    STATE_REST = "REST"
    STATE_TRANSITION = "TRANSITION"
    STATE_COMPLETE = "COMPLETE"
    REST = STATE_REST
    TRANSITION = STATE_TRANSITION
    COMPLETE = STATE_COMPLETE
    VALID_CYCLE = ["s1", "s2", "s3", "s2", "s1"]

    def __init__(self) -> None:
        self.current_state = self.STATE_REST
        self.correct_count = 0
        self.incorrect_count = 0
        self.last_activity_time = time.time()
        self.inactive_threshold = 10.0
        self._sequence = ["s1"]

    def update(self, angle: float, thresholds: dict[str, float]) -> tuple[str, bool]:
        """Update the current exercise phase and determine rep completion."""
        now = time.time()
        rep_completed = False

        if now - self.last_activity_time > self.inactive_threshold:
            self.reset()
            return self.STATE_REST, False

        new_state = self._state_from_angle(angle, thresholds)
        previous_state = self.current_state

        if new_state == previous_state:
            self.last_activity_time = now
            return self.current_state, False

        self.current_state = new_state
        state_codes = {
            self.STATE_REST: "s1",
            self.STATE_TRANSITION: "s2",
            self.STATE_COMPLETE: "s3",
        }
        self._sequence.append(state_codes[new_state])
        if len(self._sequence) > 10:
            self._sequence = self._sequence[-10:]

        if new_state == self.STATE_REST:
            valid_cycle = len(self._sequence) >= 5 and self._sequence[-5:] == self.VALID_CYCLE
            if valid_cycle:
                self.correct_count += 1
                rep_completed = True
            elif len(self._sequence) > 2:
                self.incorrect_count += 1
            self._sequence = ["s1"]

        self.last_activity_time = now
        return self.current_state, rep_completed

    def reset(self) -> None:
        self.current_state = self.STATE_REST
        self.last_activity_time = time.time()
        self._sequence = ["s1"]

    def _state_from_angle(self, angle: float, thresholds: dict[str, float]) -> str:
        if {"rest", "transition", "complete"}.issubset(thresholds):
            if angle >= thresholds["rest"]:
                return self.STATE_REST
            if angle <= thresholds["complete"]:
                return self.STATE_COMPLETE
            return self.STATE_TRANSITION

        rest_min = thresholds["rest_min"]
        rest_max = thresholds["rest_max"]
        transition_min = thresholds["transition_min"]
        transition_max = thresholds["transition_max"]
        complete_min = thresholds["complete_min"]
        complete_max = thresholds["complete_max"]

        if rest_min <= angle <= rest_max:
            return self.STATE_REST
        if transition_min <= angle <= transition_max:
            return self.STATE_TRANSITION
        if complete_min <= angle <= complete_max:
            return self.STATE_COMPLETE
        return self.current_state
