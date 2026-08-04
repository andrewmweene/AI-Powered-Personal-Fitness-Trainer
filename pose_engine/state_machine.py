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

    def __init__(self) -> None:
        self.current_state = self.STATE_REST
        self.correct_count = 0
        self.incorrect_count = 0
        self.last_activity_time = time.time()
        self.inactive_threshold = 10.0
        self._saw_complete = False
        self._cycle_started = False

    def update(self, angle: float, thresholds: dict[str, float]) -> tuple[str, bool]:
        """Update the current exercise phase and determine rep completion."""
        now = time.time()
        rep_completed = False

        if now - self.last_activity_time > self.inactive_threshold:
            self.reset()
            return self.STATE_REST, False

        new_state = self._state_from_angle(angle, thresholds)
        previous_state = self.current_state

        if self._is_valid_transition(previous_state, new_state):
            self.current_state = new_state
        else:
            self.incorrect_count += 1
            self.current_state = new_state

        if self._completed_rep_cycle(previous_state, self.current_state):
            self.correct_count += 1
            rep_completed = True
            self._saw_complete = False
            self._cycle_started = False

        self._update_cycle_flags(previous_state, self.current_state)

        self.last_activity_time = now
        return self.current_state, rep_completed

    def reset(self) -> None:
        self.current_state = self.STATE_REST
        self.last_activity_time = time.time()
        self._saw_complete = False
        self._cycle_started = False

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

    def _is_valid_transition(self, previous: str, current: str) -> bool:
        valid = {
            self.STATE_REST: {self.STATE_TRANSITION},
            self.STATE_TRANSITION: {self.STATE_COMPLETE, self.STATE_REST},
            self.STATE_COMPLETE: {self.STATE_TRANSITION},
        }
        return current in valid.get(previous, set())

    def _update_cycle_flags(self, previous: str, current: str) -> None:
        if previous == self.STATE_REST and current == self.STATE_TRANSITION:
            self._cycle_started = True

        if previous == self.STATE_TRANSITION and current == self.STATE_COMPLETE and self._cycle_started:
            self._saw_complete = True

        if current == self.STATE_REST and previous != self.STATE_REST:
            if not self._saw_complete:
                self._cycle_started = False
            self._saw_complete = False

    def _completed_rep_cycle(self, previous: str, current: str) -> bool:
        return (
            previous == self.STATE_TRANSITION
            and current == self.STATE_REST
            and self._cycle_started
            and self._saw_complete
        )
